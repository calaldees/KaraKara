#!/usr/bin/env python3

import sys
import json
from ua_parser import parse
import re
from collections import defaultdict
import argparse

p = argparse.ArgumentParser()
p.add_argument("inputs", nargs="*", default=["/logs/analytics.json"])
args = p.parse_args()

bs = defaultdict(lambda: defaultdict(int))

for fn in args.inputs:
    for line in open(fn):
        d = json.loads(line)
        ua = parse(d["ua"])
        bs[ua.user_agent.family][ua.user_agent.major] += 1

print(json.dumps(bs, indent=2, sort_keys=True))
