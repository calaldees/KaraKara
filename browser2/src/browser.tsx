/// <reference path='./browser.d.ts'/>
import {app, h} from "hyperapp";
import {WebSocketListen} from "hyperapp-fx";
import ReconnectingWebSocket from "reconnecting-websocket";

import {Login, TrackExplorer, TrackDetails, Queue, refresh} from "./screens";
import {http2ws} from "./utils";

const state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: "https://karakara.org.uk",
    screen: "explore",
    notification: null,

    // login
    tmp_queue_id: "booth",
    queue_id: null,
    loading: false,

    // track list
    track_list: {},
    search: "",
    filters: [],
    expanded: null,

    // track
    track_id: null,
    performer_name: "Shish",
    action: null,

    // queue
    queue: [],

    // bookmarks
    bookmarks: [],
};

// Insert a new history entry whenever any of these change
const nav_state = {
    push: ["queue_id", "screen", "filters", "track_id"],
    replace: ["search"]
};

/*
let loaded_state: State = state;
try {
    let saved_state = JSON.parse(window.localStorage.getItem("state") || "{}");
    loaded_state = {...loaded_state, ...saved_state};
}
catch(err) {
    console.log("Error loading state:", err);
}
*/

function view(state: State) {
    let body = null;
    if (!state.queue_id) {
        body = <Login state={state} />;
    }
    else if (state.screen == "explore") {
        if (state.track_id) {
            body = <TrackDetails state={state} track={state.track_list[state.track_id]} />;
        }
        else {
            body = <TrackExplorer state={state} />;
        }
    }
    else if (state.screen == "queue") {
        body = <Queue state={state} />;
    }
    return <body>{body}</body>;
}

function subscriptions(state: State) {
    return [
        state.queue_id && WebSocketListen({
            url: http2ws(state.root) + "/ws/",
            action: (state, response) => refresh(state),
            ws_constructor: ReconnectingWebSocket
        }),
    ];
}

app({
    init: state,
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
