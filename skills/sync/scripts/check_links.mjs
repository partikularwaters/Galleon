#!/usr/bin/env node
// Bounded local Markdown path checks, without repairs or dependencies (Node.js 22+).
// Fallback for check_links.py: same arguments, exit codes, and output bytes as Python 3.14, except
// for the limits listed in docs/verification.md. Text handling follows Python's rules
// (whitespace set, line splitting, and URL splitting).
import fs from "node:fs";
import path from "node:path";

const MAX_FILES = 256;
const MAX_DOCUMENT_BYTES = 4 * 1024 * 1024;
const MAX_TOTAL_BYTES = 256 * 1024 * 1024;
const MAX_LINKS = 4096;
const LIMITATION = "Local path existence only. Fragments, URL queries, external URLs, " +
  "descriptions, and project authority are not validated. Not a full Markdown parser.";
const FLAGS = fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW ?? 0) | (fs.constants.O_NONBLOCK ?? 0);

// Python's str.isspace() set, which differs from JavaScript's \s (no \x1c-\x1f or \x85 there).
const WS = String.raw`\t-\r\x1c-\x20\x85\xa0  -     　`;
const SPACE = new RegExp(`^[${WS}]$`);
const STRIP = new RegExp(`^[${WS}]+|[${WS}]+$`, "g");
const LINE_BREAK = String.raw`\n\r\v\f\x1c\x1d\x1e\x85  `;
const LINES = new RegExp(`[^${LINE_BREAK}]*(?:\\r\\n|[${LINE_BREAK}])|[^${LINE_BREAK}]+`, "g");
const FENCE = /^ {0,3}(`{3,}|~{3,})([^\n]*)$/;
const AUTOLINK = new RegExp(String.raw`<(?:[A-Za-z][A-Za-z0-9+.-]*:|/?(?:a|img)(?![\p{L}\p{N}_])|[^<>${WS}]+@)`, "uy");
const SPECIAL = /[`<[]/g;
const ANGLE = new RegExp(String.raw`^<([^<>\\\n]*)>(?:[${WS}]+(?:"[^"\n]*"|'[^'\n]*'))?[${WS}]*$`);
const BARE = new RegExp(String.raw`^([^${WS}()<>\\]*)(?:[${WS}]+(?:"[^"\n]*"|'[^'\n]*'))?[${WS}]*$`);

const pyStrip = (text) => text.replace(STRIP, "");

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

// Match the Python reference's weaker Windows metadata check.
const signature = (i) => (process.platform === "win32"
  ? [i.dev, i.ino, i.size, i.mtimeNs]
  : [i.dev, i.ino, i.mode, i.size, i.mtimeNs, i.ctimeNs]).join(":");

// Walk even components later removed by '..', so normalization cannot hide links.
// Returns [parts, info, problem]; parts are root-relative components.
function localPath(root, base, name) {
  if (name.includes("\x00") || name.includes("\\") || name.startsWith("/") || /^[A-Za-z]:/.test(name)) {
    return [null, null, "unsafe path spelling"];
  }
  // Check the spelling before walking, including components later removed by '..'.
  if (name.split("/").some((part) => part !== "" && part !== "." && part !== ".." &&
      (/[ .]$/.test(part) || /[<>:"|?*]/.test(part)))) {
    return [null, null, "unsafe path spelling"];
  }
  if (base.length) {
    const [, parentInfo, parentProblem] = localPath(root, [], base.join("/"));
    if (parentProblem || !parentInfo.isDirectory()) {
      return [null, null, "source parent is missing, unsafe, or unreadable"];
    }
  }
  const parts = [...base];
  for (const part of name.split("/")) {
    if (part === "" || part === ".") continue;
    if (part === "..") {
      if (!parts.length) return [null, null, "path escapes selected root"];
      parts.pop();
    } else {
      parts.push(part);
    }
    // Python's Windows lstat rejects control characters; Node.js reports ENOENT.
    if (process.platform === "win32" && /[\x01-\x1f]/.test(part)) {
      return [null, null, "path could not be inspected"];
    }
    let info;
    try {
      info = fs.lstatSync(path.join(root, ...parts), { bigint: true });
    } catch (error) {
      if (error.code === "ENOENT") continue;
      return [null, null, "path could not be inspected"];
    }
    if (info.isSymbolicLink()) return [null, null, "symlink or reparse traversal below root"];
  }
  let info;
  try {
    info = fs.lstatSync(path.join(root, ...parts), { bigint: true });
  } catch (error) {
    return error.code === "ENOENT" ? [parts, null, "missing"] : [parts, null, "path could not be inspected"];
  }
  if (info.isSymbolicLink()) return [parts, null, "symlink or reparse target"];
  if (!info.isFile() && !info.isDirectory()) return [parts, null, "nonregular target"];
  return [parts, info, null];
}

function readDocument(root, parts, before) {
  if (!before.isFile()) throw new Failure("expected a regular Markdown input");
  if (before.size > BigInt(MAX_DOCUMENT_BYTES)) throw new Failure("document exceeds the 4 MiB read bound");
  let fd;
  let raw;
  try {
    fd = fs.openSync(path.join(root, ...parts), FLAGS);
    const opened = fs.fstatSync(fd, { bigint: true });
    if (!opened.isFile() || signature(opened) !== signature(before)) {
      throw new Failure("document changed before reading");
    }
    const buffer = Buffer.allocUnsafe(MAX_DOCUMENT_BYTES + 1);
    let length = 0;
    while (length <= MAX_DOCUMENT_BYTES) {
      const got = fs.readSync(fd, buffer, length, MAX_DOCUMENT_BYTES + 1 - length, null);
      if (got === 0) break;
      length += got;
    }
    raw = buffer.subarray(0, length);
    const after = fs.fstatSync(fd, { bigint: true });
    const [, current, problem] = localPath(root, [], parts.join("/"));
    if (problem || length > MAX_DOCUMENT_BYTES || signature(after) !== signature(opened) ||
        signature(current) !== signature(after)) {
      throw new Failure("document changed or exceeded its read bound");
    }
  } catch (error) {
    if (error instanceof Failure) throw error;
    throw new Failure("document could not be read");
  } finally {
    if (fd !== undefined) {
      try { fs.closeSync(fd); } catch { /* already unreadable */ }
    }
  }
  try {
    return [new TextDecoder("utf-8", { fatal: true }).decode(raw), raw.length];
  } catch {
    throw new Failure("document is not valid UTF-8");
  }
}

// Python's str.splitlines(keepends=True).
function splitLines(text) {
  return text.match(LINES) ?? [];
}

// Preserve offsets while excluding fenced blocks.
function maskCode(text) {
  let fence = null;
  const out = [];
  for (const line of splitLines(text)) {
    const match = FENCE.exec(line.replace(/[\r\n]+$/, ""));
    let hidden = fence !== null;
    if (fence !== null) {
      if (match && match[1][0] === fence[0] && match[1].length >= fence[1] && !pyStrip(match[2])) fence = null;
    } else if (match) {
      hidden = true;
      fence = [match[1][0], match[1].length];
    }
    out.push(hidden ? line.replace(/[^\n]/g, " ") : line);
  }
  return out.join("");
}

function codeEnd(text, start) {
  let end = start + 1;
  while (end < text.length && text[end] === "`") end++;
  const run = text.slice(start, end);
  let close = text.indexOf(run, end);
  while (close >= 0 && ((close > 0 && text[close - 1] === "`") ||
                        (close + run.length < text.length && text[close + run.length] === "`"))) {
    close = text.indexOf(run, close + run.length);
  }
  return close >= 0 ? close + run.length : end;
}

// Read one single-line inline destination; return [target, next offset, problem].
function destination(text, start) {
  let depth = 1;
  let quote = null;
  let angle = false;
  let i = start + 1;
  while (i < text.length && text[i] !== "\n") {
    const char = text[i];
    if (quote) {
      if (char === quote) quote = null;
    } else if (angle) {
      if (char === ">") angle = false;
    } else if (char === "<") {
      angle = true;
    } else if ((char === '"' || char === "'") && SPACE.test(text[i - 1])) {
      quote = char;
    } else if (char === "(") {
      depth++;
    } else if (char === ")") {
      depth--;
      if (depth === 0) {
        const inner = pyStrip(text.slice(start + 1, i));
        const match = (inner.startsWith("<") ? ANGLE : BARE).exec(inner);
        return match ? [match[1], i + 1, null] : [null, i + 1, "unsupported destination or title syntax"];
      }
    }
    i++;
  }
  return [null, i, "unterminated or multiline inline link"];
}

function bisectRight(values, x) {
  let low = 0;
  let high = values.length;
  while (low < high) {
    const mid = (low + high) >> 1;
    if (x < values[mid]) high = mid; else low = mid + 1;
  }
  return low;
}

function* links(text) {
  const plain = maskCode(text);
  const starts = [0];
  for (let k = plain.indexOf("\n"); k >= 0; k = plain.indexOf("\n", k + 1)) starts.push(k + 1);
  let i = 0;
  let count = 0;
  while (i < plain.length) {
    SPECIAL.lastIndex = i;
    const found = SPECIAL.exec(plain);
    if (!found) return;
    i = found.index;
    if (plain[i] === "`") {
      i = codeEnd(plain, i);
      continue;
    }
    if (plain[i] === "<") {
      AUTOLINK.lastIndex = i;
      if (AUTOLINK.test(plain)) {
        yield [bisectRight(starts, i), null, "autolinks and HTML link/image syntax are unsupported"];
        const close = plain.indexOf(">", i + 1);
        i = close >= 0 ? close + 1 : plain.length;
      } else {
        i++;
      }
      continue;
    }
    count++;
    const line = bisectRight(starts, i);
    if (count > MAX_LINKS) {
      yield [line, null, "document exceeds the 4,096 link-candidate bound"];
      return;
    }
    const close = plain.indexOf("]", i + 1);
    if (close < 0) {
      yield [line, null, "unclosed bracket construct"];
      return;
    }
    const label = plain.slice(i + 1, close);
    let end = close + 1;
    const prefix = plain.slice(starts[line - 1], i);
    if (prefix.startsWith("    ") || prefix.startsWith("\t")) {
      yield [line, null, "indented link constructs are unsupported; use fenced code for examples"];
    } else if (label.includes("[") || label.includes("\n") || label.includes("\\") || (i > 0 && plain[i - 1] === "\\")) {
      yield [line, null, "unsupported nested, multiline, or escaped label"];
    } else if (end < plain.length && plain[end] === "(") {
      const [target, next, problem] = destination(text, end);
      end = next;
      yield [line, target, problem];
    } else {
      yield [line, null, "reference-style or standalone bracket construct is unsupported"];
    }
    i = end;
  }
}

// Python 3.14 urllib.parse.urlsplit(target).path, including its ValueError cases.
function ipv6Valid(host) {
  const zone = host.indexOf("%");
  const address = zone >= 0 ? host.slice(0, zone) : host;
  if (zone >= 0 && (zone === host.length - 1 || host.includes("%", zone + 1))) return false;
  const halves = address.split("::");
  if (halves.length > 2) return false;
  const groups = (side) => (side === "" ? [] : side.split(":"));
  const all = halves.flatMap(groups);
  let slots = all.length;
  const last = all[all.length - 1];
  if (last !== undefined && last.includes(".")) {
    if (!/^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)$/.test(last)) return false;
    slots += 1;
    all.pop();
  }
  if (!all.every((group) => /^[0-9A-Fa-f]{1,4}$/.test(group))) return false;
  return halves.length === 2 ? slots < 8 : slots === 8;
}

function urlPath(target) {
  let url = target.replace(/^[\x00-\x20]+/, "").replace(/[\t\r\n]/g, "");
  const colon = url.indexOf(":");
  if (colon > 0 && /^[A-Za-z]/.test(url[0]) && /^[A-Za-z0-9+.-]*$/.test(url.slice(0, colon))) {
    url = url.slice(colon + 1);
  }
  let netloc = "";
  if (url.startsWith("//")) {
    let delim = url.length;
    for (const c of "/?#") {
      const at = url.indexOf(c, 2);
      if (at >= 0) delim = Math.min(delim, at);
    }
    netloc = url.slice(2, delim);
    url = url.slice(delim);
    if ((netloc.includes("[") && !netloc.includes("]")) || (netloc.includes("]") && !netloc.includes("["))) {
      throw new Failure("Invalid IPv6 URL");
    }
    if (netloc.includes("[") && netloc.includes("]")) {
      const hostAndPort = netloc.slice(netloc.lastIndexOf("@") + 1);
      const open = hostAndPort.indexOf("[");
      const rest = hostAndPort.slice(open + 1);
      const closeAt = rest.indexOf("]");
      const host = rest.slice(0, closeAt);
      const port = rest.slice(closeAt + 1);
      if (open > 0 || (port && !port.startsWith(":"))) throw new Failure("Invalid IPv6 URL");
      const valid = host.startsWith("v") ? /^v[a-fA-F0-9]+\..+$/s.test(host) : host.includes(":") && ipv6Valid(host);
      if (!valid) throw new Failure("invalid bracketed host");
    }
  }
  const hash = url.indexOf("#");
  if (hash >= 0) url = url.slice(0, hash);
  const query = url.indexOf("?");
  if (query >= 0) url = url.slice(0, query);
  // Python's _checknetloc: NFKC must not introduce URL delimiters into a non-ASCII netloc.
  if (netloc && /[^\x00-\x7f]/.test(netloc)) {
    const n = netloc.replace(/[@:#?]/g, "");
    const folded = n.normalize("NFKC");
    if (n !== folded && [..."/?#@:"].some((c) => folded.includes(c))) throw new Failure("invalid netloc");
  }
  return url;
}

// urllib.parse.unquote(path, encoding="utf-8", errors="strict"): each ASCII run decodes on its own.
function unquoteStrict(text) {
  if (!text.includes("%")) return text;
  return text.split(/([\x00-\x7f]+)/).map((bit, index) => {
    if (index % 2 === 0) return bit;
    const bytes = [];
    for (let k = 0; k < bit.length; k++) {
      if (bit[k] === "%" && /^[0-9A-Fa-f]{2}$/.test(bit.slice(k + 1, k + 3))) {
        bytes.push(parseInt(bit.slice(k + 1, k + 3), 16));
        k += 2;
      } else {
        bytes.push(bit.charCodeAt(k));
      }
    }
    return new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bytes));
  }).join("");
}

function check(rootName, names) {
  const report = { method: "local-markdown-paths-v1", complete: true, files: [], checked: 0,
    skipped_external: 0, unverified_fragments: 0, unverified_queries: 0, links_found: 0,
    unsupported: 0, issues: [], limitation: LIMITATION };
  const issue = (source, line, target, kind, reason) => {
    report.issues.push({ source, line, destination: target, kind, reason });
    if (kind !== "missing") report.complete = false;
    if (kind === "unsupported") report.unsupported += 1;
  };
  if (names.length > MAX_FILES) {
    issue(null, null, null, "input", "at most 256 named documents are supported");
    return report;
  }
  let root;
  try {
    root = fs.realpathSync(rootName);
    if (!fs.statSync(root).isDirectory()) throw new Error("not a directory");
  } catch {
    issue(null, null, null, "input", "root must be an accessible directory");
    return report;
  }
  const seen = new Set();
  let total = 0;
  for (const name of names) {
    const [parts, info, problem] = localPath(root, [], name);
    if (problem) {
      const source = name.startsWith("/") || /^[A-Za-z]:/.test(name) ? null : name;
      issue(source, null, null, "input", "document: " + problem);
      continue;
    }
    const source = parts.length ? parts.join("/") : ".";
    if (seen.has(source)) continue;
    seen.add(source);
    if (total + Number(info.size) > MAX_TOTAL_BYTES) {
      issue(source, null, null, "input", "total document reads exceed 256 MiB");
      break;
    }
    let text;
    let size;
    try {
      [text, size] = readDocument(root, parts, info);
    } catch (error) {
      if (!(error instanceof Failure)) throw error;
      issue(source, null, null, "input", error.message);
      continue;
    }
    total += size;
    report.files.push(source);
    for (const [line, target, found] of links(text)) {
      if (report.links_found + report.unsupported >= MAX_LINKS) {
        issue(source, line, null, "input", "run exceeds the 4,096 link-candidate bound");
        return report;
      }
      if (found) {
        issue(source, line, null, "unsupported", found);
        continue;
      }
      report.links_found += 1;
      if (target.startsWith("//") || (/^[A-Za-z][A-Za-z0-9+.-]*:/.test(target) && !/^[A-Za-z]:/.test(target))) {
        report.skipped_external += 1;
        continue;
      }
      let decoded;
      let splitPath;
      try {
        splitPath = urlPath(target);
        if (/%(?![0-9A-Fa-f]{2})/.test(splitPath)) throw new Failure("bad percent escape");
        decoded = unquoteStrict(splitPath);
      } catch {
        issue(source, line, target, "unsupported", "invalid local URL spelling");
        continue;
      }
      if (target.includes("#")) report.unverified_fragments += 1;
      if (target.includes("?")) report.unverified_queries += 1;
      if (!splitPath && (target.includes("#") || target.includes("?"))) continue;
      const base = parts.slice(0, -1);
      const targetPath = decoded || parts[parts.length - 1];
      const [, , targetProblem] = localPath(root, base, targetPath);
      if (targetProblem && targetProblem !== "missing") {
        issue(source, line, target, "unsafe", targetProblem);
      } else {
        report.checked += 1;
        if (targetProblem) issue(source, line, target, "missing", "local target is missing");
      }
    }
  }
  return report;
}

const USAGE = "usage: check_links.mjs [-h] --root ROOT [--json] files [files ...]";
const HELP = USAGE + `

Check explicit Markdown local paths without repairs.

positional arguments:
  files        root-relative UTF-8 Markdown files; no repository scan

options:
  -h, --help   show this help message and exit
  --root ROOT  selected project boundary
  --json       ASCII-safe structured output
`;

function parseArguments(argv) {
  const parsed = parseCommandLine(argv, HELP, { "-h": ["help"], "--help": ["help"],
    "--root": ["value", "root"], "--json": ["flag", "json"] }, ["--root"], { dest: "files" });
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
    writeOutput(process.stderr, "ERROR: an argument is not valid UTF-8 or contains U+FFFD; use check_links.py\n");
    return 2;
  }
  const report = check(args.root, args.files);
  const lines = [];
  if (args.json) {
    lines.push(asciiJson(report));
  } else {
    lines.push(`${report.complete ? "COMPLETE" : "INCOMPLETE"}: ${report.checked} local paths checked; ` +
      `${report.skipped_external} external URLs skipped; ${report.unverified_fragments} fragments unverified; ` +
      `${report.unsupported} unsupported.`);
    for (const item of report.issues) lines.push(asciiJson(item));
    if (report.checked === 0) lines.push("No local path targets were checked; this is not a navigation audit.");
    lines.push(LIMITATION);
  }
  writeOutput(process.stdout, lines.join("\n") + "\n");
  if (!report.complete) return 2;
  return report.issues.length ? 1 : 0;
}

process.exitCode = main(process.argv.slice(2));
