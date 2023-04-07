declare module "*.jpg";
declare module "*.svg";
declare module "u8-mqtt/esm/web/index.js";

type Attachment = {
    mime: string;
    path: string;
};

type TrackListSection = {
    tracks?: Array<Track>;
    groups?: any;
    filters?: any;
};

type Track = {
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

type QueueItem = {
    id: number;
    performer_name: string;
    session_id: string;
    start_time: number | null;
    track_duration: number;
    track_id: string;
};
