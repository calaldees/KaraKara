declare module '*.jpg';

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

type SrtLine = {
    id: string,
    text: string,
    start: number,
    end: number,
}

type Track = {
    id: string,
    title: string,
    duration: number,
    tags: Dictionary<Array<string>>,
    attachments: Array<Attachment>,
    lyrics: Array<SrtLine>,
}

type QueueItem = {
    id: number,
    track: Track,
    performer_name: string,
    total_duration: number,
    session_owner: string,
}

type PriorityToken = {
    id: string,
    issued: string,  // ISO8601 Date,
    used: boolean,
    session_owner: string,
    valid_start: string,  // ISO8601 Date,
    valid_end: string,  // ISO8601 Date,
}

type State = {
    version: number,

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

    // login
    session_id: string | null,
    room_name: string,
    room_password: string,
    room_password_edit: string,
    loading: boolean,

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
