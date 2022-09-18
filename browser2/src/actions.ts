/*
 * Actions: functions which take app state as input,
 * and return modified state (optionally including
 * side effects) as output
 */
import { ApiRequest } from "./effects";

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
                // only used when going to settings screen
                settings_edit: state.settings,
            },
            ...effects,
        ];

/*
 * Add / remove tracks
 */
export const RemoveTrack =
    (queue_item_id: number): Action =>
    (state: State): Dispatchable =>
        [
            state,
            ApiRequest({
                notify: "Removing track...",
                notify_ok: "Track removed!",
                function: "queue/"+queue_item_id.toString(),
                state: state,
                options: {
                    method: "DELETE",
                },
            }),
        ];
