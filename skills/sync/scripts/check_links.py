#!/usr/bin/env python3
"""Bounded local Markdown path checks, without repairs or dependencies (Python 3.9+)."""
import argparse
from bisect import bisect_right
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

MAX_FILES = 256
MAX_DOCUMENT_BYTES = 4 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_LINKS = 4096
LIMITATION = ("Local path existence only. Fragments, URL queries, external URLs, "
              "descriptions, and project authority are not validated. Not a full Markdown parser.")


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def local_path(root, base, name):
    """Walk even components later removed by '..', so normalization cannot hide links."""
    if "\x00" in name or "\\" in name or name.startswith("/") or re.match(r"^[A-Za-z]:", name):
        return None, None, "unsafe path spelling"
    if base:
        _, parent_info, parent_problem = local_path(root, (), "/".join(base))
        if parent_problem or not stat.S_ISDIR(parent_info.st_mode):
            return None, None, "source parent is missing, unsafe, or unreadable"
    parts = list(base)
    for part in name.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None, None, "path escapes selected root"
            parts.pop()
        else:
            parts.append(part)
        current = root.joinpath(*parts)
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            return None, None, "path could not be inspected"
        if linked(info):
            return None, None, "symlink or reparse traversal below root"
    path = root.joinpath(*parts)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return path, None, "missing"
    except OSError:
        return path, None, "path could not be inspected"
    if linked(info):
        return path, None, "symlink or reparse target"
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        return path, None, "nonregular target"
    return path, info, None


def read_document(root, path, before):
    if not stat.S_ISREG(before.st_mode):
        raise ValueError("expected a regular Markdown input")
    if before.st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("document exceeds the 4 MiB read bound")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
             getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or signature(opened) != signature(before):
                raise ValueError("document changed before reading")
            raw = stream.read(MAX_DOCUMENT_BYTES + 1)
            after = os.fstat(stream.fileno())
        relative = path.relative_to(root).as_posix()
        _, current, problem = local_path(root, (), relative)
        if (problem or len(raw) > MAX_DOCUMENT_BYTES or signature(after) != signature(opened)
                or signature(current) != signature(after)):
            raise ValueError("document changed or exceeded its read bound")
        return raw.decode("utf-8-sig"), len(raw)
    except UnicodeError:
        raise ValueError("document is not valid UTF-8")
    except OSError:
        raise ValueError("document could not be read")


def mask_code(text):
    """Preserve offsets while excluding fenced blocks."""
    masked = list(text)
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        hidden = fence is not None
        if fence is not None:
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                fence = None
        elif match:
            hidden = True
            fence = (match[1][0], len(match[1]))
        if hidden:
            masked[offset:offset + len(line)] = ["\n" if c == "\n" else " " for c in line]
        offset += len(line)
    return "".join(masked)


def code_end(text, start):
    end = start + 1
    while end < len(text) and text[end] == "`":
        end += 1
    run = text[start:end]
    close = text.find(run, end)
    while close >= 0 and ((close > 0 and text[close - 1] == "`") or
                          (close + len(run) < len(text) and text[close + len(run)] == "`")):
        close = text.find(run, close + len(run))
    return close + len(run) if close >= 0 else end


def destination(text, start):
    """Read one single-line inline destination; return (target, next offset, problem)."""
    depth, quote, angle = 1, None, False
    i = start + 1
    while i < len(text) and text[i] != "\n":
        char = text[i]
        if quote:
            if char == quote:
                quote = None
        elif angle:
            if char == ">":
                angle = False
        elif char == "<":
            angle = True
        elif char in "\"'" and text[i - 1].isspace():
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                inner = text[start + 1:i].strip()
                title = r'''(?:\s+(?:"[^"\n]*"|'[^'\n]*'))?\s*'''
                pattern = (r"<([^<>\\\n]*)>" if inner.startswith("<") else r"([^\s()<>\\]*)") + title
                match = re.fullmatch(pattern, inner)
                return (match[1], i + 1, None) if match else (None, i + 1, "unsupported destination or title syntax")
        i += 1
    return None, i, "unterminated or multiline inline link"


