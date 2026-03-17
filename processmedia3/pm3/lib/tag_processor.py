import argparse
import csv
import sys
from io import StringIO
from itertools import pairwise
from pathlib import Path

import tomlkit


def parse_tags(data: str) -> dict[str, list[str]]:
    r"""
    >>> data = '''
    ... \ufeff
    ... category:anime
    ... from:Macross:Macross Dynamite 7
    ... use:opening
    ... title:Dynamite Explosion
    ... artist:Fire Bomber
    ... artist:Yoshiki "Test" Fukuyama
    ... retro
    ... source:"https://www.youtube.com/watch?v=1b2a8d3e4f5"
    ... \ufeff'''
    >>> from pprint import pprint
    >>> pprint(parse_tags(data))
    {'': ['retro'],
     'Macross': ['Macross Dynamite 7'],
     'artist': ['Fire Bomber', 'Yoshiki "Test" Fukuyama'],
     'category': ['anime'],
     'from': ['Macross'],
     'source': ['https://www.youtube.com/watch?v=1b2a8d3e4f5'],
     'title': ['Dynamite Explosion'],
     'use': ['opening']}
    """
    data = data.strip().strip("\ufeff").strip()
    tags_values: dict[str, list[str]] = {}

    for row in csv.reader(StringIO(data), delimiter=":"):
        row = list(filter(None, (i.strip() for i in row)))
        if len(row) == 1:
            tags_values.setdefault("", []).append(row[0])
        else:
            for parent, tag in pairwise(row):
                tags_values.setdefault(parent, []).append(tag)

    return dict((k, sorted(set(v))) for k, v in tags_values.items())


def main() -> None:
    parser = argparse.ArgumentParser(description="Process tag files in .txt format and convert to TOML")
    parser.add_argument("files", nargs="+", type=Path, metavar="FILE", help="Input .txt files to process")
    parser.add_argument(
        "-o",
        "--output",
        action="store_true",
        help="Write output to disk instead of printing to stdout",
    )

    args = parser.parse_args()

    for input_file in args.files:
        try:
            data = input_file.read_text(encoding="utf-8")
            tags = parse_tags(data)

            doc = tomlkit.document()
            for key, values in tags.items():
                doc[key] = values
            toml_output = tomlkit.dumps(doc)

            if args.output:
                output_file = input_file.with_suffix(".toml")
                output_file.write_text(toml_output, encoding="utf-8")
                print(f"Wrote {output_file}", file=sys.stderr)
            else:
                if len(args.files) > 1:
                    print(f"# {input_file}")
                print(toml_output)

        except FileNotFoundError:
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
