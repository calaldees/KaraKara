import h from "hyperapp-jsx-pragma";
import { TitleScreen } from "./title";
import { VideoScreen } from "./video";
import { PodiumScreen } from "./podium";
import { SettingsMenu } from "./settings";
import { PreviewScreen } from "./preview";

function percent(a: number, b: number): string {
    return Math.round((a / b) * 100) + "%";
}

export function Root(state: State): VNode {
    let screen = <section>Unknown state :(</section>;

    if (state.download_size)
        screen = (
            <section key="title" class={"screen_title"}>
                <h1>Loading {percent(state.download_done, state.download_size)}</h1>
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
    else if (state.queue.length === 0) screen = <TitleScreen state={state} />;
    else if (state.podium) screen = <PodiumScreen state={state} />;
    else if (state.queue.length > 0 && !state.playing)
        screen = <PreviewScreen state={state} />;
    else if (state.queue.length > 0 && state.playing)
        screen = <VideoScreen state={state} />;

    let errors: Array<string> = [];
    if(!state.room_name) errors.push("No Room Set");
    if(!state.connected) errors.push("Not Connected");
    if(!state.is_admin) errors.push("Not Admin");

    return (
        <body
            onclick={(state) => ({ ...state, audio_allowed: true })}
            ondblclick={(state) => ({ ...state, show_settings: true })}
        >
            <main class={"theme-" + state.settings["theme"]}>
                {errors.length > 0 && <h1 id={"error"}>{errors.join(", ")}</h1>}
                {screen}
            </main>
            {state.show_settings && <SettingsMenu state={state} />}
        </body>
    );
}
