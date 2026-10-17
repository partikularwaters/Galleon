#!/usr/bin/env node
// Explicit named-file byte inventories, without writes or dependencies (Node.js 22+).
// Fallback for file_inventory.py: same arguments, exit codes, and output bytes as Python 3.14, except
// for the limits listed in docs/verification.md.
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const FORMAT = "named-file-inventory";
const MAX_FILES = 256;
const MAX_BASELINE_BYTES = 4 * 1024 * 1024;
const MAX_FILE_BYTES = 64 * 1024 * 1024;
const MAX_TOTAL_BYTES = 256 * 1024 * 1024;
const CHUNK = 1024 * 1024;
const LIMITATION = "Listed file bytes only, at observation time. No extra-file scan, mode or Git " +
  "comparison, semantic review, approval, baseline authentication, or atomic snapshot.";
const FLAGS = fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0) | (fs.constants.O_NONBLOCK ?? 0);

class CheckError extends Error {}
class Missing extends CheckError {}

class UsageError extends Error {}

class HelpRequest extends Error {}

// Python 3.14 argparse rules for one parser: abbreviated options, negative-number-like and
// spaced arguments as positionals, "--", combined short flags, and when help or errors win.
// options maps each option string to [kind, dest] with kind "help", "flag", or "value";
// positional is null or { dest } for one or more values, or { dest, parser } for subcommands.
function parseCommandLine(argv, help, options, required, positional) {
  const optional = (arg) => {
    if (!arg || arg[0] !== "-") return null;
    if (Object.hasOwn(options, arg)) return [[arg, null, null]];
    if (arg.length === 1) return null;
    const eq = arg.indexOf("=");
    const head = eq >= 0 ? arg.slice(0, eq) : arg;
    const tail = eq >= 0 ? arg.slice(eq + 1) : null;
    const sep = eq >= 0 ? "=" : null;
    if (eq >= 0 && Object.hasOwn(options, head)) return [[head, tail, sep]];
    const found = [];
    for (const name of Object.keys(options)) {
      if (arg[1] !== "-" && name === arg.slice(0, 2)) found.push([name, arg.slice(2), ""]);
      else if (name.startsWith(head)) found.push([name, tail, sep]);
    }
    if (found.length) return found;
    if (/^-\.?\p{Nd}/u.test(arg) || arg.includes(" ")) return null;
    return [[null, null, null]];
  };
  const found = new Map();
  let kinds = "";
  let last = -1;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--") {
      kinds += "-" + "A".repeat(argv.length - i - 1);
      break;
    }
    const tuples = optional(argv[i]);
    if (tuples) {
      found.set(i, tuples);
      last = i;
    }
    kinds += tuples ? "O" : "A";
  }
  const values = {};
  const seen = new Set();
  const extras = [];
  let waiting = positional !== null;
  const take = (name, value) => {
    const [kind, dest] = options[name];
    if (kind === "help") throw new HelpRequest(help);
    values[dest] = kind === "flag" ? true : value;
    seen.add(name);
  };
  const consumeOptional = (start) => {
    const tuples = found.get(start);
    if (tuples.length > 1) throw new UsageError("ambiguous option: " + argv[start]);
    let [name, explicit, sep] = tuples[0];
    const taken = [];
    let stop;
    for (;;) {
      if (name === null) {
        extras.push(argv[start]);
        return start + 1;
      }
      const count = options[name][0] === "value" ? 1 : 0;
      if (explicit === null) {
        if (count && kinds[start + 1] !== "A") throw new UsageError("argument " + name + ": expected one argument");
        taken.push([name, count ? argv[start + 1] : null]);
        stop = start + 1 + count;
        break;
      }
      if (count) {
        taken.push([name, explicit]);
        stop = start + 1;
        break;
      }
      if (name[1] === "-" || explicit === "" || sep || explicit[0] === "-") {
        throw new UsageError("argument " + name + ": ignored explicit argument");
      }
      taken.push([name, null]);
      name = "-" + explicit[0];
      if (!Object.hasOwn(options, name)) {
        extras.push("-" + explicit);
        stop = start + 1;
        break;
      }
      explicit = explicit.slice(1);
      if (!explicit) explicit = sep = null;
      else if (explicit[0] === "=") [sep, explicit] = ["=", explicit.slice(1)];
      else sep = "";
    }
    for (const [option, value] of taken) take(option, value);
    return stop;
  };
  const consumePositionals = (start) => {
    if (!waiting) return start;
    const match = (positional.parser ? /^-*A[-AO]*/ : /^-*A[A-]*/).exec(kinds.slice(start));
    if (!match) return start;
    const args = argv.slice(start, start + match[0].length);
    if (positional.parser ? kinds[start] === "-" : match[0].includes("-")) args.splice(args.indexOf("--"), 1);
    waiting = false;
    if (positional.parser) {
      const sub = positional.parser(args);
      Object.assign(values, sub.values);
      extras.push(...sub.extras);
    } else {
      values[positional.dest] = args;
    }
    return start + match[0].length;
  };
  let start = 0;
  while (start <= last) {
    let next = start;
    while (next <= last && !found.has(next)) next++;
    if (start !== next) {
      const end = consumePositionals(start);
      if (end > start) {
        start = end;
        continue;
      }
    }
    if (!found.has(start)) {
      extras.push(...argv.slice(start, next));
      start = next;
    }
    start = consumeOptional(start);
  }
  extras.push(...argv.slice(consumePositionals(start)));
  const missing = required.filter((name) => !seen.has(name));
  if (waiting) missing.push(positional.dest);
  if (missing.length) throw new UsageError("the following arguments are required: " + missing.join(", "));
  return { values, extras };
}

