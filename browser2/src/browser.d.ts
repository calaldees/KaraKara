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
    id_short: string,
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

type PriorityToken = {
    id: string,
    issued: Date,
    used: boolean,
    session_owner: string,
    valid_start: Date,
    valid_end: Date,
}

type State = {
    version: number,

    // global
    root: string,
    root_edit: string,
    screen: string,
    notification: {
        text: string,
        style: string,
    },
    show_settings: boolean,

    // login
    queue_id: string,
    queue_id_edit: string,
    queue_password: string,
    queue_password_edit: string,
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
    drop_source: number,
    drop_target: number,

    // bookmarks
    bookmarks: Array<string>,

    // settings
    settings: Dictionary<any>,

    // priority_tokens
    priority_tokens: Array<PriorityToken>,
}
