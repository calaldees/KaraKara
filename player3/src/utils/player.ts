import type { Subtitle } from "@/types";

/**
 * turn seconds into {MM}:{SS}
 */
export function s_to_mns(t: number): string {
    return `${Math.floor(t / 60)}:${(`${Math.floor(t % 60)}`).padStart(2, "0")}`;
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

export async function canAutoplayWithSound() {
    try {
        const ctx = new window.AudioContext();
        const source = ctx.createBufferSource();
        source.buffer = ctx.createBuffer(1, 1, 22050); // tiny silent buffer
        source.connect(ctx.destination);
        source.start(0);
        await ctx.resume();
        source.disconnect();
        await ctx.close();
        return true;
    } catch (_e) {
        return false;
    }
}
