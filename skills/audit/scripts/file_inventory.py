#!/usr/bin/env python3
"""Explicit named-file byte inventories, without writes or dependencies (Python 3.9+)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys

FORMAT = "named-file-inventory"
MAX_FILES = 256
MAX_BASELINE_BYTES = 4 * 1024 * 1024
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
LIMITATION = ("Listed file bytes only, at observation time. No extra-file scan, mode or Git "
              "comparison, semantic review, approval, baseline authentication, or atomic snapshot.")


class CheckError(ValueError):
    pass


class Missing(CheckError):
    pass


def canonical(name):
    if (not isinstance(name, str) or not name or name.startswith("/") or "\\" in name
            or "\x00" in name or re.search(r"[\ud800-\udfff]", name) or re.match(r"^[A-Za-z]:", name)
            or any(p in ("", ".", "..") or p.casefold() == ".git" for p in name.split("/"))):
        raise CheckError("expected a canonical root-relative project-file path; Git internals are excluded")
    return name


def root_path(name):
    try:
        root = Path(name).resolve(strict=True)
        if not root.is_dir():
            raise CheckError("root must be an accessible directory")
        return root
    except (OSError, ValueError, RuntimeError):
        raise CheckError("root must be an accessible directory")


def signature(info):
    # Windows path/handle metadata can disagree on mode and change time.
    if os.name == "nt":
        return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def regular(root, name):
    pieces = canonical(name).split("/")
    path = root
    for index, piece in enumerate(pieces):
        path = path / piece
        try:
            info = path.lstat()
        except FileNotFoundError:
            raise Missing("listed file or parent is missing")
        except OSError:
            raise CheckError("listed path could not be inspected")
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise CheckError("symlink or reparse traversal below root")
        if index < len(pieces) - 1 and not stat.S_ISDIR(info.st_mode):
            raise CheckError("non-directory parent")
    if not stat.S_ISREG(info.st_mode):
        raise CheckError("expected a regular file")
    return path, info


def read(root, name, bound, budget, collect=False):
    path, before = regular(root, name)
    if before.st_size > bound:
        raise CheckError("file exceeds its read bound")
    if before.st_size > budget["remaining"]:
        raise CheckError("total reads exceed the run bound")
    digest, chunks, count = hashlib.sha256(), [], 0
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
             getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or signature(opened) != signature(before):
                raise CheckError("file changed before reading")
            while True:
                chunk = stream.read(min(1024 * 1024, bound - count + 1, budget["remaining"] + 1))
                if not chunk:
                    break
                count += len(chunk)
                budget["remaining"] -= len(chunk)
                if count > bound or budget["remaining"] < 0:
                    raise CheckError("file changed or exceeded its read bound")
                digest.update(chunk)
                if collect:
                    chunks.append(chunk)
            after = os.fstat(stream.fileno())
        try:
            _, current = regular(root, name)
        except CheckError:
            raise CheckError("file path changed or became unsafe during reading")
        if (count != opened.st_size or signature(after) != signature(opened)
                or signature(current) != signature(after)):
            raise CheckError("file changed during reading")
    except OSError:
        raise CheckError("file could not be read")
    return {"path": name, "size": count, "sha256": digest.hexdigest()}, b"".join(chunks)


def capture(root, names, budget=None):
    if budget is None:
        budget = {"remaining": MAX_TOTAL_BYTES}
    if not names or len(names) > MAX_FILES:
        raise CheckError("select 1 to 256 named files")
    paths = sorted({canonical(name) for name in names})
    files = []
    for name in paths:
        item, _ = read(root, name, MAX_FILE_BYTES, budget)
        files.append(item)
    return {"format": FORMAT, "version": 1, "files": files}


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise CheckError("duplicate JSON field")
        out[key] = value
    return out


def invalid_constant(value):
    raise CheckError("nonfinite JSON value")


def bounded_integer(value):
    if len(value) > 20:
        raise CheckError("oversized JSON integer")
    return int(value)


def baseline(root, name, budget=None):
    if budget is None:
        budget = {"remaining": MAX_TOTAL_BYTES}
    _, raw = read(root, name, MAX_BASELINE_BYTES, budget, collect=True)
    try:
        data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object,
                          parse_constant=invalid_constant, parse_int=bounded_integer)
    except (UnicodeError, ValueError, RecursionError):
        raise CheckError("baseline must be valid UTF-8 JSON with unique fields and finite values")
    if (not isinstance(data, dict) or set(data) != {"format", "version", "files"}
            or data["format"] != FORMAT or type(data["version"]) is not int or data["version"] != 1
            or not isinstance(data["files"], list) or not 1 <= len(data["files"]) <= MAX_FILES):
        raise CheckError("unsupported or empty inventory format")
    seen, total = set(), 0
    for item in data["files"]:
        if not isinstance(item, dict) or set(item) != {"path", "size", "sha256"}:
            raise CheckError("invalid inventory entry")
        path = canonical(item["path"])
        if path in seen:
            raise CheckError("duplicate inventory path")
        if type(item["size"]) is not int or not 0 <= item["size"] <= MAX_FILE_BYTES:
            raise CheckError("invalid inventory size")
        if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise CheckError("invalid SHA-256 digest")
        total += item["size"]
        if total > MAX_TOTAL_BYTES:
            raise CheckError("inventory exceeds the total read bound")
        seen.add(path)
    return sorted(data["files"], key=lambda item: item["path"])


def compare(root, entries, budget=None):
    if budget is None:
        budget = {"remaining": MAX_TOTAL_BYTES}
    report = {"method": "named-file-compare-v1", "complete": True, "checked": 0,
              "changed": [], "missing": [], "unsafe": [], "limitation": LIMITATION}
    for want in entries:
        name = want["path"]
        try:
            actual, _ = read(root, name, MAX_FILE_BYTES, budget)
        except Missing:
            report["missing"].append(name)
            continue
        except CheckError as error:
            report["complete"] = False
            report["unsafe"].append({"path": name, "reason": str(error)})
            continue
        report["checked"] += 1
        if actual["size"] != want["size"] or actual["sha256"] != want["sha256"]:
            report["changed"].append(name)
    return report


def ascii_text(value):
    return json.dumps(value, ensure_ascii=True)[1:-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Capture or compare explicit file bytes without writing.")
    commands = parser.add_subparsers(dest="command", required=True)
    capture_parser = commands.add_parser("capture", help="print a baseline for explicitly named files")
    compare_parser = commands.add_parser("compare", help="compare exactly the baseline's named files")
    for sub in (capture_parser, compare_parser):
        sub.add_argument("--root", required=True, help="selected project boundary")
        sub.add_argument("--json", action="store_true", help="ASCII-safe machine-readable output")
    capture_parser.add_argument("files", nargs="+", help="canonical root-relative paths")
    compare_parser.add_argument("--baseline", required=True, help="root-relative inventory JSON path")
    args = parser.parse_args(argv)
    try:
        root = root_path(args.root)
        budget = {"remaining": MAX_TOTAL_BYTES}
        result = (capture(root, args.files, budget) if args.command == "capture"
                  else compare(root, baseline(root, args.baseline, budget), budget))
    except CheckError as error:
        print("INCOMPLETE: " + ascii_text(str(error)), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=True))
    elif args.command == "capture":
        print("Captured {} named files; use --json for a reusable baseline.".format(len(result["files"])))
        for item in result["files"]:
            print("{}: {} bytes; SHA-256 {}".format(ascii_text(item["path"]), item["size"], item["sha256"]))
        print(LIMITATION)
    else:
        print("{}: {} files hashed; {} changed; {} missing; {} unsafe or unreadable.".format(
            "COMPLETE" if result["complete"] else "INCOMPLETE", result["checked"],
            len(result["changed"]), len(result["missing"]), len(result["unsafe"])))
        for kind in ("changed", "missing", "unsafe"):
            for item in result[kind]:
                print(kind + ": " + json.dumps(item, ensure_ascii=True))
        print(LIMITATION)
    if args.command == "capture":
        return 0
    return 2 if not result["complete"] else (1 if result["changed"] or result["missing"] else 0)


if __name__ == "__main__":
    sys.exit(main())
