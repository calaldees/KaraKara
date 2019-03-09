import {get_lyrics, api} from "./util";


// ====================================================================
// State and state management functions
// ====================================================================

const state = {
    // global app bits
    connected: false,
    audio_allowed: (new AudioContext()).state === "running",
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.autoplay"            : 0, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.event.end"                  : null,
        "karakara.podium.video_lag"           : 0.50,  // adjust to get podium and projector in sync
        "karakara.podium.soft_sub_lag"        : 0.35,  // adjust to get soft-subs and hard-subs in sync
    },
    socket: null,

    // title screen
    images: [],

    // playlist screen
    queue: [],

    // video screen
    playing: false,
    paused: false,
    progress: 0,
};

const actions = {
    // this has nothing to do with the player, we just need
    // to make sure that the user has clicked in order for
    // chrome to allow auto-play.
    click: () => () => ({ audio_allowed: true }),

    // general application state
    get_state: () => state => state,
    set_socket: value => () => ({ socket: value }),
    set_connected: value => () => ({ connected: value }),
    check_settings: () => (state, actions) => {
        api(state, "GET", "settings", {}, function(data) {
            actions.set_settings(Object.assign(state.settings, data.settings));
        });
        if(state.images.length === 0) {
            api(state, "GET", "random_images", {count: 25}, function(data) {
                let n=0;
                actions.set_images(data.images.map(function(fn) {
                    return {
                        filename: fn,
                        x: (n++ / data.images.length),
                    }
                }));
            });
        }
    },
    set_settings: value => () => ({ settings: value }),
    set_images: value => () => ({ images: value }),

    // current track controls
    play: () => (state) => ({
        playing: true,
        // if we're already playing, leave the state alone;
        // if we're starting a new song, start it un-paused from 0s
        paused: state.playing ? state.paused : false,
        progress: state.playing ? state.progress : 0,
    }),
    pause: () => (state) => {
        const video = document.getElementsByTagName("video")[0];
        if (video) {
            if (state.paused) {video.play();}
            else              {video.pause();}
        }
        return { paused: !state.paused };
    },
    stop: () => () => ({
        playing: false,
        paused: false,
        progress: 0,
    }),
    set_progress: value => () => ({ progress: value }),
    seek_forwards: value => (state, actions) => {
        const skip = value || state.settings["karakara.player.video.skip.seconds"];
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime += skip;
        return { progress: state.progress + skip };
    },
    seek_backwards: value => (state, actions) => {
        const skip = value || state.settings["karakara.player.video.skip.seconds"];
        const video = document.getElementsByTagName("video")[0];
        if(video) video.currentTime -= skip;
        return { progress: state.progress - skip };
    },

    // playlist controls
    check_queue: () => (state, actions) => {
        api(state, "GET", "queue_items", {}, function(data) {
            function merge_lyrics(item) {
                item.track.lyrics = get_lyrics(state, item.track);
                return item;
            }
            let queue_with_lyrics = data.queue.map((item) => merge_lyrics(item));
            actions.set_queue(queue_with_lyrics);
        });
    },
    set_queue: value => (state, actions) => {
        // if the first song in the queue has changed, stop playing
        if(state.queue.length === 0 || value.length === 0 || state.queue[0].id !== value[0].id) {
            return { queue: value, playing: false, paused: false, progress: 0 };
        }
        else {
            return { queue: value };
        }
    },
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

    // Tell the network what to do
    send: value => (state, actions) => {
        console.log("websocket_send("+ value +")");
        state.socket.send(value);
    },
    set_track_status: value => (state, actions) => {
        actions.dequeue();
        api(state, "PUT", "queue_items", {
            "queue_item.id": state.queue[0].id,
            "status": value,
            "uncache": new Date().getTime()
        }, function(data) {
            actions.check_queue();
        });
    },
};

export {state, actions};
