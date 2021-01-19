/// <reference path='./browser.d.ts'/>
import { app } from "hyperapp";
import h from "hyperapp-jsx-pragma";
import { MQTTSubscribe } from "hyperapp-mqtt";
import { AutoHistory } from "hyperapp-auto-history";
import { SaveStateManager } from "./save_state";

import {
    Login,
    TrackExplorer,
    TrackDetails,
    Queue,
    Control,
    SettingsMenu,
    refresh
} from "./screens";
import { http2ws } from "./utils";

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
    queue_id: null,
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
};
const ssm = new SaveStateManager(state, [
    "performer_name",
    "queue_id",
    "queue_password",
    "bookmarks",
]);

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
    } else if (state.screen == "control") {
        body = <Control state={state} />;
    } else if (state.screen == "queue") {
        body = <Queue state={state} />;
    }
    return <body>
        {body}
        {state.show_settings && <SettingsMenu state={state} />}
    </body>;
}

const HistoryManager = AutoHistory({
    init: state,
    push: ["root", "queue_id", "filters", "track_id"],
    replace: ["search"],
});

let mySubs = {};

function getOpenMQTTListener(state: State): MQTTSubscribe {
    let url = http2ws(state.root) + "/mqtt";
    if (!mySubs[url]) {
        mySubs[url] = MQTTSubscribe({
            url: url,
            topic: "karakara/queue/" + state.queue_id,
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
    return [HistoryManager, state.queue_id && getOpenMQTTListener(state)];
}

app({
    init: state,
    view: view,
    subscriptions: subscriptions,
    node: document.body,
});
