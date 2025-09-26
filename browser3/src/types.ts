export interface Attachment {
    variant: string | null;
    mime: string;
    path: string;
}

export interface Subtitle {
    start: number;
    end: number;
    text: string;
    top: boolean;
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
}

export interface QueueItem {
    id: number;
    performer_name: string;
    session_id: string;
    start_time: number | null;
    track_id: string;
    video_variant: string | null;
    subtitle_variant: string | null;
}
