import logging
import re
import string
from collections.abc import Generator, Sequence
from datetime import timedelta

from tqdm.contrib.concurrent import thread_map

from pm3.lib.source import SourceType
from pm3.lib.subtitle_processor import Subtitle
from pm3.lib.track import Track

type ErrGen = Generator[str, None, None]
log = logging.getLogger(__name__)


def lint(tracks: Sequence[Track]) -> None:
    """
    Scan through all the data, looking for things which seem suspicious
    and probably want a human to investigate
    """

    thread_map(lint_track, tracks, max_workers=4, desc="lint   ", unit="track")
    lint_library(tracks)


def lint_library(tracks: Sequence[Track]) -> None:
    # Check for inconsistent capitalization of tags across multiple tracks
    # Do this outside of _lint() to avoid threading issues
    all_tags: dict[str, list[str]] = {}
    for track in tracks:
        for source in track.sources:
            if source.type == SourceType.TAGS:
                for k, vs in source.tags.items():
                    all_tags.setdefault(k, []).extend(vs)
    for k, vs in all_tags.items():
        # There are several different tracks with the same title
        if k in {"title", "contact"}:
            continue
        v_by_lower: dict[str, str] = {}
        for v in vs:
            vl = v.lower()
            # BoA and Boa are different
            # Bis, bis, and BiS are three different bands...
            if k == "artist" and vl.lower() in ["boa", "bis"]:
                continue
            if vl in v_by_lower and v_by_lower[vl] != v:
                log.error(f"Tag {k}:{v} has inconsistent capitalization")
            v_by_lower[vl] = v


def lint_track(track: Track) -> None:
    json = track.to_json()

    # Check for a bug where a 3 minute track was reported as 92 minutes
    if json["duration"] > 10 * 60:
        log.error(f"{track.id} is very long ({int(json['duration']) // 60}m)")

    variants = {s.variant for s in track.sources}
    if "Vocal" in variants and "on" not in json["tags"]["vocaltrack"]:
        log.error(f"{track.id} has Vocal variant but no vocaltrack:on tag")
    if "Instrumental" in variants and "off" not in json["tags"]["vocaltrack"]:
        log.error(f"{track.id} has Instrumental variant but no vocaltrack:off tag")

    # for t in track.targets:
    #    if not t.path.exists():
    #        log.error(f"{t.friendly} missing (Sources: {[s.file.relative for s in t.sources]!r})")

    for s in track.sources:
        if s.type in {SourceType.VIDEO, SourceType.IMAGE}:
            if s.meta.aspect_ratio < 1 / 1:
                log.error(f"{s.file.relative} has weird aspect ratio {s.meta.aspect_ratio_str}")

        if s.type == SourceType.TAGS:
            for err_list in [
                lint_tags_required(s.tags),
                lint_tags_banned(s.tags),
                lint_tags_lowercase_keys(s.tags),
                lint_tags_lowercase_values(s.tags),
                lint_tags_use(s.tags),
                lint_tags_source(s.tags),
                lint_tags_duration(s.tags, json["duration"]),
            ]:
                for err in err_list:
                    log.error(f"{s.file.relative}: {err}")

        if s.type == SourceType.SUBTITLES:
            for err_list in [
                lint_subtitles_exists(s.subtitles),
                # Commented out as there's a surprising number of tracks that are very empty
                # lint_subtitles_big_silence(s.file.relative, s.subtitles, duration=json["duration"]),
                lint_subtitles_random_topline(s.subtitles),
                lint_subtitles_spacing(s.subtitles),
            ]:
                for err in err_list:
                    log.error(f"{s.file.relative}: {err}")
            if s.variant != "Hiragana":
                for err in lint_subtitles_line_contents(s.subtitles):
                    log.error(f"{s.file.relative}: {err}")


def lint_tags_required(tags: dict[str, list[str]]) -> ErrGen:
    """
    >>> list(lint_tags_required({"title": ["My Song"], "vocaltrack": ["on"]}))
    ['no category tag', 'no lang tag', 'vocaltrack:on but no vocalstyle']
    """
    # Certain tags are required
    for key in ["title", "category", "vocaltrack", "lang"]:
        if not tags.get(key):
            yield f"no {key} tag"

    # Tracks with vocals should have a vocalstyle
    if tags.get("vocaltrack") == ["on"]:
        if not tags.get("vocalstyle"):
            yield "vocaltrack:on but no vocalstyle"


