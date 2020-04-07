/// <reference path='./browser.d.ts'/>
import { app, h } from "hyperapp";
import { WebSocketListen } from "hyperapp-fx";
import { AutoHistory } from "hyperapp-auto-history";
import ReconnectingWebSocket from "reconnecting-websocket";

import { Login, TrackExplorer, TrackDetails, Queue, refresh } from "./screens";
import { http2ws } from "./utils";

const state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: "https://karakara.org.uk",
    screen: "explore",
    notification: null,

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

function subscriptions(state: State) {
    HistoryManager.push_state_if_changed(state);
    return [
        HistoryManager,
        state.queue_id &&
            WebSocketListen({
                url: http2ws(state.root) + "/" + state.queue_id + ".ws",
                action: (state, response) => refresh(state),
                ws_constructor: ReconnectingWebSocket,
            }),
    ];
}

app({
    init: state,
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
