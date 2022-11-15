interface Dictionary<T> {
    [Key: string]: T;
}

type FormInputEvent = {
    target: HTMLTextAreaElement;
};

type Attachment = {
    mime: string,
    path: string,
}

type Track = {
    id: string,
    duration: number,
    tags: {
        title: Array<string>,
        from?: Array<string>,
        artist?: Array<string>,
        vocaltrack?: Array<string>,
    }
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

type State = {
    // global
    root: string,
    root_edit: string,
    room_name: string,
    room_name_edit: string,
    room_password: string,
    room_password_edit: string,
    podium: boolean,
    track_list: Dictionary<Track>,
    is_admin: boolean,
    show_settings: boolean,
    connected: boolean,
    fullscreen: boolean,
    audio_allowed: boolean,
    settings: Dictionary<any>,
    now: number,
    notification: null | {
        text: string,
        style: string,
    },

    // loading screen
    download_size: number | null,
    download_done: number,

    // playlist screen
    queue: Array<QueueItem>,
}

// Our Action is like hyperapp's Action, except while theirs is generic,
// ours specifically acts upon our State object.
declare type Action = import('hyperapp').Action<State>;
declare type Effect = import('hyperapp').Effect<State>;
declare type Dispatch = import('hyperapp').Dispatch<State>;
declare type Dispatchable<P=any> = import('hyperapp').Dispatchable<State, P>;
declare type Subscription = import('hyperapp').Subscription<State>;
declare type Unsubscribe = import('hyperapp').Unsubscribe;
declare type VNode = import('hyperapp').VNode<State>;
