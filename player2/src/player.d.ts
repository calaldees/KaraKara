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
    lyrics: string,
    srt_lyrics: Array<SrtLine>,
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
    queue_id: string,
    podium: boolean,

    // global temporary
    show_settings: boolean,
    connected: boolean,
    ws_errors: number,
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
