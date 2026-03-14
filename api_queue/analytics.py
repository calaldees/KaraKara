#!/usr/bin/env python3

import json
from ua_parser import parse
from collections import defaultdict
import argparse
from tqdm import tqdm
import dateparser
import typing as t


family_to_browserslist = {
    "Chrome": "chrome",
    "Chrome Mobile": "and_chr",
    "Chrome Mobile iOS": "ios_chr",   # ??
    "Edge": "edge",
    "Facebook": "facebook", # ??
    "Firefox": "firefox",
    "Firefox Mobile": "and_ff",
    "Mobile Safari": "ios_saf",
    "Phantom": "phantom",  # ??
    "Safari": "safari",
    "Samsung Internet": "samsung",
    #and_qq
    #and_uc
    #android
    #baidu
    #bb
    #ie
    #ie_mob
    #kaios
    #op_mini
    #op_mob
    #opera
}


def boolean_flag(parser, name, default=None, help=None):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        f"--{name}",
        dest=name,
        action="store_true",
        help=help
    )
    group.add_argument(
        f"--no-{name}",
        dest=name,
        action="store_false",
        help=argparse.SUPPRESS  # suppress duplicate help text
    )
    parser.set_defaults(**{name: default})


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("inputs", nargs="*", default=["/logs/analytics.json"])
    boolean_flag(p, "dev", help="Only show dev-mode (--no-dev to exclude dev mode)")
    boolean_flag(p, "admin", help="Only show admins (--no-admin to exclude admins)")
    boolean_flag(p, "test", help="Only show 'test' room (--no-test to exclude 'test' room)")
    p.add_argument("--room", help="Only show stats for the given room")
    p.add_argument("--date-from", help="Only show stats from this date (YYYY-MM-DD)", type=dateparser.parse)
    p.add_argument("--date-to", help="Only show stats up to this date (YYYY-MM-DD)", type=dateparser.parse)
    p.add_argument("--dedupe", default=False, action="store_true", help="Only count each session / IP address once")
    return p.parse_args()


def filter_excludes(args: argparse.Namespace, d: dict) -> bool:
    if args.dev is not None:
        if d.get("dev") != args.dev:
            return True
    if args.admin is not None:
        if d.get("admin") != args.admin:
            return True
    if args.test is not None:
        if (d.get("room") == "test") != args.test:
            return True
    if args.room is not None:
        if d.get("room") != args.room:
            return True
    date = dateparser.parse(d["time"])
    if args.date_from is not None:
        if date < args.date_from:
            return True
    if args.date_to is not None:
        if date > args.date_to:
            return True
    return False


def get_all_lines(args: argparse.Namespace) -> t.Generator[dict, None, None]:
    ips = set()
    for fn in args.inputs:
        with open(fn) as fp:
            lines = fp.readlines()
        for line in tqdm(lines, desc=fn):
            d = json.loads(line)

            if args.dedupe:
                ip = d.get("session", d.get("remote_addr", None))
                if ip in ips:
                    continue
                ips.add(ip)

            if filter_excludes(args, d):
                continue

            yield d


def main():
    args = parse_args()

    bs = defaultdict(lambda: defaultdict(int))
    total = 0

    for d in get_all_lines(args):
        ua = parse(d["user_agent"])
        if ua and ua.user_agent and ua.user_agent.family and ua.user_agent.major:
            bs[ua.user_agent.family][ua.user_agent.major] += 1
            total += 1

    print(f"{total} results")
    for family in sorted(bs.keys()):
        vers = bs[family]
        for ver in sorted(vers.keys()):
            n = vers[ver]
            bl = family_to_browserslist.get(family, "_" + family)
            print(f"{bl:15s} {ver:3s} : {n/total*100:5.2f}% ({n})")


if __name__ == "__main__":
    main()
