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
    if (!settings['karakara.websocket.port'] && !settings['karakara.websocket.path']) {
        console.error("setup_websocket", "Websocket port or path not specified - remote control disabled");
        return;
    }

    let websocket_url = (IS_SECURE ? 'wss://' : 'ws://') + HOSTNAME;
    if (settings['karakara.websocket.path']) {
        websocket_url += settings['karakara.websocket.path'];
    } else {
        websocket_url += ":"+settings['karakara.websocket.port']+"/";
    }
    console.log("setup_websocket", websocket_url);

    socket = new WebSocket(websocket_url);
    socket.onopen = function(){ // Authenicate client with session key on socket connect
        const session_key = document.cookie.match(/karakara_session=([^;\s]+)/)[1];  // TODO - replace with use of settings['session_key'] or server could just use the actual http-header
        socket.send(session_key);
        $('body').removeClass('websocket_disconnected');
        console.log("Websocket: Connected");
        if (socket_retry_interval) {
            clearInterval(socket_retry_interval);
            socket_retry_interval = null;
        }
        stop_queue_poll();
        if (screens.current == 'video') {
            console.log("auto play video on websocket reconnection");
            get_video().play();
            // TODO: play is not quite perfect as the video resets
        }
        else {
            update_playlist();
        }

    };
    socket.onclose  = function() {
        socket = null;
        $('body').addClass('websocket_disconnected');
        console.log("Websocket: Disconnected");
        if (!socket_retry_interval) {
            socket_retry_interval = setInterval(setup_websocket,settings["karakara.websocket.disconnected_retry_interval"]*1000);
        }
        start_queue_poll();
    };
    socket.onmessage = function(msg) {
        const cmd = $.trim(msg.data);
        console.log('Websocket: Remote command: '+cmd);
        if (cmd in commands) {commands[cmd]();}
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
        case KEYCODE.T        : player.update_progress(player.get_state().progress + 1); break; // add
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
