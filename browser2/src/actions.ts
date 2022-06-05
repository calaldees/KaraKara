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
    PushScrollPos,
    PopScrollPos,
} from "./effects";

/*
 * App navigation
 */

export const GoToScreen =
    (screen: string, effects: Array<Effect> = []): Action =>
    (state: State): Dispatchable =>
        [
            {
                ...state,
                screen,
            },
            ...effects,
        ];

export const ClearNotification =
    (): Action =>
    (state: State): Dispatchable => ({
        ...state,
        notification: null,
    });

export const ShowSettings =
    (): Action =>
    (state: State): Dispatchable => ({
        ...state,
        show_settings: true,
    });

export const SelectTrack =
    (track_id: string | null): Action =>
    (state: State): Dispatchable =>
        [
            { ...state, track_id },
            track_id ? PushScrollPos() : PopScrollPos(),
        ];

export const TryLogin =
    (): Action =>
    (state: State): Dispatchable =>
        [
            {
                ...state,
                room_name: state.room_name_edit.toLowerCase().trim(),
            },
            state.room_password
                ? LoginThenFetchTrackList(state)
                : FetchTrackList(state),
        ];

/*
 * User inputs
 */
export const SetPerformerName =
    (): Action =>
    (state: State, event: FormInputEvent): Dispatchable => ({
        ...state,
        performer_name: event.target.value,
    });

export function UpdateSettings(
    state: State,
    event: FormInputEvent,
): Dispatchable {
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
    (command: string): Action =>
    (state: State): Dispatchable =>
        [state, SendCommand(state, command)];

/*
 * Add / remove tracks
 */
export const ActivateEnqueue =
    (): Action =>
    (state: State): Dispatchable => ({
        ...state,
        action: "enqueue",
    });

export const CancelEnqueue =
    (): Action =>
    (state: State): Dispatchable => ({
        ...state,
        action: null,
    });

export const EnqueueCurrentTrack =
    (): Action =>
    (state: State): Dispatchable =>
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
    (queue_item_id: number): Action =>
    (state: State): Dispatchable =>
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
    (track_id: string): Action =>
    (state: State): Dispatchable => ({
        ...state,
        bookmarks: state.bookmarks.concat([track_id]),
    });

export const RemoveBookmark =
    (track_id: string): Action =>
    (state: State): Dispatchable => ({
        ...state,
        bookmarks: state.bookmarks.filter((x) => x != track_id),
    });
