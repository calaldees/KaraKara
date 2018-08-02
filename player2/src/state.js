import {get_lyrics, api} from "./util";


// ====================================================================
// State and state management functions
// ====================================================================

const state = {
    // global app bits
    connected: false,
    clicked: false,
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.autoplay"            : 30, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.websocket.path"             : "/ws/",
        "karakara.websocket.port"             : null,
        "karakara.event.end"                  : null,
    },
    socket: null,

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    paused: false,
    progress: 0,
};

const actions = {
    dequeue: () => state => ({
        // remove the first song
        queue: state.queue.slice(1),
        // and stop playing (same as .stop(), but we
        // want to do it all in a single state update
        // to avoid rendering an incomplete state)
        playing: false,
        paused: false,
        progress: 0,
    }),
    play: () => (state) => ({
        playing: true,
        // if we're already playing, leave the state alone;
        // if we're starting a new song, start it un-paused from 0s
        paused: state.playing ? state.paused : false,
        progress: state.playing ? state.progress : 0,
    }),
    stop: () => () => ({
        playing: false,
        paused: false,
        progress: 0,
    }),
    get_state: () => state => state,
    set_socket: value => () => ({ socket: value }),
    set_progress: value => () => ({ progress: value }),
    set_connected: value => () => ({ connected: value }),
    click: () => () => ({ clicked: true }),

    // Tell the network as a whole what to do. We could
    // react to these signals immediately, but by sending
    // them remotely and waiting for a response, all the
    // clients can be more in sync.
    send_play: value => (state, actions) => {state.socket.send("play");},
    send_ended: value => (state, actions) => {state.socket.send("ended");},

    check_settings: () => (state, actions) => {
        api(state, "settings", function(data) {
            actions.set_settings(Object.assign(state.settings, data.settings));
        });
    },
    set_settings: value => () => ({ settings: value }),

    check_queue: () => (state, actions) => {
        api(state, "queue_items", function(data) {
            function merge_lyrics(item) {
                item.track.lyrics = get_lyrics(state, item.track);
                return item;
            }
            let queue_with_lyrics = data.queue.map((item) => merge_lyrics(item));
            actions.set_queue(queue_with_lyrics);
        });
    },
    set_queue: value => () => ({ queue: value }),

    // These are a bit messier because the VIDEO object
    // state is separated from the application state :(
    pause: value => (state, actions) => {
        const video = document.getElementsByTagName("video")[0];
        if (video) {
            if (state.paused) {video.play();}
            else              {video.pause();}
        }
        return { paused: !state.paused };
    },
    seek_forwards: value => (state, actions) => {
        const skip = state.settings["karakara.player.video.skip.seconds"];
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime += skip;
        return { progress: state.progress + skip };
    },
    seek_backwards: value => (state, actions) => {
        const skip = state.settings["karakara.player.video.skip.seconds"];
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime -= skip;
        return { progress: state.progress - skip };
    },
};

export {state, actions};