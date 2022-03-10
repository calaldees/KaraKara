/// <reference path='./browser.d.ts'/>
import Cookies from 'js-cookie'
import { app } from "hyperapp";
import { HashStateManager } from "@shish2k/hyperapp-hash-state";
import { SurviveHMR } from "@shish2k/hyperapp-survive-hmr";
import {
    LocalStorageLoader,
    LocalStorageSaver,
} from "@shish2k/hyperapp-localstorage";

import { Root } from "./screens/root";
import { getMQTTListener, ResizeListener } from "./subs";
import { AutoLogin } from "./effects";
import { is_logged_in } from "./utils";

// If we're running stand-alone, then use the main karakara.uk
// server; else we're probably running as part of the full-stack,
// in which case we should use server we were loaded from.
const auto_root =
    window.location.pathname == "/"
        ? "https://karakara.uk"
        : window.location.protocol + "//" + window.location.host;

function isWidescreen() {
    return window.innerWidth > 780 && window.innerWidth > window.innerHeight;
}

let state: State = {
    // bump this each time the schema changes to
    // invalidate anybody's saved state
    version: 1,

    // global
    root: auto_root,
    root_edit: auto_root,
    screen: "explore",
    notification: null,
    priority_token: null,
    show_settings: false,
    download_size: null,
    download_done: 0,
    booth: false,
    widescreen: isWidescreen(),
    scroll_stack: [],

    // login
    session_id: null,
    room_name: "",
    room_password: "",
    room_password_edit: "",
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

function _cookieListener(dispatch, props) {
    let oldCookieVal: string | null = null;
    let cookieTimer = setInterval(function() {
        let cookieVal = Cookies.get(props.name);
        if(cookieVal != oldCookieVal) {
            oldCookieVal = cookieVal;
            console.log(props.name + " has new cookie val: " + cookieVal);
            dispatch(props.callback, cookieVal);
        }
    }, 1000);
    return function() {
        clearInterval(cookieTimer);
    };
}
function CookieListener(name, callback) {
    return [_cookieListener, {name: name, callback: callback}];
}

const subscriptions = (state: State): Array<Subscription> => [
    HashStateManager(
        {
            push: ["root", "filters", "track_id", "room_name"],
            replace: ["search", "booth", "widescreen"],
        },
        state,
    ),
    is_logged_in(state) && getMQTTListener(state),
    LocalStorageSaver("performer_name", state.performer_name),
    LocalStorageSaver("room_password", state.room_password),
    LocalStorageSaver("bookmarks", state.bookmarks),
    ResizeListener((state, event) => ({
        ...state,
        widescreen: isWidescreen(),
    })),
    CookieListener("priority_token", (state, cookie) => ({
        ...state,
        priority_token: cookie ? JSON.parse(cookie) : null,
    })),
];

app({
    init: [
        state,
        LocalStorageLoader("performer_name", (state, x) => ({
            ...state,
            performer_name: x,
        })),
        LocalStorageLoader("room_password", (state, x) => ({
            ...state,
            room_password_edit: x,
            room_password: x,
        })),
        LocalStorageLoader("bookmarks", (state, x) => ({
            ...state,
            bookmarks: x,
        })),
        SurviveHMR(module, [
            AutoLogin(),
        ]),
    ],
    view: Root,
    subscriptions: subscriptions,
    node: document.body,
});
