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
    description: string,
    attachments: Array<Attachment>,
    // .srt_lyrics is the only field which doesn't come directly
    // as-is from the server. The server broadcasts .srt as a text
    // field, and on each update, we re-parse that into .srt_lyrics
    srt_lyrics: Array<SrtLine>,
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

    // global temporary
    show_settings: boolean,
    connected: boolean,
    fullscreen: false,
    audio_allowed: boolean,
    settings: Dictionary<any>,

    // title screen
    images: Array<WaterfallImage>,

    // playlist screen
    queue: Array<QueueItem>,

    // video screen
    playing: boolean,
    paused: boolean,
    progress: number,
}
