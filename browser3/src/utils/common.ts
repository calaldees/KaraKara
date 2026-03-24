import type { Attachment, QueueItem } from "@/types";

/**
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(attachment) -> /files/asdfasdfa.mp4
 */
export function attachment_path(attachment: Attachment): string {
    if (
        attachment.path.startsWith("http://") ||
        attachment.path.startsWith("https://")
    ) {
        return attachment.path;
    }
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

/**
 * Create a mock fetch function for testing/storybook that returns mock data
 * based on the requested path
 *
 * @param pathMap - Map of path patterns to content to return
 * @returns Mock fetch function
 */
export function createMockFetch(pathMap: Record<string, any>): typeof fetch {
    return ((url: string | URL | Request, init?: RequestInit) => {
        const urlString =
            typeof url === "string"
                ? url
                : url instanceof URL
                  ? url.toString()
                  : url.url;
        console.log("Mock fetch called with:", urlString, init);

        // Find matching path in the map
        let responseData = null;
        for (const [pattern, content] of Object.entries(pathMap)) {
            if (
                urlString.includes(pattern) ||
                new RegExp(pattern).test(urlString)
            ) {
                responseData = content;
                break;
            }
        }

        if (responseData === null) {
            console.warn(`No mock data found for URL: ${urlString}`);
            responseData = [];
        }

        // Create a proper ReadableStream with the mock data
        const encoder = new TextEncoder();
        const data = encoder.encode(JSON.stringify(responseData));

        const stream = new ReadableStream({
            start(controller) {
                controller.enqueue(data);
                controller.close();
            },
        });

        return Promise.resolve(
            new Response(stream, {
                status: 200,
                headers: { "Content-Type": "application/json" },
            }),
        );
    }) as typeof fetch;
}
