/*
 * Actions: functions which take app state as input,
 * and return modified state (optionally including
 * side effects) as output
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
export const GoToScreen =
    (screen: string) =>
    (state: State): Action => ({
        ...state,
        screen,
    });

export const ClearNotification =
    () =>
    (state: State): Action => ({
        ...state,
        notification: null,
    });

export const ShowSettings =
    () =>
    (state: State): Action => ({
        ...state,
        show_settings: true,
    });

export const HideSettings =
    () =>
    (state: State): Action => ({
        ...state,
        show_settings: false,
    });

export const SelectTrack =
    (track_id: string | null) =>
    (state: State): Action => ({ ...state, track_id });

export const TryLogin =
    () =>
    (state: State): Action =>
        [
            state,
            state.room_password
                ? LoginThenFetchTrackList(state)
                : FetchTrackList(state),
        ];

/*
 * User inputs
 */
export const SetPerformerName =
    () =>
    (state: State, event: FormInputEvent): Action => ({
        ...state,
        performer_name: event.target.value,
    });

export const UpdateRoomName =
    () =>
    (state: State, event: FormInputEvent): Action => ({
        ...state,
        room_name_edit: event.target.value.toLowerCase(),
    });

export function UpdateSettings(state: State, event: FormInputEvent): Action {
    if (Array.isArray(state.settings[event.target.name])) {
        state.settings[event.target.name] = event.target.value.split(",");
    } else {
        state.settings[event.target.name] = event.target.value;
    }
    return state;
}

/*
 * Player controls
 */
export const Command =
    (command: string) =>
    (state: State): Action =>
        [state, SendCommand(state, command)];

/*
 * Add / remove tracks
 */
export const ActivateEnqueue =
    () =>
    (state: State): Action => ({
        ...state,
        action: "enqueue",
    });

export const CancelEnqueue =
    () =>
    (state: State): Action => ({
        ...state,
        action: null,
    });

export const EnqueueCurrentTrack =
    () =>
    (state: State): Action =>
        [
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

export const RemoveTrack =
    (queue_item_id: number) =>
    (state: State): Action =>
        [
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
export const AddBookmark =
    (track_id: string) =>
    (state: State): Action => ({
        ...state,
        bookmarks: state.bookmarks.concat([track_id]),
    });

export const RemoveBookmark =
    (track_id: string) =>
    (state: State): Action => ({
        ...state,
        bookmarks: state.bookmarks.filter((x) => x != track_id),
    });
