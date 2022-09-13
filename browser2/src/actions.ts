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
                title: "Removing track...",
                function: "queue/"+queue_item_id.toString()+"/item",
                state: state,
                options: {
                    method: "DELETE",
                },
            }),
        ];