function asciiJson(value) {
  if (typeof value === "string") {
    return JSON.stringify(value).replace(/[\u007f-￿]/g,
      (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
  }
  if (typeof value === "number" || typeof value === "bigint" || typeof value === "boolean") {
    return String(value);
  }
  if (Array.isArray(value)) return "[" + value.map(asciiJson).join(", ") + "]";
  return "{" + Object.entries(value).map(([k, v]) => asciiJson(k) + ": " + asciiJson(v)).join(", ") + "}";
}

const asciiText = (value) => asciiJson(value).slice(1, -1);

// Order by Unicode code point, matching Python's sorted(), not by UTF-16 unit.
function fold(c) {
  return c >= 0xe000 ? c - 0x800 : c >= 0xd800 ? c + 0x2000 : c;
}

function compareCodePoints(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    const x = a.charCodeAt(i);
    const y = b.charCodeAt(i);
    if (x !== y) return fold(x) - fold(y);
  }
  return a.length - b.length;
}

const LONE_SURROGATE = /[\ud800-\udbff](?![\udc00-\udfff])|(?<![\ud800-\udbff])[\udc00-\udfff]/;

function canonical(name) {
  if (typeof name !== "string" || !name || name.startsWith("/") || name.includes("\\") ||
      name.includes("\x00") || LONE_SURROGATE.test(name) || /^[A-Za-z]:/.test(name) ||
      name.split("/").some((p) => p === "" || p === "." || p === ".." || p.toLowerCase() === ".git")) {
    throw new CheckError("expected a canonical root-relative project-file path; Git internals are excluded");
  }
  return name;
}

function rootPath(name) {
  try {
    const root = fs.realpathSync(name);
    if (!fs.statSync(root).isDirectory()) throw new Error("not a directory");
    return root;
  } catch {
    throw new CheckError("root must be an accessible directory");
  }
}

const signature = (i) => [i.dev, i.ino, i.mode, i.size, i.mtimeNs, i.ctimeNs].join(":");

function regular(root, name) {
  const pieces = canonical(name).split("/");
  let current = root;
  let info;
  for (let index = 0; index < pieces.length; index++) {
    current = path.join(current, pieces[index]);
    try {
      info = fs.lstatSync(current, { bigint: true });
    } catch (error) {
      if (error.code === "ENOENT") throw new Missing("listed file or parent is missing");
      throw new CheckError("listed path could not be inspected");
    }
    if (info.isSymbolicLink()) throw new CheckError("symlink or reparse traversal below root");
    if (index < pieces.length - 1 && !info.isDirectory()) throw new CheckError("non-directory parent");
  }
  if (!info.isFile()) throw new CheckError("expected a regular file");
  return [current, info];
}

function read(root, name, bound, budget, collect = false) {
  const [file, before] = regular(root, name);
  if (before.size > BigInt(bound)) throw new CheckError("file exceeds its read bound");
  if (before.size > BigInt(budget.remaining)) throw new CheckError("total reads exceed the run bound");
  const digest = crypto.createHash("sha256");
  const chunks = [];
  let count = 0;
  let fd;
  try {
    fd = fs.openSync(file, FLAGS);
    const opened = fs.fstatSync(fd, { bigint: true });
    if (!opened.isFile() || signature(opened) !== signature(before)) {
      throw new CheckError("file changed before reading");
    }
    const buffer = Buffer.allocUnsafe(CHUNK);
    for (;;) {
      const want = Math.min(CHUNK, bound - count + 1, budget.remaining + 1);
      const got = fs.readSync(fd, buffer, 0, want, null);
      if (got === 0) break;
      count += got;
      budget.remaining -= got;
      if (count > bound || budget.remaining < 0) {
        throw new CheckError("file changed or exceeded its read bound");
      }
      digest.update(buffer.subarray(0, got));
      if (collect) chunks.push(Buffer.from(buffer.subarray(0, got)));
    }
    const after = fs.fstatSync(fd, { bigint: true });
    let now;
    try {
      now = regular(root, name)[1];
    } catch {
      throw new CheckError("file path changed or became unsafe during reading");
    }
    if (BigInt(count) !== opened.size || signature(after) !== signature(opened) ||
        signature(now) !== signature(after)) {
      throw new CheckError("file changed during reading");
    }
  } catch (error) {
    if (error instanceof CheckError) throw error;
    throw new CheckError("file could not be read");
  } finally {
    if (fd !== undefined) {
      try { fs.closeSync(fd); } catch { /* already unreadable */ }
    }
  }
  return [{ path: name, size: count, sha256: digest.digest("hex") }, Buffer.concat(chunks)];
}

function capture(root, names, budget) {
  if (!names.length || names.length > MAX_FILES) throw new CheckError("select 1 to 256 named files");
  const unique = [...new Set(names.map(canonical))].sort(compareCodePoints);
  return {
    format: FORMAT,
    version: 1,
    files: unique.map((name) => read(root, name, MAX_FILE_BYTES, budget)[0]),
  };
}

// Strict JSON: unique fields, finite values, bounded integers, integers kept distinct from floats.
function parseStrictJson(text) {
  const fail = () => { throw new CheckError("baseline must be valid UTF-8 JSON with unique fields and finite values"); };
  const number = /-?(?:0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?/y;
  const simple = { '"': '"', "\\": "\\", "/": "/", b: "\b", f: "\f", n: "\n", r: "\r", t: "\t" };
  let i = 0;
  const space = () => { while (i < text.length && " \t\n\r".includes(text[i])) i++; };
  const string = () => {
    let out = "";
    i++;
    for (;;) {
      if (i >= text.length) fail();
      const c = text[i++];
      if (c === '"') return out;
      if (c < " ") fail();
      if (c !== "\\") { out += c; continue; }
      const e = text[i++];
      if (e === "u") {
        const hex = text.slice(i, i + 4);
        if (!/^[0-9a-fA-F]{4}$/.test(hex)) fail();
        out += String.fromCharCode(parseInt(hex, 16));
        i += 4;
      } else if (e !== undefined && Object.hasOwn(simple, e)) {
        out += simple[e];
      } else {
        fail();
      }
    }
  };
  const value = (depth) => {
    if (depth > 64) fail();
    space();
    const c = text[i];
    if (c === "{") {
      const out = new Map();
      i++;
      space();
      if (text[i] === "}") { i++; return out; }
      for (;;) {
        space();
        if (text[i] !== '"') fail();
        const key = string();
        if (out.has(key)) fail();
        space();
        if (text[i++] !== ":") fail();
        out.set(key, value(depth + 1));
        space();
        const next = text[i++];
        if (next === "}") return out;
        if (next !== ",") fail();
      }
    }
    if (c === "[") {
      const out = [];
      i++;
      space();
      if (text[i] === "]") { i++; return out; }
      for (;;) {
        out.push(value(depth + 1));
        space();
        const next = text[i++];
        if (next === "]") return out;
        if (next !== ",") fail();
      }
    }
    if (c === '"') return string();
    for (const [word, result] of [["true", true], ["false", false], ["null", null]]) {
      if (text.startsWith(word, i)) { i += word.length; return result; }
    }
    number.lastIndex = i;
    const m = number.exec(text);
    if (!m) fail();
    i += m[0].length;
    if (m[1] === undefined && m[2] === undefined) {
      if (m[0].length > 20) fail();
      return BigInt(m[0]);
    }
    const parsed = Number(m[0]);
    if (!Number.isFinite(parsed)) fail();
    return parsed;
  };
  const result = value(0);
  space();
  if (i !== text.length) fail();
  return result;
}

function loadBaseline(root, name, budget) {
  const raw = read(root, name, MAX_BASELINE_BYTES, budget, true)[1];
  let data;
  try {
    data = parseStrictJson(new TextDecoder("utf-8", { fatal: true }).decode(raw));
  } catch (error) {
    if (error instanceof CheckError) throw error;
    throw new CheckError("baseline must be valid UTF-8 JSON with unique fields and finite values");
  }
  const files = data instanceof Map ? data.get("files") : undefined;
  if (!(data instanceof Map) || data.size !== 3 || data.get("format") !== FORMAT ||
      data.get("version") !== 1n || !Array.isArray(files) || files.length < 1 || files.length > MAX_FILES) {
    throw new CheckError("unsupported or empty inventory format");
  }
  const seen = new Set();
  let total = 0;
  const entries = [];
  for (const item of files) {
    if (!(item instanceof Map) || item.size !== 3 || !item.has("path") || !item.has("size") ||
        !item.has("sha256")) {
      throw new CheckError("invalid inventory entry");
    }
    const entry = { path: canonical(item.get("path")), size: item.get("size"), sha256: item.get("sha256") };
    if (seen.has(entry.path)) throw new CheckError("duplicate inventory path");
    if (typeof entry.size !== "bigint" || entry.size < 0n || entry.size > BigInt(MAX_FILE_BYTES)) {
      throw new CheckError("invalid inventory size");
    }
    if (typeof entry.sha256 !== "string" || !/^[0-9a-f]{64}$/.test(entry.sha256)) {
      throw new CheckError("invalid SHA-256 digest");
    }
    total += Number(entry.size);
    if (total > MAX_TOTAL_BYTES) throw new CheckError("inventory exceeds the total read bound");
    seen.add(entry.path);
    entries.push({ path: entry.path, size: Number(entry.size), sha256: entry.sha256 });
  }
  return entries.sort((a, b) => compareCodePoints(a.path, b.path));
}

function compare(root, entries, budget) {
  const report = { method: "named-file-compare-v1", complete: true, checked: 0,
    changed: [], missing: [], unsafe: [], limitation: LIMITATION };
  for (const want of entries) {
    let actual;
    try {
      actual = read(root, want.path, MAX_FILE_BYTES, budget)[0];
    } catch (error) {
      if (error instanceof Missing) { report.missing.push(want.path); continue; }
      if (error instanceof CheckError) {
        report.complete = false;
        report.unsafe.push({ path: want.path, reason: error.message });
        continue;
      }
      throw error;
    }
    report.checked += 1;
    if (actual.size !== want.size || actual.sha256 !== want.sha256) report.changed.push(want.path);
  }
  return report;
}

const USAGE = "usage: file_inventory.mjs [-h] {capture,compare} ...";
const HELP = USAGE + `

Capture or compare explicit file bytes without writing.

positional arguments:
  {capture,compare}
    capture          print a baseline for explicitly named files
    compare          compare exactly the baseline's named files

options:
  -h, --help         show this help message and exit
`;
const CAPTURE_HELP = `usage: file_inventory.mjs capture [-h] --root ROOT [--json] files [files ...]

positional arguments:
  files        canonical root-relative paths

options:
  -h, --help   show this help message and exit
  --root ROOT  selected project boundary
  --json       ASCII-safe machine-readable output
`;
const COMPARE_HELP = `usage: file_inventory.mjs compare [-h] --root ROOT [--json] --baseline BASELINE

options:
  -h, --help           show this help message and exit
  --root ROOT          selected project boundary
  --json               ASCII-safe machine-readable output
  --baseline BASELINE  root-relative inventory JSON path
`;

function parseSubcommand(args) {
  const [command, ...rest] = args;
  const options = { "-h": ["help"], "--help": ["help"], "--root": ["value", "root"], "--json": ["flag", "json"] };
  let parsed;
  if (command === "capture") {
    parsed = parseCommandLine(rest, CAPTURE_HELP, options, ["--root"], { dest: "files" });
  } else if (command === "compare") {
    options["--baseline"] = ["value", "baseline"];
    parsed = parseCommandLine(rest, COMPARE_HELP, options, ["--root", "--baseline"], null);
  } else {
    throw new UsageError("argument command: invalid choice: " + command);
  }
  return { values: { command, ...parsed.values }, extras: parsed.extras };
}

function parseArguments(argv) {
  const parsed = parseCommandLine(argv, HELP, { "-h": ["help"], "--help": ["help"] }, [],
    { dest: "command", parser: parseSubcommand });
  if (parsed.extras.length) throw new UsageError("unrecognized arguments: " + parsed.extras.join(" "));
  return { json: false, files: [], ...parsed.values };
}

// Node.js decodes invalid UTF-8 arguments to U+FFFD, losing the bytes Python would keep.
function lossyArgument(argv) {
  return argv.some((arg) => arg.includes("\ufffd"));
}

// Python's text streams translate newlines on Windows, including help and errors.
function writeOutput(stream, text) {
  stream.write(process.platform === "win32" ? text.replace(/\n/g, "\r\n") : text);
}

function main(argv) {
  let args;
  try {
    args = parseArguments(argv);
  } catch (error) {
    if (error instanceof HelpRequest) {
      writeOutput(process.stdout, error.message);
      return 0;
    }
    if (!(error instanceof UsageError)) throw error;
    writeOutput(process.stderr, USAGE + "\nerror: " + asciiText(error.message) + "\n");
    return 2;
  }
  if (lossyArgument(argv)) {
    writeOutput(process.stderr, "ERROR: an argument is not valid UTF-8 or contains U+FFFD; use file_inventory.py\n");
    return 2;
  }
  let result;
  try {
    const root = rootPath(args.root);
    const budget = { remaining: MAX_TOTAL_BYTES };
    result = args.command === "capture"
      ? capture(root, args.files, budget)
      : compare(root, loadBaseline(root, args.baseline, budget), budget);
  } catch (error) {
    if (!(error instanceof CheckError)) throw error;
    writeOutput(process.stderr, "INCOMPLETE: " + asciiText(error.message) + "\n");
    return 2;
  }
  const lines = [];
  if (args.json) {
    lines.push(asciiJson(result));
  } else if (args.command === "capture") {
    lines.push(`Captured ${result.files.length} named files; use --json for a reusable baseline.`);
    for (const item of result.files) {
      lines.push(`${asciiText(item.path)}: ${item.size} bytes; SHA-256 ${item.sha256}`);
    }
    lines.push(LIMITATION);
  } else {
    lines.push(`${result.complete ? "COMPLETE" : "INCOMPLETE"}: ${result.checked} files hashed; ` +
      `${result.changed.length} changed; ${result.missing.length} missing; ` +
      `${result.unsafe.length} unsafe or unreadable.`);
    for (const kind of ["changed", "missing", "unsafe"]) {
      for (const item of result[kind]) lines.push(kind + ": " + asciiJson(item));
    }
    lines.push(LIMITATION);
  }
  writeOutput(process.stdout, lines.join("\n") + "\n");
  if (args.command === "capture") return 0;
  return !result.complete ? 2 : result.changed.length || result.missing.length ? 1 : 0;
}

process.exitCode = main(process.argv.slice(2));
