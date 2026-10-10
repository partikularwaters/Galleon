#!/usr/bin/env python3
"""Read-only, explicitly approximate file reading-cost report (Python 3.9+)."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys

MAX_FILES = 32
MAX_BYTES = 4 * 1024 * 1024
METHOD = "rough-whitespace-words-v1"
LIMIT = ("Estimate only: whitespace words x 1.3, rounded up. Not a model tokenizer "
         "count or full prompt cost; code, minified text, and languages can differ greatly.")


def measure(paths):
    if len(paths) > MAX_FILES:
        raise ValueError("at most 32 named files are supported")
    files, seen, skipped = [], set(), 0
    for name in paths:
        path = Path(name)
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise ValueError("expected a regular file, not a directory or symlink: " + name)
        if before.st_size > MAX_BYTES:
            raise ValueError("file exceeds the 4 MiB read bound: " + name)
        identity = (before.st_dev, before.st_ino)
        if identity in seen:
            skipped += 1
            continue
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
                 getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or signature(opened) != signature(before):
                raise ValueError("file changed before reading: " + name)
            raw = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
        if len(raw) > MAX_BYTES or signature(after) != signature(opened):
            raise ValueError("file changed or exceeded its read bound: " + name)
        current = path.lstat()
        if signature(current) != signature(after):
            raise ValueError("file changed during reading: " + name)
        words = len(raw.decode("utf-8-sig").split())
        files.append({"path": name, "words": words, "estimated_tokens": (words * 13 + 9) // 10})
        seen.add(identity)
    return {"method": METHOD, "limitation": LIMIT, "files": files,
            "read_set_estimated_tokens": sum(item["estimated_tokens"] for item in files),
            "duplicate_paths_skipped": skipped}


def signature(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns


def ascii_text(value):
    return json.dumps(value, ensure_ascii=True)[1:-1]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Estimate reading cost; never edit or migrate files.")
    parser.add_argument("--json", action="store_true", help="emit one ASCII-safe JSON report")
    parser.add_argument("files", nargs="+", help="explicit UTF-8 file paths; no directory scan")
    args = parser.parse_args(argv)
    try:
        report = measure(args.files)
    except (OSError, ValueError, UnicodeError) as error:
        print("ERROR: " + ascii_text(str(error)), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print("Method: " + METHOD)
        for item in report["files"]:
            print("{}: {} estimated tokens ({} words)".format(
                ascii_text(item["path"]), item["estimated_tokens"], item["words"]))
        print("Read-set estimate: {} tokens; duplicate paths skipped: {}".format(
            report["read_set_estimated_tokens"], report["duplicate_paths_skipped"]))
        print(LIMIT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
