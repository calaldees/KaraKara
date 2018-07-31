import { app } from "hyperapp";
import { state, actions } from "./state.js";
import { view } from "./view.js";

const player = app(state, actions, view, document.body);


/* ====================================================================
Video controls, bypassing app state
==================================================================== */

function _get_video() {
    return document.getElementsByTagName("video")[0];
}
function vid_pause() {
    const video = _get_video();
    if (!video) {return;}
    if (video.paused) {video.play();}
    else              {video.pause();}
}
function vid_seek_forwards() {
    const settings = player.get_state().settings;
    const video = _get_video();
    if (!video) {return;}
    video.currentTime = Math.min(video.currentTime + settings["karakara.player.video.skip.seconds"], video.duration);
}
function vid_seek_backwards() {
    const settings = player.get_state().settings;
    const video = _get_video();
    if (!video) {return;}
    video.currentTime = Math.max(video.currentTime - settings["karakara.player.video.skip.seconds"], 0);
}


/* ====================================================================
Network controls
==================================================================== */

// TODO: poll main.setQueue(getJson("/api/queue.json"))
// TODO: onended = dequeue() + report completion to server
let interval_queue_refresh = null;
function start_queue_poll() {
    const settings = player.get_state().settings;
    if (!interval_queue_refresh) {
        interval_queue_refresh = setInterval(update_playlist, settings["karakara.player.queue.update_time"] * 1000);
        console.log('queue poll time = '+settings["karakara.player.queue.update_time"]);
    }
}
function stop_queue_poll() {
    if (interval_queue_refresh) {
        clearInterval(interval_queue_refresh);
        interval_queue_refresh = null;
    }
}

// Websocket ------------------------------------------------------------------
let socket;
let socket_retry_interval = null;
function setup_websocket() {
    const settings = player.get_state().settings;
    const ws_path = settings['karakara.websocket.path'];
    const ws_port = settings['karakara.websocket.port'];

    if (!ws_port && !ws_path) {
        console.error("setup_websocket", "Websocket port or path not specified - remote control disabled");
        return;
    }

    const websocket_url = (
        (document.location.protocol === "https:" ? 'wss://' : 'ws://') +
        document.location.hostname +
        (ws_port ? ":" + ws_port : "") +
        (ws_path ? ws_path : "")
    );
    console.log("setup_websocket", websocket_url);

    socket = new WebSocket(websocket_url);
    socket.onopen = function() {
        // Authenticate client with session key on socket connect
        // TODO - replace with use of settings['session_key'] or server could
        // just use the actual http-header
        const session_key = document.cookie.match(/karakara_session=([^;\s]+)/)[1];
        socket.send(session_key);
        player.set_connected(true);
        if (socket_retry_interval) {
            clearInterval(socket_retry_interval);
            socket_retry_interval = null;
        }
    };
    socket.onclose = function() {
        socket = null;
        player.set_connected(false);
        if (!socket_retry_interval) {
            socket_retry_interval = setInterval(
                setup_websocket,
                settings["karakara.websocket.disconnected_retry_interval"]*1000
            );
        }
    };
    socket.onmessage = function(msg) {
        const cmd = $.trim(msg.data);
        console.log('Websocket: Remote command: '+cmd);
        const commands = {
            "skip": player.dequeue,
            "play": player.play,
            "stop": player.stop,
        };
        if (cmd in commands) {commands[cmd]();}
        else {console.log("unknown command: " + cmd)}
    };
}


/* ====================================================================
Local controls
==================================================================== */

const KEYCODE = {
    BACKSPACE: 8,
    ENTER    :13,
    ESCAPE   :27,
    LEFT     :37,
    RIGHT    :39,
    SPACE    :32,
    A        :65,
    S        :83,
    T        :84,
};
document.onkeydown = function(e) {
    let handled = true;
    switch (e.which) {
        case KEYCODE.S        : player.dequeue(); break; // skip
        case KEYCODE.A        : player.enqueue(); break; // add
        case KEYCODE.ENTER    : player.play(); break;
        case KEYCODE.ESCAPE   : player.stop(); break;
        case KEYCODE.LEFT     : vid_seek_backwards();break;
        case KEYCODE.RIGHT    : vid_seek_forwards(); break;
        case KEYCODE.SPACE    : vid_pause(); break;
        default: handled = false;
    }
    if (handled) {
        e.preventDefault();
    }
};

if(window.location.hash === "#podium") {
    const FPS = 5;
    setInterval(
        function() {
            let state = player.get_state();
            if(!state.playing) {
                if(state.settings["karakara.player.autoplay"] === 0) return;
                if(state.progress >= state.settings["karakara.player.autoplay"]) {player.play();}
                else {player.update_progress(state.progress + 1/FPS);}
            }
            else {
                if(state.progress >= state.queue[0].track.duration) {player.stop();}
                else {player.update_progress(state.progress + 1/FPS);}
            }
        },
        1000/FPS
    );
}