def lint_tags_banned(tags: dict[str, list[str]]) -> ErrGen:
    # No "red" tags - move these tracks to the WorkInProgress folder instead
    if "red" in tags:
        yield "Put track in WorkInProgress folder instead of using 'red' tag"


def lint_tags_lowercase_keys(tags: dict[str, list[str]]) -> ErrGen:
    """
    All top-level keys should be lowercase; sub-keys can be mixed case

    "Title" can't be uppercase by itself:
      >>> list(lint_tags_lowercase_keys({"Title": ["My Song"], "artist": ["Bob"]}))
      ['Title key which is not lowercase']

    "Cake Series" is allowed to be uppercase because it's a sub-tag of "from":
      >>> list(lint_tags_lowercase_keys({"from": ["Cake Series"], "Cake Series": ["Cakes of Doom"]}))
      []
    """

    all_values = [v for vs in tags.values() for v in vs]
    for key in tags.keys():
        if key != key.lower() and key not in all_values:
            yield f"{key} key which is not lowercase"


def lint_tags_lowercase_values(tags: dict[str, list[str]]) -> ErrGen:
    """
    Values should be lowercase unless they are known exceptions
    (eg, titles and artist names)
    """
    all_values = [v for vs in tags.values() for v in vs]
    for key, values in tags.items():
        if key in all_values:
            continue
        if key in [
            "title",
            "artist",
            "from",
            "contributor",
            "source",
            "contact",
            "info",
            "status",
        ]:
            continue
        for value in values:
            if value != value.lower():
                yield f"{key}:{value} should be lowercase"


def lint_tags_use(tags: dict[str, list[str]]) -> ErrGen:
    """
    "use" tags should be consistent
    """
    if uses := tags.get("use"):
        known_uses = [
            "opening",
            "ending",
            "insert",
            "character",
            "doujin",
            "trailer",
        ]
        for use in uses:
            if use not in known_uses and re.match(r"^(op|ed)(\d+)$", use) is None:
                yield f"weird use:{use} tag"
        for n in range(0, 50):
            if f"op{n}" in uses and "opening" not in uses:
                yield f"use:op{n} but no opening tag"
            if f"ed{n}" in uses and "ending" not in uses:
                yield f"use:ed{n} but no ending tag"


def lint_tags_source(tags: dict[str, list[str]]) -> ErrGen:
    """
    "source" tags should not contain unquoted URLs

      source:http://example.com -- bad, becomes "source":["http"] + "http":["//example.com"]
      source:"http://example.com" -- good, becomes "source":["http://example.com"]
    """
    if "source" in tags:
        if "http" in tags["source"] or "https" in tags["source"]:
            yield "appears to have an unquoted URL in the source tag"


def lint_tags_duration(tags: dict[str, list[str]], duration: float) -> ErrGen:
    if duration > 5 * 60:
        if "full" not in tags.get("length", []):
            yield f"is {duration}s but has no length:full tag"


def lint_subtitles_exists(ls: list[Subtitle]) -> ErrGen:
    """
    >>> list(lint_subtitles_exists([]))
    ['no subtitles']

    >>> list(lint_subtitles_exists([Subtitle(text="Hello", start=timedelta(0), end=timedelta(seconds=2))]))
    ['only one subtitle: Hello']
    """
    if len(ls) == 0:
        yield "no subtitles"
    if len(ls) == 1:
        yield f"only one subtitle: {ls[0].text}"


def lint_subtitles_big_silence(ls: list[Subtitle], duration: float) -> ErrGen:
    """
    Check for large amounts of dead air between lines relative to track duration
    """
    total_silence = timedelta(0)
    total_silence += ls[0].start
    for l1, l2 in zip(ls[:-1], ls[1:]):
        total_silence += l2.start - l1.end
    total_silence += timedelta(seconds=duration) - ls[-1].end
    if total_silence.total_seconds() / duration > 0.5:
        yield f"a lot of dead air between lines: {int(total_silence.total_seconds())}s over {int(duration)}s"


