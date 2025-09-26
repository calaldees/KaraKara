import { Subtitle } from "@/types";
import { parse as parse_iso_duration } from "tinyduration";

/**
 * turn seconds into {MM}:{SS}
 */
export function s_to_mns(t: number): string {
    return (
        Math.floor(t / 60) + ":" + (Math.floor(t % 60) + "").padStart(2, "0")
    );
}

/**
 * Turn an ISO8601 UTC datetime into the user's local time
 *
 * eg "2021-01-03T14:00:00" -> "14:00"
 */
export function short_date(long_date: string): string {
    const date = new Date(long_date);
    return date.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
    });
}

const BIG_GAP = 5;

/*
 * If there is a large gap between subtitles, insert a new "..." subtitle
 * to indicate the gap
 */
export function add_dot_dot_dots(subtitles: Subtitle[]): Subtitle[] {
    let last_end = subtitles[0]?.start ?? 0;
    const out: Subtitle[] = [];
    for (const subtitle of subtitles) {
        if (subtitle.start - last_end > BIG_GAP) {
            out.push({
                start: last_end,
                end: subtitle.start,
                text: "···",
                top: false,
            });
        }
        out.push(subtitle);
        last_end = subtitle.end;
    }
    return out;
}

export function parse_duration(inp: string | number): number {
    if (typeof inp === "number") {
        return inp;
    } else {
        const parsed = parse_iso_duration(inp);
        return (
            (parsed.hours ?? 0) * 3600 +
            (parsed.minutes ?? 0) * 60 +
            (parsed.seconds ?? 0)
        );
    }
}
