/// <reference path='./player.d.ts'/>
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import { SyncedInterval } from "@shish2k/hyperapp-synced-interval";
import {
    LocalStorageLoader,
    LocalStorageSaver,
} from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import { getMQTTListener, KeyboardListener, BeLoggedIn, WakeLock } from "./subs";
import { ApiRequest } from "./effects";
import { current_and_future } from "./utils";

// If we're running stand-alone, then use the main karakara.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.uk"
        : window.location.protocol + "//" + window.location.host;

const state: State = {
    // global
    root: auto_root,
    root_edit: auto_root,
    room_name: "",
    room_name_edit: "",
    room_password: "",
    room_password_edit: "",
    podium: false,
    track_list: {},
    is_admin: false,
    show_settings: false,
    connected: false,
    fullscreen: false,
    audio_allowed:
        window.AudioContext == undefined ||
        new AudioContext().state === "running",
    settings: {
        title: "KaraKara",
        theme: "metalghosts",
        preview_volume: 0.2,
        track_space: 10,
        validation_event_end_datetime: null,
    },
    now: Date.now() / 1000,
    notification: null,
    wake_lock: {
        held: false,
        status: "default",
    },

    // loading screen
    download_size: null,
    download_done: 0,

    // playlist screen
    queue: [],
};

const init: Dispatchable = [
    state,
    LocalStorageLoader("room_password", (state, x) => ({
        ...state,
        room_password_edit: x,
        room_password: x,
    })),
    ApiRequest({
        url: `${state.root}/files/tracks.json`,
        options: {
            credentials: "omit",
        },
        state: state,
        progress: (state, { done, size }): State => ({
            ...state,
            download_done: done,
            download_size: size,
        }),
        action: (state, response: Dictionary<Track>): State => ({
            ...state,
            track_list: response,
            download_done: 0,
            download_size: null,
        }),
        exception: (state, error): State => ({
            ...state,
        }),
    }),
];

function syncVideo(state: State) {
    let movie: HTMLVideoElement = document.getElementsByTagName(
        "VIDEO",
    )[0] as HTMLVideoElement;
    let visible_queue = current_and_future(state.now, state.queue);
    if (movie && visible_queue.length > 0) {
        let queue_item = visible_queue[0];
        if (queue_item.start_time && queue_item.start_time < state.now) {
            let goal = state.now - queue_item.start_time;
            let diff = Math.abs(movie.currentTime - goal);
            // if our time is nearly-correct, leave it as-is
            if (diff > 3) {
                console.log(
                    `Time is ${movie.currentTime} and should be ${goal}`,
                );
                movie.currentTime = goal;
            }
        }
    }
}

const subscriptions = (state: State): Array<Subscription | boolean> => [
    HashStateManager(
        {
            push: ["root", "room_name"],
            replace: ["podium", "room_name_edit"],
        },
        state,
    ),
    LocalStorageSaver("room_password", state.room_password),
    KeyboardListener,
    getMQTTListener(state),
    BeLoggedIn(state.room_name, state.room_password),
    SyncedInterval({
        server: state.root + "/time.json",
        interval: 1000,
        sync: 5 * 60 * 1000,
        onInterval(state: State, timestamp_ms: number): Dispatchable {
            (window as any).state = state;
            syncVideo(state);
            return { ...state, now: timestamp_ms / 1000 };
        },
    }),
    WakeLock({
        onChange(state: State, {held, status}: {held: boolean, status: string}): Dispatchable {
            return {
                ...state, wake_lock: {
                    held,
                    status,
                }
            };
        }
    }),
];

app({
    init: init,
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
