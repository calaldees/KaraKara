import h from "hyperapp-jsx-pragma";
import { TitleScreen } from "./title";
import { VideoScreen } from "./video";
import { PodiumScreen } from "./podium";
import { SettingsMenu } from "./settings";
import { PreviewScreen } from "./preview";
import { current_and_future, percent } from "../utils";

export function Root(state: State): VNode {
    let screen = <section>Unknown state :(</section>;
    let visible_queue = current_and_future(state.now, state.queue);

    if (state.download_size)
        screen = (
            <section key="title" class={"screen_title"}>
                <h1>
                    Loading {percent(state.download_done, state.download_size)}
                </h1>
            </section>
        );
    else if (!state.audio_allowed && !state.podium)
        // podium doesn't play sound
        screen = (
            <section key="title" class={"screen_title"}>
                <h1>Click to Activate</h1>
            </section>
        );
    else if (!state.room_name)
        screen = (
            <section key="title" class={"screen_title"}>
                <h1>KaraKara</h1>
            </section>
        );
    else if (visible_queue.length === 0) screen = <TitleScreen state={state} />;
    else if (state.podium)
        screen = (
            <PodiumScreen
                state={state}
                track={state.track_list[visible_queue[0].track_id]}
                queue_item={visible_queue[0]}
            />
        );
    else if (
        visible_queue[0].start_time == null ||
        visible_queue[0].start_time > state.now
    )
        screen = (
            <PreviewScreen
                state={state}
                track={state.track_list[visible_queue[0].track_id]}
                queue={visible_queue}
            />
        );
    else
        screen = (
            <VideoScreen
                state={state}
                track={state.track_list[visible_queue[0].track_id]}
                queue_item={visible_queue[0]}
            />
        );

    let errors: Array<string> = [];
    if (!state.room_name) errors.push("No Room Set");
    if (!state.connected) errors.push("Not Connected");
    if (!state.is_admin) errors.push("Not Admin");
    if (Object.keys(state.track_list).length == 0) errors.push("No Tracks");

    return (
        <body
            onclick={(state: State) => ({ ...state, audio_allowed: true })}
            ondblclick={(state: State) => ({ ...state, show_settings: true })}
        >
            <main class={"theme-" + state.settings["theme"]}>
                {errors.length > 0 && <h1 id={"error"}>{errors.join(", ")}</h1>}
                {screen}
            </main>
            {state.show_settings && <SettingsMenu state={state} />}
        </body>
    );
}
