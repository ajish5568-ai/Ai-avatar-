#!/usr/bin/env python3
import argparse

from dotenv import load_dotenv

from avatar_series.config import load_config
from avatar_series.heygen import HeyGenClient
from avatar_series.pipeline import run


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(description="AI avatar presenter video series")
    ap.add_argument("-c", "--config", default="series.yaml")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="render episodes")
    g.add_argument("episodes", nargs="*", help="episode ids (default: all)")
    g.add_argument("--dry-run", action="store_true", help="write payloads, no API calls")
    g.add_argument("--force", action="store_true", help="re-render even if done")

    sub.add_parser("list-avatars")
    sub.add_parser("list-voices")
    args = ap.parse_args()

    if args.cmd == "generate":
        run(load_config(args.config), set(args.episodes) or None, args.dry_run, args.force)
    elif args.cmd == "list-avatars":
        for a in HeyGenClient().list_avatars():
            print(a.get("avatar_id"), "-", a.get("avatar_name"))
    elif args.cmd == "list-voices":
        for v in HeyGenClient().list_voices():
            print(v.get("voice_id"), "-", v.get("name"), f"({v.get('language')})")


if __name__ == "__main__":
    main()
