#!/usr/bin/env node
// Read-only, explicitly approximate file reading-cost report (Node.js 22+).
// Fallback for count_tokens.py: same arguments, exit codes, and output bytes as Python 3.14, except
// for the limits listed in docs/verification.md.
import fs from "node:fs";

const MAX_FILES = 32;
const MAX_BYTES = 4 * 1024 * 1024;
const METHOD = "rough-whitespace-words-v1";
const LIMIT = "Estimate only: whitespace words x 1.3, rounded up. Not a model tokenizer " +
  "count or full prompt cost; code, minified text, and languages can differ greatly.";
const FLAGS = fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0) | (fs.constants.O_NONBLOCK ?? 0);
// Python's str.split() whitespace, so word counts match count_tokens.py.
const WORD = new RegExp("[^\\t-\\r\\x1c-\\x20\\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]+", "g");

class Failure extends Error {}

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

const USAGE = "usage: count_tokens.mjs [-h] [--json] files [files ...]";
const HELP = USAGE + `

Estimate reading cost; never edit or migrate files.

positional arguments:
  files       explicit UTF-8 file paths; no directory scan

options:
  -h, --help  show this help message and exit
  --json      emit one ASCII-safe JSON report
`;

function parseArguments(argv) {
  const parsed = parseCommandLine(argv, HELP, { "-h": ["help"], "--help": ["help"], "--json": ["flag", "json"] },
    [], { dest: "files" });
  if (parsed.extras.length) throw new UsageError("unrecognized arguments: " + parsed.extras.join(" "));
  return { json: false, ...parsed.values };
}

// Node.js decodes invalid UTF-8 arguments to U+FFFD, losing the bytes Python would keep.
function lossyArgument(argv) {
  return argv.some((arg) => arg.includes("\ufffd"));
}

function asciiJson(value) {
  if (typeof value === "string") {
    return JSON.stringify(value).replace(/[\u007f-￿]/g,
      (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
  }
  if (typeof value === "number") return String(value);
  if (Array.isArray(value)) return "[" + value.map(asciiJson).join(", ") + "]";
  return "{" + Object.entries(value).map(([k, v]) => asciiJson(k) + ": " + asciiJson(v)).join(", ") + "}";
}

const asciiText = (value) => asciiJson(value).slice(1, -1);
// Match the Python reference's weaker Windows metadata check.
const signature = (i) => (process.platform === "win32"
  ? [i.dev, i.ino, i.size, i.mtimeNs]
  : [i.dev, i.ino, i.size, i.mtimeNs, i.ctimeNs]).join(":");

function measure(paths) {
  if (paths.length > MAX_FILES) throw new Failure("at most 32 named files are supported");
  const files = [];
  const seen = new Set();
  let skipped = 0;
  for (const name of paths) {
    let before;
    try {
      before = fs.lstatSync(name, { bigint: true });
    } catch {
      throw new Failure("file could not be inspected: " + name);
    }
    if (!before.isFile()) throw new Failure("expected a regular file, not a directory or symlink: " + name);
    if (before.size > BigInt(MAX_BYTES)) throw new Failure("file exceeds the 4 MiB read bound: " + name);
    const identity = before.dev + ":" + before.ino;
    if (seen.has(identity)) { skipped += 1; continue; }
    let raw;
    let fd;
    try {
      fd = fs.openSync(name, FLAGS);
      const opened = fs.fstatSync(fd, { bigint: true });
      if (!opened.isFile() || signature(opened) !== signature(before)) {
        throw new Failure("file changed before reading: " + name);
      }
      const buffer = Buffer.allocUnsafe(MAX_BYTES + 1);
      let length = 0;
      while (length <= MAX_BYTES) {
        const got = fs.readSync(fd, buffer, length, MAX_BYTES + 1 - length, null);
        if (got === 0) break;
        length += got;
      }
      const after = fs.fstatSync(fd, { bigint: true });
      if (length > MAX_BYTES || signature(after) !== signature(opened)) {
        throw new Failure("file changed or exceeded its read bound: " + name);
      }
      if (signature(fs.lstatSync(name, { bigint: true })) !== signature(after)) {
        throw new Failure("file changed during reading: " + name);
      }
      raw = buffer.subarray(0, length);
    } catch (error) {
      if (error instanceof Failure) throw error;
      throw new Failure("file could not be read: " + name);
    } finally {
      if (fd !== undefined) {
        try { fs.closeSync(fd); } catch { /* already unreadable */ }
      }
    }
    let text;
    try {
      text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
    } catch {
      throw new Failure("file is not valid UTF-8: " + name);
    }
    const words = (text.match(WORD) ?? []).length;
    files.push({ path: name, words, estimated_tokens: Math.floor((words * 13 + 9) / 10) });
    seen.add(identity);
  }
  return {
    method: METHOD,
    limitation: LIMIT,
    files,
    read_set_estimated_tokens: files.reduce((sum, item) => sum + item.estimated_tokens, 0),
    duplicate_paths_skipped: skipped,
  };
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
    writeOutput(process.stderr, "ERROR: an argument is not valid UTF-8 or contains U+FFFD; use count_tokens.py\n");
    return 2;
  }
  let report;
  try {
    report = measure(args.files);
  } catch (error) {
    if (!(error instanceof Failure)) throw error;
    writeOutput(process.stderr, "ERROR: " + asciiText(error.message) + "\n");
    return 2;
  }
  if (args.json) {
    writeOutput(process.stdout, asciiJson(report) + "\n");
  } else {
    const lines = ["Method: " + METHOD];
    for (const item of report.files) {
      lines.push(`${asciiText(item.path)}: ${item.estimated_tokens} estimated tokens (${item.words} words)`);
    }
    lines.push(`Read-set estimate: ${report.read_set_estimated_tokens} tokens; ` +
      `duplicate paths skipped: ${report.duplicate_paths_skipped}`);
    lines.push(LIMIT);
    writeOutput(process.stdout, lines.join("\n") + "\n");
  }
  return 0;
}

process.exitCode = main(process.argv.slice(2));
