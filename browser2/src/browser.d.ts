declare module '*.jpg';
declare module '*.svg';

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
    mime: string,
    path: string,
}

type TrackListSection = {
    tracks?: Array<Track>,
    groups?: any,
    filters?: any,
};

type Track = {
    id: string,
    duration: number,
    tags: {
        title: Array<string>,
        category?: Array<string>,
        vocaltrack?: Array<string>,
        [x: string]: Array<string> | undefined,
    },
    attachments: {
        video: Array<Attachment>,
        preview: Array<Attachment>,
        image: Array<Attachment>,
        subtitle?: Array<Attachment>,
    },
    lyrics: Array<string>,
}

type QueueItem = {
    id: number,
    performer_name: string,
    session_id: string,
    start_time: number | null,
    track_duration: number,
    track_id: string,
}

type PriorityToken = {
    id: string,
    issued: string,  // ISO8601 Date,
    used: boolean,
    session_id: string,
    valid_start: string,  // ISO8601 Date,
    valid_end: string,  // ISO8601 Date,
}

type State = {
    // global
    root: string,
    root_edit: string,
    screen: string,
    notification: null | {
        text: string,
        style: string,
    },
    priority_token: PriorityToken | null,
    show_settings: boolean,
    download_size: number | null,
    download_done: number,
    booth: boolean,
    widescreen: boolean,
    scroll_stack: Array<number>,
    now: number,

    // login
    session_id: string | null,
    room_name: string,
    room_name_edit: string,
    room_password: string,
    room_password_edit: string,
    loading: boolean,
    is_admin: boolean,

    // track list
    track_list: Dictionary<Track>,
    search: string,
    filters: Array<string>,
    expanded: string | null,

    // track
    track_id: string | null,
    performer_name: string,
    action: string | null,

    // queue
    queue: Array<QueueItem>,
    drop_source: number | null,
    drop_target: number | null,

    // bookmarks
    bookmarks: Array<string>,

    // settings
    settings: Dictionary<any>,

    // priority_tokens
    priority_tokens: Array<PriorityToken>,
}

declare type Action = import('hyperapp').Action<State>;
declare type Effect = import('hyperapp').Effect<State>;
declare type Dispatchable = import('hyperapp').Dispatchable<State>;
declare type Subscription = import('hyperapp').Subscription<State>;
declare type VNode = import('hyperapp').VNode<State>;
