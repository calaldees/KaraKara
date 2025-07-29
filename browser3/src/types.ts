export interface Attachment {
    mime: string;
    path: string;
}

export interface Track {
    id: string;
    duration: number;
    tags: {
        title: string[];
        category?: string[];
        vocaltrack?: string[];
        [x: string]: string[] | undefined;
    };
    attachments: {
        video: Attachment[];
        image: Attachment[];
        subtitle?: Attachment[];
    };
    lyrics: string[];
}

export interface QueueItem {
    id: number;
    performer_name: string;
    session_id: string;
    start_time: number | null;
    track_duration: number;
    track_id: string;
}
