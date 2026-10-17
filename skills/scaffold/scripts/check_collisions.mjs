#!/usr/bin/env node
// Read-only portable sibling-name preview, without adoption or writes (Node.js 22+).
// Fallback for check_collisions.py: same arguments, exit codes, and output bytes as Python 3.14, except
// for the limits listed in docs/verification.md.
import fs from "node:fs";
import path from "node:path";

const MAX_NAMES = 256;
const MAX_SIBLINGS = 4096;
const POLICY = "Unicode NFC, then case folding; conservative portable sibling-name policy";
const LIMITATION = "Preview only: names are not reserved. Not a filesystem emulator, ownership " +
  "check, installer, or permission to create or replace anything.";
const RESERVED = new Set(["con", "prn", "aux", "nul", "conin$", "conout$"]);
for (const prefix of ["com", "lpt"]) {
  for (const digit of [..."123456789¹²³"]) RESERVED.add(prefix + digit);
}
const LONE_SURROGATE = /[\ud800-\udbff](?![\udc00-\udfff])|(?<![\ud800-\udbff])[\udc00-\udfff]/;
const WINDOWS = process.platform === "win32";

class CheckError extends Error {}

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
  if (value === null) return "null";
  if (typeof value === "string") {
    return JSON.stringify(value).replace(/[\u007f-￿]/g,
      (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
  }
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (Array.isArray(value)) return "[" + value.map(asciiJson).join(", ") + "]";
  return "{" + Object.entries(value).map(([k, v]) => asciiJson(k) + ": " + asciiJson(v)).join(", ") + "}";
}

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

// Python's NFC-then-casefold, per code point. Lower, upper, lower reproduces full case folding
// (for example ß and ẞ both become ss); dotless ı stays distinct from i, as in Python, and
// Cherokee folds to its uppercase letters, as in Python.
function key(name) {
  return [...name.normalize("NFC")]
    .map((ch) => (ch === "ı" ? ch : ch.toLowerCase().toUpperCase().toLowerCase()))
    .join("")
    .replace(/[\u13f8-\u13fd\uab70-\uabbf]/g, (ch) => ch.toUpperCase());
}

// Python's os.fsdecode on POSIX: UTF-8, with each undecodable byte kept as U+DC80 to U+DCFF.
function fsDecode(bytes) {
  let out = "";
  let i = 0;
  while (i < bytes.length) {
    const b = bytes[i];
    const size = b < 0x80 ? 1 : b >= 0xc2 && b <= 0xdf ? 2 : b >= 0xe0 && b <= 0xef ? 3 : b >= 0xf0 && b <= 0xf4 ? 4 : 0;
    const low = b === 0xe0 ? 0xa0 : b === 0xf0 ? 0x90 : 0x80;
    const high = b === 0xed ? 0x9f : b === 0xf4 ? 0x8f : 0xbf;
    let valid = size > 0 && i + size <= bytes.length;
    for (let k = 1; valid && k < size; k++) {
      valid = bytes[i + k] >= (k === 1 ? low : 0x80) && bytes[i + k] <= (k === 1 ? high : 0xbf);
    }
    if (valid) {
      out += bytes.subarray(i, i + size).toString("utf8");
      i += size;
    } else {
      out += String.fromCharCode(0xdc00 + b);
      i += 1;
    }
  }
  return out;
}

function invalid(name) {
  if (typeof name !== "string" || !name || name === "." || name === "..") {
    return "expected a nonempty simple sibling name";
  }
  if (/[\x00-\x1f<>:"/\\|?*]/.test(name) || LONE_SURROGATE.test(name)) {
    return "path separators, control characters, surrogate characters, and portable reserved punctuation are invalid";
  }
  if (name.endsWith(" ") || name.endsWith(".")) return "trailing spaces or dots are invalid in portable mode";
  const stem = key(name).split(".")[0].replace(/[ .]+$/, "");
  if (RESERVED.has(stem)) return "reserved Windows device name in portable mode";
  return null;
}

const signature = (i) => (i === null ? null : [i.dev, i.ino, i.mode, i.size, i.mtimeNs, i.ctimeNs].join(":"));

function inspectParent(name) {
  if (typeof name !== "string" || !name || name.includes("\x00") || LONE_SURROGATE.test(name)) {
    throw new CheckError("invalid parent path");
  }
  if (WINDOWS && /^[A-Za-z]:(?![\\/])/.test(name)) {
    throw new CheckError("drive-relative parent paths are unsupported");
  }
  if (name.split(WINDOWS ? /[\\/]/ : "/").includes("..")) {
    throw new CheckError("parent path must not contain '..' components");
  }
  const full = path.resolve(process.cwd(), name);
  const anchor = path.parse(full).root;
  const parts = full.slice(anchor.length).split(path.sep).filter(Boolean);
  let current = anchor;
  let info = null;
  for (const part of [null, ...parts]) {
    if (part !== null) current = path.join(current, part);
    try {
      info = fs.lstatSync(current, { bigint: true });
    } catch (error) {
      if (error.code === "ENOENT") { info = null; continue; }
      throw new CheckError("parent ancestry could not be inspected");
    }
    if (info.isSymbolicLink()) throw new CheckError("symlink or reparse boundary in parent ancestry");
    if (!info.isDirectory()) throw new CheckError("parent or ancestor is not a directory");
  }
  return [full, info];
}

function siblings(parentName) {
  const [full, before] = inspectParent(parentName);
  const names = [];
  if (before !== null) {
    let directory;
    try {
      directory = fs.opendirSync(full, { encoding: "buffer" });
      for (let entry = directory.readSync(); entry !== null; entry = directory.readSync()) {
        if (names.length >= MAX_SIBLINGS) throw new CheckError("parent exceeds the 4,096 sibling bound");
        names.push(WINDOWS ? entry.name.toString("utf8") : fsDecode(entry.name));
      }
    } catch (error) {
      if (error instanceof CheckError) throw error;
      throw new CheckError("parent listing could not be read");
    } finally {
      try { directory?.closeSync(); } catch { /* already closed */ }
    }
  }
  const after = inspectParent(parentName)[1];
  if ((before === null) !== (after === null) || signature(before) !== signature(after)) {
    throw new CheckError("parent changed during inspection");
  }
  return [before !== null, names.sort(compareCodePoints)];
}

function check(parent, proposed) {
  const report = { method: "sibling-name-preview-v1", complete: true, policy: POLICY,
    parent_exists: null, proposed_count: proposed.length, siblings_checked: 0, occupied: [],
    duplicates: [], invalid: [], errors: [], limitation: LIMITATION };
  if (!proposed.length || proposed.length > MAX_NAMES) {
    report.complete = false;
    report.errors.push("select 1 to 256 sibling names");
    return report;
  }
  for (const name of proposed) {
    const reason = invalid(name);
    if (reason) report.invalid.push({ name, reason });
  }
  if (report.invalid.length) {
    report.complete = false;
    return report;
  }
  let present;
  let existing;
  try {
    [present, existing] = siblings(parent);
  } catch (error) {
    // Messages intentionally omit the supplied machine path.
    report.complete = false;
    report.errors.push(error instanceof CheckError ? error.message : "parent could not be inspected");
    return report;
  }
  report.parent_exists = present;
  report.siblings_checked = existing.length;
  const actual = new Map();
  const proposals = new Map();
  for (const name of existing) {
    const token = key(name);
    if (!actual.has(token)) actual.set(token, []);
    actual.get(token).push(name);
  }
  for (const name of proposed) {
    const token = key(name);
    if (!proposals.has(token)) proposals.set(token, []);
    proposals.get(token).push(name);
    for (const found of actual.get(token) ?? []) {
      report.occupied.push({ name, existing: found, kind: name === found ? "exact" : "equivalent" });
    }
  }
  for (const token of [...proposals.keys()].sort(compareCodePoints)) {
    const names = proposals.get(token);
    if (names.length > 1) {
      report.duplicates.push({ names, kind: new Set(names).size === 1 ? "exact" : "equivalent" });
    }
  }
  return report;
}

const USAGE = "usage: check_collisions.mjs [-h] --parent PARENT [--json] names [names ...]";
const HELP = USAGE + `

Preview explicit sibling names without creating anything.

positional arguments:
  names            proposed simple sibling names; no nested paths

options:
  -h, --help       show this help message and exit
  --parent PARENT  one existing or absent destination parent
  --json           ASCII-safe structured output
`;

function parseArguments(argv) {
  const parsed = parseCommandLine(argv, HELP, { "-h": ["help"], "--help": ["help"],
    "--parent": ["value", "parent"], "--json": ["flag", "json"] }, ["--parent"], { dest: "names" });
  if (parsed.extras.length) throw new UsageError("unrecognized arguments: " + parsed.extras.join(" "));
  return { json: false, ...parsed.values };
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
    writeOutput(process.stderr, USAGE + "\nerror: " + asciiJson(error.message).slice(1, -1) + "\n");
    return 2;
  }
  if (lossyArgument(argv)) {
    writeOutput(process.stderr, "ERROR: an argument is not valid UTF-8 or contains U+FFFD; use check_collisions.py\n");
    return 2;
  }
  const report = check(args.parent, args.names);
  const lines = [];
  if (args.json) {
    lines.push(asciiJson(report));
  } else {
    lines.push(`${report.complete ? "COMPLETE" : "INCOMPLETE"}: ${report.proposed_count} names proposed; ` +
      `${report.siblings_checked} siblings inspected; ${report.occupied.length} occupied; ` +
      `${report.duplicates.length} duplicate groups; ${report.invalid.length} invalid.`);
    if (report.parent_exists === false) lines.push("Parent is absent; it was not created.");
    for (const kind of ["occupied", "duplicates", "invalid", "errors"]) {
      for (const item of report[kind]) lines.push(kind + ": " + asciiJson(item));
    }
    lines.push(POLICY, LIMITATION);
  }
  writeOutput(process.stdout, lines.join("\n") + "\n");
  if (!report.complete) return 2;
  return report.occupied.length || report.duplicates.length ? 1 : 0;
}

process.exitCode = main(process.argv.slice(2));
