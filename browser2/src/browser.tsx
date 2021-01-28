/// <reference path='./browser.d.ts'/>
import { app } from "hyperapp";
import { MQTTSubscribe } from "hyperapp-mqtt";
import { AutoHistory } from "hyperapp-auto-history";
import { SaveStateManager } from "./save_state";

import { http2ws } from "./utils";
import { refresh } from "./screens/base";
import { Root } from "./screens/root";

// If we're running stand-alone, then use the main karakara.org.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.org.uk"
        : window.location.protocol + "//" + window.location.host;

let state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: auto_root,
    screen: "explore",
    notification: null,
    show_settings: false,

    // login
    tmp_queue_id: "",
    queue_id: "",
    queue_password: "",
    loading: false,

    // track list
    track_list: {},
    search: "",
    filters: [],
    expanded: null,

    // track
    track_id: null,
    performer_name: "",
    action: null,

    // queue
    queue: [],
    drop_source: null,
    drop_target: null,

    // bookmarks
    bookmarks: [],

    // settings
    settings: {},

    // priority_tokens
    priority_tokens: [],
};
const ssm = new SaveStateManager(state, [
    "performer_name",
    "queue_password",
    "bookmarks",
]);

const HistoryManager = AutoHistory({
    init: state,
    push: ["root", "filters", "track_id"],
    replace: ["tmp_queue_id", "search"],
});

let mySubs = {};

function getOpenMQTTListener(state: State): MQTTSubscribe {
    let url = http2ws(state.root) + "/mqtt";
    if (!mySubs[url]) {
        mySubs[url] = MQTTSubscribe({
            url: url,
            options: state.queue_password ? {username: state.queue_id, password: state.queue_password} : {},
            topic: "karakara/room/" + state.queue_id + "/commands",
            connect(state: State) {
                return refresh(state);
            },
            close(state: State) {
                // delete mySubs[url];
                return { ...state };
            },
            message(state: State, msg) {
                return refresh(state);
            },
        });
    }
    return mySubs[url];
}

function subscriptions(state: State) {
    ssm.save_state_if_changed(state);
    HistoryManager.push_state_if_changed(state);
    return [HistoryManager, state.queue_id && state.track_list && getOpenMQTTListener(state)];
}

app({
    init: state,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
