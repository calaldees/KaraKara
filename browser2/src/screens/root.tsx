import h from "hyperapp-jsx-pragma";

import { Login } from "./login";
import { TrackList } from "./track_list";
import { TrackDetails } from "./track_details";
import { Queue } from "./queue";
import { Control } from "./control";
import { SettingsMenu } from "./settings";
import { PrintableList } from "./printable_list";
import { RoomSettings } from "./room_settings";
import { PriorityTokens } from "./priority_tokens";
import { is_logged_in } from "../utils";

export const QueueOrControl = ({ state }: { state: State }): VNode =>
    state.room_password ? <Control state={state} /> : <Queue state={state} />;

export const Explore = ({ state }: { state: State }): VNode =>
    state.track_id ? (
        <TrackDetails state={state} track={state.track_list[state.track_id]} />
    ) : (
        <TrackList state={state} />
    );

export function Root(state: State): VNode {
    let body = null;
    if (!is_logged_in(state)) {
        body = <Login state={state} />;
    } else if (state.screen == "printable_list") {
        body = <PrintableList state={state} />;
    } else {
        let active_screen = null;
        if (state.screen == "explore") {
            active_screen = <Explore state={state} />;
        } else if (state.screen == "queue") {
            active_screen = <QueueOrControl state={state} />;
        } else if (state.screen == "room_settings") {
            active_screen = <RoomSettings state={state} />;
        } else if (state.screen == "priority_tokens") {
            active_screen = <PriorityTokens state={state} />;
        }

        if (state.widescreen) {
            body = (
                <div class={"widescreen"}>
                    <QueueOrControl state={state} />
                    {active_screen}
                </div>
            );
        } else {
            body = active_screen;
        }
    }
    return (
        <body>
            {body}
            {state.show_settings && <SettingsMenu state={state} />}
        </body>
    );
}
