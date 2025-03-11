export type Attachment = {
    mime: string;
    path: string;
};

export type Track = {
    id: string;
    duration: number;
    tags: {
        title: Array<string>;
        category?: Array<string>;
        vocaltrack?: Array<string>;
        [x: string]: Array<string> | undefined;
    };
    attachments: {
        video: Array<Attachment>;
        preview: Array<Attachment>;
        image: Array<Attachment>;
        subtitle?: Array<Attachment>;
    };
    lyrics: Array<string>;
};

export type QueueItem = {
    id: number;
    performer_name: string;
    session_id: string;
    start_time: number | null;
    track_duration: number;
    track_id: string;
};
