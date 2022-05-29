interface Dictionary<T> {
    [Key: string]: T;
}

type FormInputEvent = {
    target: HTMLTextAreaElement;
};

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
}

type WaterfallImage = {
    filename: string,
    delay: number,
    x: number,
}

type State = {
    // global persistent
    root: string,
    root_edit: string,
    room_name: string,
    room_name_edit: string,
    room_password: string,
    room_password_edit: string,
    podium: boolean,
    track_list: Dictionary<Track>,

    // global temporary
    show_settings: boolean,
    connected: boolean,
    fullscreen: false,
    audio_allowed: boolean,
    settings: Dictionary<any>,

    // loading screen
    download_size: number | null,
    download_done: number,

    // title screen
    images: Array<WaterfallImage>,

    // playlist screen
    queue: Array<QueueItem>,

    // video screen
    playing: boolean,
    paused: boolean,
    progress: number,
}

declare type Action = import('hyperapp').Action<State>;
declare type Effect = import('hyperapp').Effect<State>;
declare type Dispatchable = import('hyperapp').Dispatchable<State>;
declare type Subscription = import('hyperapp').Subscription<State>;
declare type VNode = import('hyperapp').VNode<State>;
