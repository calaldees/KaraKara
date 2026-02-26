#!/usr/bin/env python3
import argparse
import sys

# Unicode ranges
HIRAGANA_RANGE = ("\u3040", "\u309f")
KATAKANA_RANGE = ("\u30a0", "\u30ff")
KATAKANA_PHONO_EXT = ("\u31f0", "\u31ff")
KANJI_RANGE = ("\u4e00", "\u9fff")  # CJK Unified Ideographs
ASCII_RANGE = (0x00, 0x7F)


def in_range(char, start, end):
    return start <= char <= end


def analyze_text(text):
    counts = {"hiragana": 0, "katakana": 0, "kanji": 0, "ascii": 0, "other": 0}

    for ch in text:
        code = ord(ch)

        if in_range(ch, *HIRAGANA_RANGE):
            counts["hiragana"] += 1
        elif in_range(ch, *KATAKANA_RANGE) or in_range(ch, *KATAKANA_PHONO_EXT):
            counts["katakana"] += 1
        elif in_range(ch, *KANJI_RANGE):
            counts["kanji"] += 1
        elif ASCII_RANGE[0] <= code <= ASCII_RANGE[1]:
            counts["ascii"] += 1
        else:
            counts["other"] += 1

    total = len(text) if len(text) > 0 else 1
    percentages = {k: (v / total) * 100 for k, v in counts.items()}

    return counts, percentages


def main():
    parser = argparse.ArgumentParser(
        description="Detect and quantify Hiragana, Katakana, Kanji, ASCII, and other characters."
    )
    parser.add_argument("file", nargs="?", help="File to analyse")

    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    counts, percentages = analyze_text(text)

    print("Counts:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    print("\nPercentages:")
    for k, v in percentages.items():
        print(f"  {k}: {v:.2f}%")


if __name__ == "__main__":
    main()
