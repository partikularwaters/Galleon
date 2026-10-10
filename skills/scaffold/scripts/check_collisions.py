#!/usr/bin/env python3
"""Read-only portable sibling-name preview, without adoption or writes (Python 3.9+)."""
import argparse
import json
import os
from pathlib import Path
import stat
import sys
import unicodedata

MAX_NAMES = 256
MAX_SIBLINGS = 4096
POLICY = "Unicode NFC, then case folding; conservative portable sibling-name policy"
LIMITATION = ("Preview only: names are not reserved. Not a filesystem emulator, ownership "
              "check, installer, or permission to create or replace anything.")
RESERVED = {"con", "prn", "aux", "nul", "conin$", "conout$"}
RESERVED.update(prefix + digit for prefix in ("com", "lpt") for digit in "123456789¹²³")


class CheckError(ValueError):
    pass


def key(name):
    return unicodedata.normalize("NFC", name).casefold()


def invalid(name):
    if not isinstance(name, str) or not name or name in (".", ".."):
        return "expected a nonempty simple sibling name"
    if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or c in '<>:"/\\|?*' for c in name):
        return "path separators, control characters, surrogate characters, and portable reserved punctuation are invalid"
    if name.endswith((" ", ".")):
        return "trailing spaces or dots are invalid in portable mode"
    if key(name).split(".", 1)[0].rstrip(" .") in RESERVED:
        return "reserved Windows device name in portable mode"
    return None


def signature(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def inspect_parent(name):
    if not isinstance(name, str) or not name or "\x00" in name or any(0xD800 <= ord(c) <= 0xDFFF for c in name):
        raise CheckError("invalid parent path")
    given = Path(name)
    if given.drive and not given.is_absolute():
        raise CheckError("drive-relative parent paths are unsupported")
    if ".." in given.parts:
        raise CheckError("parent path must not contain '..' components")
    path = given if given.is_absolute() else Path.cwd() / given
    current = Path(path.anchor)
    info = None
    for part in (None,) + path.parts[1:]:
        if part is not None:
            current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            info = None
            continue
        except (OSError, ValueError):
            raise CheckError("parent ancestry could not be inspected")
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise CheckError("symlink or reparse boundary in parent ancestry")
        if not stat.S_ISDIR(info.st_mode):
            raise CheckError("parent or ancestor is not a directory")
    return path, info


def siblings(parent_name):
    path, before = inspect_parent(parent_name)
    names = []
    if before is not None:
        try:
            with os.scandir(path) as listing:
                for entry in listing:
                    if len(names) >= MAX_SIBLINGS:
                        raise CheckError("parent exceeds the 4,096 sibling bound")
                    names.append(entry.name)
        except OSError:
            raise CheckError("parent listing could not be read")
    _, after = inspect_parent(parent_name)
    if ((before is None) != (after is None)
            or before is not None and signature(before) != signature(after)):
        raise CheckError("parent changed during inspection")
    return before is not None, sorted(names)


def check(parent, proposed):
    report = {"method": "sibling-name-preview-v1", "complete": True,
              "policy": POLICY, "parent_exists": None, "proposed_count": len(proposed),
              "siblings_checked": 0, "occupied": [], "duplicates": [],
              "invalid": [], "errors": [], "limitation": LIMITATION}
    if not proposed or len(proposed) > MAX_NAMES:
        report["complete"] = False
        report["errors"].append("select 1 to 256 sibling names")
        return report
    for name in proposed:
        reason = invalid(name)
        if reason:
            report["invalid"].append({"name": name, "reason": reason})
    if report["invalid"]:
        report["complete"] = False
        return report
    try:
        present, existing = siblings(parent)
    except (OSError, ValueError) as error:
        # Messages intentionally omit the supplied machine path.
        reason = str(error) if isinstance(error, CheckError) else "parent could not be inspected"
        report["complete"] = False
        report["errors"].append(reason)
        return report
    report["parent_exists"] = present
    report["siblings_checked"] = len(existing)
    actual, proposals = {}, {}
    for name in existing:
        actual.setdefault(key(name), []).append(name)
    for name in proposed:
        proposals.setdefault(key(name), []).append(name)
        for found in actual.get(key(name), []):
            report["occupied"].append({"name": name, "existing": found,
                                       "kind": "exact" if name == found else "equivalent"})
    for token in sorted(proposals):
        names = proposals[token]
        if len(names) > 1:
            report["duplicates"].append({"names": names, "kind": "exact" if len(set(names)) == 1 else "equivalent"})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preview explicit sibling names without creating anything.")
    parser.add_argument("--parent", required=True, help="one existing or absent destination parent")
    parser.add_argument("--json", action="store_true", help="ASCII-safe structured output")
    parser.add_argument("names", nargs="+", help="proposed simple sibling names; no nested paths")
    args = parser.parse_args(argv)
    report = check(args.parent, args.names)
    if args.json:
        print(json.dumps(report, ensure_ascii=True))
    else:
        print("{}: {} names proposed; {} siblings inspected; {} occupied; {} duplicate groups; {} invalid.".format(
            "COMPLETE" if report["complete"] else "INCOMPLETE", report["proposed_count"],
            report["siblings_checked"], len(report["occupied"]), len(report["duplicates"]), len(report["invalid"])))
        if report["parent_exists"] is False:
            print("Parent is absent; it was not created.")
        for kind in ("occupied", "duplicates", "invalid", "errors"):
            for item in report[kind]:
                print(kind + ": " + json.dumps(item, ensure_ascii=True))
        print(POLICY)
        print(LIMITATION)
    return 2 if not report["complete"] else (1 if report["occupied"] or report["duplicates"] else 0)


if __name__ == "__main__":
    sys.exit(main())
