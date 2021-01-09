declare module '*.jpg';
declare module 'hyperapp';

declare module "*.json" {
    const value: any;
    export default value;
}

type FormInputEvent = {
    target: HTMLTextAreaElement;
};

interface Dictionary<T> {
    [Key: string]: T;
}

type ApiResponse = {
    status: string,
    messages: Array<string>,
    data: any,
    code: number,
    template: string,
    format: string,
    identity: Dictionary<string>,
    paths: Dictionary<string>,
}

type Attachment = {
    id: number,
    location: string,
    type: string,
    extra_fields: Dictionary<any>,
}

type Track = {
    id: string,
    title: string,
    duration: number,
    tags: Dictionary<Array<string>>,
    description: string,
    attachments: Array<Attachment>,
    lyrics: string,
    srt: string,
    image: string,
    source_filename: string,
    queue: {
        played: Array<any>,
        pending: Array<any>,
    }
}

type QueueItem = {
    id: number,
    track: Track,
    performer_name: string,
    total_duration: number,
}

type State = {
    version: number,

    // global
    root: string,
    screen: string,
    notification: string,

    // login
    tmp_queue_id: string,
    queue_id: string,
    loading: boolean,

    // track list
    track_list: Dictionary<Track>,
    search: string,
    filters: Array<string>,
    expanded: string,

    // track
    track_id: string,
    performer_name: string,
    action: string,

    // queue
    queue: Array<QueueItem>,

    // bookmarks
    bookmarks: Array<string>,
}
