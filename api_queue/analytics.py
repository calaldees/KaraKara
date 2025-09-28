#!/usr/bin/env python3

import sys
import json
from ua_parser import parse
import re
from collections import defaultdict
import argparse
from tqdm import tqdm


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
    p.add_argument("--event", help="Only show stats for the given event")
    p.add_argument("--dedupe", default=False, action="store_true", help="Only count each session / IP address once")
    return p.parse_args()


def main():
    args = parse_args()
    bs = defaultdict(lambda: defaultdict(int))
    ips = set()
    total = 0

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

            # analytics.json
            if "user_agent" in d:
                if args.dev is not None:
                    if d.get("dev") != args.dev:
                        continue
                if args.admin is not None:
                    if d.get("admin") != args.admin:
                        continue
                if args.test is not None:
                    if (d.get("room") == "test") != args.test:
                        continue
                if args.room is not None:
                    if d.get("room") != args.room:
                        continue
                ua = parse(d["user_agent"])

            # nginx-access.json
            elif "http_user_agent" in d:
                if "/login.json" not in d["request"]:
                    continue
                if args.room and f"/room/{args.room}/login.json" not in d["request"]:
                    continue
                ua = parse(d["http_user_agent"])

            # unknown
            else:
                ua = None


            if ua and ua.user_agent and ua.user_agent.family and ua.user_agent.major:
                bs[ua.user_agent.family][ua.user_agent.major] += 1
                total += 1
            #else:
            #    print(ua)

    print(f"{total} results")
    for family in sorted(bs.keys()):
        vers = bs[family]
        for ver in sorted(vers.keys()):
            n = vers[ver]
            bl = family_to_browserslist.get(family, "_" + family)
            print(f"{bl:10s} {ver:3s} : {n/total*100:5.2f}%")
    #print(json.dumps(bs, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
