import {random_track} from "./demo";


// ====================================================================
// State and state management functions
// ====================================================================

const state = {
    // global app bits
    connected: false,
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.queue.update_time"   :  3 , //Seconds to poll server
        "karakara.player.autoplay"            : 30, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.player.files"               : "/files/",
        "karakara.websocket.path"             : null,
        "karakara.websocket.port"             : null,
        "karakara.websocket.disconnected_retry_interval": 5, // Seconds to retry websocket in the event of disconnection
        "karakara.event.end": null,
        "HOSTNAME": document.location.hostname,
        "QUEUE_ID": null,
    },

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    progress: 0,
};

const actions = {
    dequeue: () => state => ({ queue: state.queue.slice(1), playing: false, progress: 0 }),
    enqueue: () => state => ({ queue: state.queue.concat(random_track()) }),
    play: () => () => ({ playing: true, progress: 0 }),
    stop: () => () => ({ playing: false, progress: 0 }),
    queue_updated: value => () => ({ queue: value }),
    settings: value => () => ({ settings: value }),
    get_state: () => state => state,
    update_progress: value => () => ({ progress: value }),
    set_connected: value => () => ({ connected: value }),

    // These are a bit messier because the VIDEO object
    // state is separated from the application state :(
    pause: value => (state, actions) => {
        const video = document.getElementsByTagName("video")[0];
        if (!video) {return;}
        if (video.paused) {video.play();}
        else              {video.pause();}
    },
    seek_forwards: value => (state, actions) => {
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime = Math.min(video.currentTime + state.settings["karakara.player.video.skip.seconds"], video.duration);
    },
    seek_backwards: value => (state, actions) => {
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime = Math.max(video.currentTime - state.settings["karakara.player.video.skip.seconds"], 0);
    },
};


// ====================================================================
// populate some demo state if we're running from a local file
// ====================================================================

if(document.location.protocol === "file:") {
    state.queue = [
        random_track(), random_track(), random_track(),
        random_track(), random_track(), random_track(),
        random_track(), random_track(), random_track(),
    ];
    state.settings["karakara.player.files"] = "https://files.shishnet.org/karakara-demo/";
    state.settings["karakara.event.end"] = "midnight";
    state.settings["HOSTNAME"] = "karakara.org.uk";
    state.settings["QUEUE_ID"] = "minami";
}

export {state, actions};