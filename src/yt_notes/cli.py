import argparse
import sys
from pathlib import Path

from .doctor import check_dependencies
from .ingest import ingest
from .notevalidate import validate_note


def _cmd_doctor(_args) -> int:
    ok = True
    for d in check_dependencies():
        mark = "✓" if d["present"] else "✗"
        print(f"  {mark} {d['name']}")
        if not d["present"]:
            ok = False
            print(f"      {d['hint']}")
    print("All dependencies present." if ok else "Some dependencies are missing (see hints).")
    return 0 if ok else 1


def _cmd_ingest(args) -> int:
    bp = ingest(args.url, force=args.force, model=args.model)
    print(str(bp))
    return 0


def _cmd_validate(args) -> int:
    problems = validate_note(Path(args.note).read_text(), args.bundle)
    if not problems:
        print("OK")
        return 0
    for p in problems:
        print(f"  ✗ {p}")
    return 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="yt-notes")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(func=_cmd_doctor)
    ing = sub.add_parser("ingest")
    ing.add_argument("url")
    ing.add_argument("--force", action="store_true")
    ing.add_argument("--model", default="base")
    ing.set_defaults(func=_cmd_ingest)
    val = sub.add_parser("validate")
    val.add_argument("note", help="path to the note markdown file")
    val.add_argument("bundle", help="path to the bundle directory")
    val.set_defaults(func=_cmd_validate)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
