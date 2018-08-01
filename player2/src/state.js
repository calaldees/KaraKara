import {get_lyrics, api} from "./util";


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
        "karakara.event.end"                  : null,
    },

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    progress: 0,
};

const actions = {
    dequeue: () => state => ({ queue: state.queue.slice(1), playing: false, progress: 0 }),
    // enqueue: () => state => ({ queue: state.queue.concat(random_track()) }),
    play: () => () => ({ playing: true, progress: 0 }),
    stop: () => () => ({ playing: false, progress: 0 }),
    get_state: () => state => state,
    set_progress: value => () => ({ progress: value }),
    set_connected: value => () => ({ connected: value }),

    check_settings: () => (state, actions) => {
        api(state, "settings", function(data) {
            let new_settings = state.settings;
            for(let key in data.settings) {
                new_settings[key] = data.settings[key];
            }
            actions.set_settings(new_settings);
        });
    },
    set_settings: value => () => ({ settings: value }),

    check_queue: () => (state, actions) => {
        api(state, "queue_items", function(data) {
            actions.set_queue(data.queue);
        });
    },
    set_queue: value => () => ({ queue: value }),

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

export {state, actions};