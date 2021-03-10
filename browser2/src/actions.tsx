/*
 * Actions: functions which modify app state
 */
import {
    ApiRequest,
    SendCommand,
    LoginThenFetchTrackList,
    FetchTrackList,
} from "./effects";

/*
 * App navigation
 */
export const GoToScreen = (screen: string) => (state: State) =>
    ({ ...state, screen } as State);

export const ClearNotification = () => (state: State) =>
    ({ ...state, notification: null } as State);

export const ShowSettings = () => (state: State) =>
    ({ ...state, show_settings: true } as State);

export const HideSettings = () => (state: State) =>
    ({
        ...state,
        show_settings: false,
    } as State);
export const SelectTrack = (track_id: string | null) => (state: State) =>
    ({ ...state, track_id } as State);

export const TryLogin = () => (state: State) => [
    state,
    state.room_password
        ? LoginThenFetchTrackList(state)
        : FetchTrackList(state),
];

/*
 * User inputs
 */
export const SetPerformerName = () => (state: State, event: FormInputEvent) =>
    ({
        ...state,
        performer_name: event.target.value,
    } as State);

export const UpdateRoomName = () => (state: State, event: FormInputEvent) =>
    ({
        ...state,
        room_name_edit: event.target.value.toLowerCase(),
    } as State);

export function UpdateSettings(state: State, event) {
    state.settings[event.target.name] = event.target.value;
    return state;
}

/*
 * Player controls
 */
export const Command = (command: string) => (state: State) => [
    state,
    SendCommand(state, command),
];

/*
 * Add / remove tracks
 */
export const ActivateEnqueue = () => (state: State, event: FormInputEvent) =>
    ({
        ...state,
        action: "enqueue",
    } as State);

export const CancelEnqueue = () => (state: State, event: FormInputEvent) =>
    ({
        ...state,
        action: null,
    } as State);

export const EnqueueCurrentTrack = () => (state: State) => [
    state,
    ApiRequest({
        title: "Adding to queue...",
        function: "queue_items",
        state: state,
        options: {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                track_id: state.track_id || "error",
                performer_name: state.performer_name,
            }),
        },
        action: (state, response) => [{ ...state, action: null }],
    }),
];

export const RemoveTrack = (queue_item_id: number) => (state: State) => [
    state,
    ApiRequest({
        title: "Removing track...",
        function: "queue_items",
        state: state,
        options: {
            method: "DELETE",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                "queue_item.id": queue_item_id.toString(),
            }),
        },
    }),
];

/*
 * Bookmarks
 */
export const AddBookmark = (track_id: string) => (
    state: State,
    event: FormInputEvent,
) =>
    ({
        ...state,
        bookmarks: state.bookmarks.concat([track_id]),
    } as State);

export const RemoveBookmark = (track_id: string) => (
    state: State,
    event: FormInputEvent,
) =>
    ({
        ...state,
        bookmarks: state.bookmarks.filter((x) => x != track_id),
    } as State);