def links(text):
    plain = mask_code(text)
    starts = [0] + [m.end() for m in re.finditer("\n", plain)]
    i, count = 0, 0
    while i < len(plain):
        if plain[i] == "`":
            i = code_end(plain, i)
            continue
        if plain[i] == "<" and re.match(r"<(?:[A-Za-z][A-Za-z0-9+.-]*:|/?(?:a|img)\b|[^<>\s]+@)", plain[i:]):
            yield bisect_right(starts, i), None, "autolinks and HTML link/image syntax are unsupported"
            close = plain.find(">", i + 1)
            i = close + 1 if close >= 0 else len(plain)
            continue
        if plain[i] != "[":
            i += 1
            continue
        count += 1
        line = bisect_right(starts, i)
        if count > MAX_LINKS:
            yield line, None, "document exceeds the 4,096 link-candidate bound"
            return
        close = plain.find("]", i + 1)
        if close < 0:
            yield line, None, "unclosed bracket construct"
            return
        label = plain[i + 1:close]
        end = close + 1
        line_start = starts[line - 1]
        if plain[line_start:i].startswith(("    ", "\t")):
            yield line, None, "indented link constructs are unsupported; use fenced code for examples"
        elif "[" in label or "\n" in label or "\\" in label or (i > 0 and plain[i - 1] == "\\"):
            yield line, None, "unsupported nested, multiline, or escaped label"
        elif end < len(plain) and plain[end] == "(":
            target, end, problem = destination(text, end)
            yield line, target, problem
        else:
            yield line, None, "reference-style or standalone bracket construct is unsupported"
        i = end


def check(root_name, names):
    report = {"method": "local-markdown-paths-v1", "complete": True, "files": [],
              "checked": 0, "skipped_external": 0, "unverified_fragments": 0,
              "unverified_queries": 0, "links_found": 0, "unsupported": 0,
              "issues": [], "limitation": LIMITATION}

    def issue(source, line, target, kind, reason):
        report["issues"].append({"source": source, "line": line, "destination": target,
                                 "kind": kind, "reason": reason})
        if kind != "missing":
            report["complete"] = False
        if kind == "unsupported":
            report["unsupported"] += 1

    if len(names) > MAX_FILES:
        issue(None, None, None, "input", "at most 256 named documents are supported")
        return report
    try:
        root = Path(root_name).resolve(strict=True)
        if not root.is_dir():
            raise ValueError()
    except (OSError, ValueError, RuntimeError):
        issue(None, None, None, "input", "root must be an accessible directory")
        return report
    seen, total = set(), 0
    for name in names:
        path, info, problem = local_path(root, (), name)
        if problem:
            source = None if name.startswith("/") or re.match(r"^[A-Za-z]:", name) else name
            issue(source, None, None, "input", "document: " + problem)
            continue
        source = path.relative_to(root).as_posix()
        if source in seen:
            continue
        seen.add(source)
        if total + info.st_size > MAX_TOTAL_BYTES:
            issue(source, None, None, "input", "total document reads exceed 256 MiB")
            break
        try:
            text, size = read_document(root, path, info)
        except ValueError as error:
            issue(source, None, None, "input", str(error))
            continue
        total += size
        report["files"].append(source)
        for line, target, problem in links(text):
            if report["links_found"] + report["unsupported"] >= MAX_LINKS:
                issue(source, line, None, "input", "run exceeds the 4,096 link-candidate bound")
                return report
            if problem:
                issue(source, line, None, "unsupported", problem)
                continue
            report["links_found"] += 1
            if target.startswith("//") or (re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
                                            and not re.match(r"^[A-Za-z]:", target)):
                report["skipped_external"] += 1
                continue
            try:
                split = urlsplit(target)
                if re.search(r"%(?![0-9A-Fa-f]{2})", split.path):
                    raise ValueError()
                decoded = unquote(split.path, encoding="utf-8", errors="strict")
            except (ValueError, UnicodeError):
                issue(source, line, target, "unsupported", "invalid local URL spelling")
                continue
            if "#" in target:
                report["unverified_fragments"] += 1
            if "?" in target:
                report["unverified_queries"] += 1
            if not split.path and ("#" in target or "?" in target):
                continue
            base = path.parent.relative_to(root).parts
            target_path = decoded if decoded else path.name
            _, _, problem = local_path(root, base, target_path)
            if problem and problem != "missing":
                issue(source, line, target, "unsafe", problem)
            else:
                report["checked"] += 1
                if problem:
                    issue(source, line, target, "missing", "local target is missing")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check explicit Markdown local paths without repairs.")
    parser.add_argument("--root", required=True, help="selected project boundary")
    parser.add_argument("--json", action="store_true", help="ASCII-safe structured output")
    parser.add_argument("files", nargs="+", help="root-relative UTF-8 Markdown files; no repository scan")
    args = parser.parse_args(argv)
    report = check(args.root, args.files)
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print("{}: {} local paths checked; {} external URLs skipped; {} fragments unverified; {} unsupported.".format(
            "COMPLETE" if report["complete"] else "INCOMPLETE", report["checked"],
            report["skipped_external"], report["unverified_fragments"], report["unsupported"]))
        for item in report["issues"]:
            print(json.dumps(item, ensure_ascii=True))
        if report["checked"] == 0:
            print("No local path targets were checked; this is not a navigation audit.")
        print(LIMITATION)
    return 2 if not report["complete"] else (1 if report["issues"] else 0)


if __name__ == "__main__":
    sys.exit(main())
