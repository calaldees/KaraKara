/**
 * turn timestamp into into "{X}min / {X}sec [in the future]"
 */
 export function time_until(now: number, time: number|null): string {
    if(!time) return "";

    const seconds_total = Math.floor(time - now);
    const seconds = seconds_total % 60;
    const minutes = Math.floor(seconds_total / 60);
    if (minutes > 1) {
        return `In ${minutes} mins`;
    }
    if (minutes == 1) {
        return `In ${minutes} min`;
    }
    if (seconds <= 0) {
        return "Now";
    }
    return `In ${seconds} secs`;
}

/**
 * turn seconds into {MM}:{SS}
 */
export function s_to_mns(t: number): string {
    return (
        Math.floor(t / 60) + ":" + (Math.floor(t % 60) + "").padStart(2, "0")
    );
}

/**
 * Looking at an Attachment, get the full URL
 *
 * eg attachment_path(state.root, attachment) -> https://karakara.uk/files/asdfasdfa.mp4
 */
export function attachment_path(root: string, attachment: Attachment): string {
    return root + "/files/" + attachment.path;
}

/**
 * Get the URL, username, and password to be passed to MQTTSubscribe or MQTTPublish
 */
export function mqtt_login_info(state: State): Dictionary<string> {
    return {
        url: state.root.replace("https://", "wss://").replace("http://", "ws://") + "/mqtt",
        username: state.room_name,
        password: state.room_password,
    };
}

/**
 * Turn an ISO8601 date into a nicer time
 *
 * eg "2021-01-03T14:00:00" -> "14:00"
 */
export function short_date(long_date: string): string {
    return long_date.split("T")[1].substring(0, 5);
}

/*
 * Given a list of all tracks in the queue, find which ones are in-progress
 * now or queued for the future
 */
export function current_and_future(now: number, tracks: Array<QueueItem>): Array<QueueItem> {
    return tracks.filter(t => (t.start_time == null || t.start_time + t.track_duration > now));
}

export function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}
