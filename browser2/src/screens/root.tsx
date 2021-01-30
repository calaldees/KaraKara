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

export function Root(state: State) {
    let body = null;
    // room_name can be set from saved state, but then track_list will be empty,
    // so push the user back to login screen if that happens (can we load the
    // track list on-demand somehow?)
    if (state.room_name === "" || Object.keys(state.track_list).length === 0) {
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
            body = <TrackList state={state} />;
        }
    } else if (state.screen == "control") {
        body = <Control state={state} />;
    } else if (state.screen == "queue") {
        body = <Queue state={state} />;
    } else if (state.screen == "printable_list") {
        body = <PrintableList state={state} />;
    } else if (state.screen == "room_settings") {
        body = <RoomSettings state={state} />;
    } else if (state.screen == "priority_tokens") {
        body = <PriorityTokens state={state} />;
    }
    return <body>
        {body}
        {state.show_settings && <SettingsMenu state={state} />}
    </body>;
}