import type { Attachment, QueueItem, Settings, Track } from "@/types";
import { SettingsSchema } from "../schemas";

/**
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(attachment) -> /files/asdfasdfa.mp4
 */
export function attachment_path(attachment: Pick<Attachment, "path">): string {
    const files = new URL("/files/", window.location.origin);
    const url = new URL(attachment.path, files);
    return url.origin === window.location.origin ? url.pathname : url.href;
}

/**
 * turn timestamp into into "{X}min / {X}sec [in the future]"
 */
export function time_until(now: number, time: number | null): string {
    if (time === null) return "";

    const seconds_total = Math.floor(time - now);
    const seconds = seconds_total % 60;
    const minutes = Math.floor(seconds_total / 60);
    if (minutes > 1) {
        return `In ${minutes} mins`;
    }
    if (minutes === 1) {
        return `In ${minutes} min`;
    }
    if (seconds <= 0) {
        return "Now";
    }
    return `In ${seconds} secs`;
}

/**
 * Get the URL, username, and password to be passed to MQTTSubscribe or MQTTPublish
 */
export function mqtt_url(): string {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return proto + "//" + window.location.host + "/api/mqtt";
}

export function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

/*
 * Given a list of all tracks in the queue, find which ones are in-progress
 * now or queued for the future (+1 second buffer to account for the video
 * taking a moment to start)
 */
export function current_and_future(
    now: number,
    queue: QueueItem[],
): QueueItem[] {
    return queue.filter(
        (t) =>
            t.start_time == null || t.start_time + t.track_duration + 1 > now,
    );
}

export function track_title(
    track: Pick<Track, "tags" | "id"> | undefined,
): string {
    if (!track) {
        return "(invalid track)";
    }
    if (track.tags.title && track.tags.title[0]) {
        return track.tags.title[0];
    }
    return track.id;
}

/**
 * Extracts default values from a JSON schema
 */
export function get_defaults_from_schema(schema: any): Record<string, any> {
    const defaults: Record<string, any> = {};

    if (schema.properties) {
        Object.entries(schema.properties).forEach(
            ([key, prop]: [string, any]) => {
                if (prop.default !== undefined) {
                    defaults[key] = prop.default;
                }
            },
        );
    }

    return defaults;
}

/**
 * Get default settings for a room
 */
export function get_default_settings(): Settings {
    return get_defaults_from_schema(SettingsSchema) as Settings;
}
