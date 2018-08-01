import { app } from "hyperapp";
import { state, actions } from "./state";
import { view } from "./view";
import { get_protocol, get_hostname } from "./util";

const player = app(state, actions, view, document.body);


// ====================================================================
// Initial connect & sync
// ====================================================================

player.check_settings();
player.check_queue();


// ====================================================================
// Network controls
// ====================================================================

// TODO: onended = dequeue() + report completion to server
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
        (get_protocol() === "http:" ? 'ws://' : 'wss://') +
        get_hostname() +
        ((ws_port && !ws_path) ? ":" + ws_port : "") +
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
        // now that we're connected, make sure state is in
        // sync for the websocket to send incremental updates
        player.check_settings();
        player.check_queue();
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
            "pause": player.pause,
            "seek_forwards": player.seek_forwards,
            "seek_backwards": player.seek_backwards,
            "ended": player.dequeue,
            "queue_updated": player.check_queue,
            "settings": player.check_settings,
        };
        if (cmd in commands) {commands[cmd]();}
        else {console.log("unknown command: " + cmd)}
    };
}


// ====================================================================
// Local controls
// ====================================================================

document.onkeydown = function(e) {
    let handled = true;
    switch (e.key) {
        case "s"          : player.dequeue(); break; // skip
        //case "a"          : player.enqueue(); break; // add
        case "Enter"      : player.play(); break;
        case "Escape"     : player.stop(); break;
        case "ArrowLeft"  : player.seek_backwards(); break;
        case "ArrowRight" : player.seek_forwards(); break;
        case "Space"      : player.pause(); break;
        case "u"          : player.check_settings(); player.check_queue(); break; // update
        default: handled = false;
    }
    if (handled) {
        e.preventDefault();
    }
};


// ====================================================================
// Auto-play for podium mode
// ====================================================================

if(window.location.hash === "#podium") {
    const FPS = 5;
    setInterval(
        function() {
            let state = player.get_state();
            if(!state.playing) {
                if(state.settings["karakara.player.autoplay"] === 0) return;
                if(state.progress >= state.settings["karakara.player.autoplay"]) {player.play();}
                else {player.set_progress(state.progress + 1/FPS);}
            }
            else {
                if(state.progress >= state.queue[0].track.duration) {player.stop();}
                else {player.set_progress(state.progress + 1/FPS);}
            }
        },
        1000/FPS
    );
}
