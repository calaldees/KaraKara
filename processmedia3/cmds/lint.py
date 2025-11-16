import logging
import re
from datetime import timedelta
from collections.abc import Sequence

from tqdm.contrib.concurrent import thread_map

from lib.source import SourceType
from lib.track import Track


log = logging.getLogger(__name__)


def lint(tracks: Sequence[Track]) -> None:
    """
    Scan through all the data, looking for things which seem suspicious
    and probably want a human to investigate
    """

    def _lint(track: Track) -> None:
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
            if s.type == SourceType.TAGS:
                # All top-level keys should be lowercase
                # from:Cake Series             -- correct top-level tag
                # Cake Series:Cakes of Doom    -- valid sub-tag
                # Artist:Bob                   -- incorrect top-level tag
                all_values = [v for vs in s.tags.values() for v in vs]
                for key in s.tags.keys():
                    if key != key.lower() and key not in all_values:
                        log.error(
                            f"{s.file.relative} has {key} key which is not lowercase"
                        )

                # Values should be lowercase unless they are known exceptions
                # (eg, titles and artist names)
                for key, values in s.tags.items():
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
                            log.error(
                                f"{s.file.relative} {key}:{value} should be lowercase"
                            )

                # Certain tags are required
                for key in ["title", "category", "vocaltrack", "lang"]:
                    if not s.tags.get(key):
                        log.error(f"{s.file.relative} has no {key} tag")

                # Tracks with vocals should have a vocalstyle
                if s.tags.get("vocaltrack") == ["on"]:
                    if not s.tags.get("vocalstyle"):
                        log.error(
                            f"{s.file.relative} has vocaltrack:on but no vocalstyle"
                        )

                # "use" tags should be consistent
                if uses := s.tags.get("use"):
                    known_uses = [
                        "opening",
                        "ending",
                        "insert",
                        "character song",
                        "doujin song",
                        "trailer",  # ??
                    ]
                    for use in uses:
                        if (
                            use not in known_uses
                            and re.match(r"^(op|ed)(\d+)$", use) is None
                        ):
                            log.error(f"{s.file.relative} has weird use:{use} tag")
                    for n in range(0, 50):
                        if f"op{n}" in uses and "opening" not in uses:
                            log.error(
                                f"{s.file.relative} has use:op{n} but no opening tag"
                            )
                        if f"ed{n}" in uses and "ending" not in uses:
                            log.error(
                                f"{s.file.relative} has use:ed{n} but no ending tag"
                            )

                # "source" tags should not contain unquoted URLs
                #    source:http://example.com -- bad, becomes "source":["http"] + "http":["//example.com"]
                #    source:"http://example.com" -- good, becomes "source":["http://example.com"]
                if "source" in s.tags:
                    if "http" in s.tags["source"] or "https" in s.tags["source"]:
                        log.error(
                            f"{s.file.relative} appears to have an unquoted URL in the source tag"
                        )

                dur = json["duration"]
                if dur > 5 * 60:
                    if "full" not in s.tags.get("length", []):
                        log.error(
                            f"{s.file.relative} is {dur}s but has no length:full tag"
                        )

                # No "red" tags - move these tracks to the WorkInProgress folder instead
                if "red" in s.tags:
                    log.error(f"{s.file.relative} has red tag")

            if s.type == SourceType.SUBTITLES:
                ls = s.subtitles

                # Check for weird stuff at the file level
                if len(ls) == 0:
                    log.error(f"{s.file.relative} has no subtitles")
                if len(ls) == 1:
                    log.error(f"{s.file.relative} has only one subtitle: {ls[0].text}")

                # Check for large amounts of dead air between lines relative to track duration
                # Commented out as there's a surprising number of tracks that are very empty
                """
                total_silence = timedelta(0)
                total_silence += ls[0].start
                for l1, l2 in zip(ls[:-1], ls[1:]):
                    total_silence += l2.start - l1.end
                total_silence += timedelta(seconds=json["duration"]) - ls[-1].end
                total_duration = json["duration"]
                if total_silence.total_seconds() / total_duration > 0.5:
                    log.error(
                        f"{s.file.relative} has a lot of dead air between lines: {int(total_silence.total_seconds())}s over {int(total_duration)}s"
                    )
                """

                # Most lines are on the bottom, but there are a random couple on top,
                # normally means that a title line got added
                top_count = len([s for s in ls if s.top])
                if top_count > 0 and top_count / len(ls) < 0.8:
                    log.error(f"{s.file.relative} has random topline")

                # Check for weird stuff at the line level
                for index, l in enumerate(ls):
                    if "\n" in l.text:
                        log.error(
                            f"{s.file.relative}:{index + 1} line contains newline: {l.text}"
                        )
                    # People manually adding "instrumental break" markers - they should
                    # just leave it empty and subtitle_processor will add as appropriate.
                    # Perhaps better to warn on all non-alphanumeric / punctuation text?
                    if "♪" in l.text:
                        log.error(
                            f"{s.file.relative}:{index + 1} line contains music note: {l.text}"
                        )

                # Check for weird stuff between lines (eg gaps or overlaps)
                # separate out the top and bottom lines because they may have
                # different timing and we only care about timing glitches
                # within the same area of the screen
                toplines = [l for l in ls if l.top]
                botlines = [l for l in ls if not l.top]
                for ls in [toplines, botlines]:
                    for index, (l1, l2, l3) in enumerate(zip(ls[:-1], ls[1:], ls[2:])):
                        if (
                            l1.end == l2.start
                            and l2.end == l3.start
                            and (l1.text == l2.text == l3.text)
                        ):
                            log.error(
                                f"{s.file.relative}:{index + 1} no gap between 3+ repeats: {l1.text}"
                            )
                    for index, (l1, l2) in enumerate(zip(ls[:-1], ls[1:])):
                        if l2.start > l1.end:
                            gap = l2.start - l1.end
                            if gap < timedelta(microseconds=100_000) and not (
                                l1.text == l2.text
                            ):
                                log.error(
                                    f"{s.file.relative}:{index + 1} blink between lines: {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}"
                                )
                        elif l2.start < l1.end:
                            gap = l1.end - l2.start
                            log.error(
                                f"{s.file.relative}:{index + 1} overlapping lines {int(gap.microseconds / 1000)}: {l1.text} / {l2.text}"
                            )

    thread_map(_lint, tracks, max_workers=4, desc="lint   ", unit="track")

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
