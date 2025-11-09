import type { Attachment, QueueItem } from "@/types";

/**
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(attachment) -> /files/asdfasdfa.mp4
 */
export function attachment_path(attachment: Attachment): string {
    return "/files/" + attachment.path;
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
    const proto = window.location.protocol == "https:" ? "wss:" : "ws:";
    return proto + "//" + window.location.host + "/mqtt";
}

export function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

/*
 * Given a list of all tracks in the queue, find which ones are in-progress
 * now or queued for the future
 */
export function current_and_future(
    now: number,
    queue: QueueItem[],
): QueueItem[] {
    return queue.filter(
        (t) => t.start_time == null || t.start_time + t.track_duration > now,
    );
}
