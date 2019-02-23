import { app } from "hyperapp";
import ReconnectingWebSocket from "reconnecting-websocket";
import queryString from 'query-string';

import { state, actions } from "./state";
import { view } from "./view";
import {get_protocol, get_hostname, get_ws_port, get_queue_id} from "./util";

const player = app(state, actions, view, document.body);
window.player = player; // make this global for debugging


// ====================================================================
// Network controls
// ====================================================================

function create_websocket() {
    const websocket_url = (
        (get_protocol() === "http:" ? 'ws://' : 'wss://') +
        get_hostname() + get_ws_port() +
        "/ws/"
		// "?queue_id=" + get_queue_id()
    );
    console.log("setup_websocket", websocket_url);

    const socket = new ReconnectingWebSocket(websocket_url);
    socket.onopen = function() {
        console.log("websocket_onopen()");
        player.set_connected(true);
        // player.send("ping"); // auth doesn't actually happen until the first packet
        // now that we're connected, make sure state is in
        // sync for the websocket to send incremental updates
        player.check_settings();
        player.check_queue();
    };
    socket.onclose = function() {
        console.log("websocket_onclose()");
        player.set_connected(false);
    };
    socket.onmessage = function(msg) {
        const cmd = msg.data.trim();
        console.log("websocket_onmessage("+ cmd +")");
        const commands = {
            "skip": () => player.send_ended('skipped'),  // Skip action requires the player to send the ended signal to poke the correct api endpoint. This feel ineligant fix. Advice please.
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
    return socket;
}
player.set_socket(create_websocket());


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
        default: handled = false;
    }
    if (handled) {
        e.preventDefault();
    }
};


// ====================================================================
// Auto-play for podium mode
// ====================================================================

const FPS = 5;
setInterval(
    function() {
        let state = player.get_state();
        if(state.paused || !state.audio_allowed) return;

        // if we're waiting for a track to start, and autoplay
        // is enabled, show a countdown
        if(!state.playing && state.settings["karakara.player.autoplay"] !== 0) {
            if(state.progress >= state.settings["karakara.player.autoplay"]) {player.send("play");}
            else {player.set_progress(state.progress + 1/FPS);}
        }

        // if we're playing, but we don't have a video,
        // let's simulate video progress happening
        if(state.playing && queryString.parse(location.hash).podium) {
            if(state.progress >= state.queue[0].track.duration) {player.dequeue();}
            else {player.set_progress(state.progress + 1/FPS);}
        }
    },
    1000/FPS
);