def lint_subtitles_random_topline(ls: list[Subtitle]) -> ErrGen:
    """
    Most lines are on the bottom, but there are a random couple on top,
    normally means that a title line got added
    """
    top_count = len([s for s in ls if s.top])
    bot_count = len(ls) - top_count
    if bot_count > top_count and 3 > top_count > 0:
        yield "random topline: " + ", ".join(repr(s.text) for s in ls if s.top)
    if top_count > bot_count and 3 > bot_count > 0:
        yield "random bottomline: " + ", ".join(repr(s.text) for s in ls if not s.top)


def lint_subtitles_line_contents(ls: list[Subtitle]) -> ErrGen:
    """
    >>> from datetime import timedelta as d
    >>> lines = [
    ...     Subtitle(text="Hello\\nWorld", start=d(0), end=d(seconds=2)),
    ...     Subtitle(text="This is a test ♪", start=d(seconds=2), end=d(seconds=4)),
    ... ]
    >>> list(lint_subtitles_line_contents(lines))
    ['line 1 line contains newline: Hello\\nWorld', "line 2 line contains non-alphanumeric: 'This is a test ♪': '♪' ('\\\\u266a')"]
    """
    for index, l in enumerate(ls):
        if "\n" in l.text:
            yield f"line {index + 1} line contains newline: {l.text}"
        # Manual things:
        #   "♪" -> people adding "instrumental break" markers manually
        ok = string.ascii_letters + string.digits + " ,.'\"[]!?()~-—–:/+’*;&\n" + "áéñāōòèàóíŪú"
        for char in l.text:
            if char not in ok:
                yield f"line {index + 1} line contains non-alphanumeric: {l.text!r}: {char!r} ({ascii(char)})"

    # check that lines have matched brackets
    bracket_pairs = {
        "(": ")",
        "[": "]",
        "{": "}",
        "«": "»",
        "“": "”",
        # "‘": "’",
    }
    for index, l in enumerate(ls):
        stack = []
        for char in l.text:
            if char in bracket_pairs:
                stack.append(char)
            elif char in bracket_pairs.values():
                if not stack:
                    yield f"line {index + 1} line has unmatched closing bracket: {l.text!r}: {char!r}"
                else:
                    open_bracket = stack.pop()
                    if bracket_pairs[open_bracket] != char:
                        yield f"line {index + 1} line has mismatched brackets: {l.text!r}: {open_bracket!r} / {char!r}"
        if stack:
            yield f"line {index + 1} line has unmatched opening bracket: {l.text!r}: {stack!r}"


def lint_subtitles_spacing(ls: list[Subtitle]) -> ErrGen:
    """
    Check for weird stuff between lines (eg gaps or overlaps)

    >>> from datetime import timedelta as d
    >>> lines = [
    ...     Subtitle(text="Hello", start=d(0), end=d(seconds=2)),
    ...     Subtitle(text="Hello", start=d(seconds=2), end=d(seconds=4)),
    ...     Subtitle(text="Hello", start=d(seconds=4), end=d(seconds=6)),
    ...     Subtitle(text="World", start=d(seconds=6, microseconds=50_000), end=d(seconds=8)),
    ...     Subtitle(text="World", start=d(seconds=8), end=d(seconds=10)),
    ...     Subtitle(text="Overlap", start=d(seconds=9, microseconds=900_000), end=d(seconds=12)),
    ... ]
    >>> list(lint_subtitles_spacing(lines))
    ['line 1 no gap between 3+ repeats: Hello', 'line 3 blink between lines: 50: Hello / World', 'line 5 overlapping lines 100: World / Overlap']
    """
    # separate out the top and bottom lines because they may have
    # different timing and we only care about timing glitches
    # within the same area of the screen
    toplines = [l for l in ls if l.top]
    botlines = [l for l in ls if not l.top]
    for ls in [toplines, botlines]:
        for index, (l1, l2, l3) in enumerate(zip(ls[:-1], ls[1:], ls[2:])):
            if l1.end == l2.start and l2.end == l3.start and (l1.text == l2.text == l3.text):
                yield f"line {index + 1} no gap between 3+ repeats: {l1.text}"
        for index, (l1, l2) in enumerate(zip(ls[:-1], ls[1:])):
            if l2.start > l1.end:
                gap = l2.start - l1.end
                if gap < timedelta(microseconds=100_000) and not (l1.text == l2.text):
                    yield (
                        f"line {index + 1} blink between lines: {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}"
                    )
            elif l2.start < l1.end:
                gap = l1.end - l2.start
                yield (f"line {index + 1} overlapping lines {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}")
