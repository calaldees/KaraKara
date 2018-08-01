/* ====================================================================
State and state management functions
==================================================================== */

import {random_track} from "./demo";

const state = {
    queue: [
        random_track(), random_track(), random_track(),
        random_track(), random_track(), random_track(),
        random_track(), random_track(), random_track(),
    ],
    playing: false,
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.queue.update_time"   :  3 , //Seconds to poll server
        "karakara.player.autoplay"            : 30, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.websocket.path"             : null,
        "karakara.websocket.port"             : null,
        "karakara.websocket.disconnected_retry_interval": 5, // Seconds to retry websocket in the event of disconnection
        "karakara.event.end": "midnight",
        "HOSTNAME": "karakara.org.uk",
        "QUEUE_ID": "minami",
    },
    progress: 0,
    connected: false,
};

const actions = {
    dequeue: value => state => ({ queue: state.queue.slice(1), playing: false, progress: 0 }),
    enqueue: value => state => ({ queue: state.queue.concat(random_track()) }),
    play: value => state => ({ playing: true, progress: 0 }),
    stop: value => state => ({ playing: false, progress: 0 }),
    queue_updated: value => state => ({ queue: value }),
    settings: value => state => ({ settings: value }),
    get_state: () => state => state,
    update_progress: value => state => ({ progress: value }),
    set_connected: value => state => ({ connected: value }),
};

export {state, actions};