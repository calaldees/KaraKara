/// <reference path='./browser.d.ts'/>
import { app, h } from "hyperapp";
import { WebSocketListen } from "hyperapp-fx";
import { AutoHistory } from "hyperapp-auto-history";
import ReconnectingWebSocket from "reconnecting-websocket";

import { Login, TrackExplorer, TrackDetails, Queue, refresh } from "./screens";
import { http2ws } from "./utils";

// If we're running stand-alone, then use the main karakara.org.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.org.uk"
        : window.location.protocol + "//" + window.location.host;

const state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: auto_root,
    screen: "explore",
    notification: null,
    ws_errors: 0,

    // login
    tmp_queue_id: "test",
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

function view(state: State) {
    let body = null;
    // queue_id can be set from saved state, but then track_list will be empty,
    // so push the user back to login screen if that happens (can we load the
    // track list on-demand somehow?)
    if (state.queue_id === null || Object.keys(state.track_list).length === 0) {
        body = <Login state={state} />;
    } else if (state.screen == "explore") {
        if (state.track_id) {
            body = (
                <TrackDetails
                    state={state}
                    track={state.track_list[state.track_id]}
                />
            );
        } else {
            body = <TrackExplorer state={state} />;
        }
    } else if (state.screen == "queue") {
        body = <Queue state={state} />;
    }
    return <body>{body}</body>;
}

const HistoryManager = AutoHistory({
    init: state,
    push: ["root", "queue_id", "filters", "track_id"],
    replace: ["search"],
});

let mySubs = {};

function getOpenWebSocketListener(state: State): WebSocketListen {
    let url =
        http2ws(state.root) + "/" + state.queue_id + ".ws?_=" + state.ws_errors;
    if (!mySubs[url]) {
        mySubs[url] = WebSocketListen({
            url: url,
            open(state: State) {
                return refresh(state);
            },
            close(state: State) {
                delete mySubs[url];
                return {
                    ...state,
                    ws_error_count: state.ws_errors + 1,
                };
            },
            action(state: State, msg: MessageEvent) {
                return refresh(state);
            },
            error(state: State, response) {
                console.log("Error listening to websocket:", response);
                return { ...state, ws_error_count: state.ws_errors + 1 };
            },
        });
    }
    return mySubs[url];
}

function subscriptions(state: State) {
    HistoryManager.push_state_if_changed(state);
    return [HistoryManager, state.queue_id && getOpenWebSocketListener(state)];
}

app({
    init: state,
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
