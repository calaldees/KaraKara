import h from "hyperapp-jsx-pragma";
import { TitleScreen } from "./title";
import { VideoScreen } from "./video";
import { PodiumScreen } from "./podium";
import { SettingsMenu } from "./settings";
import { PreviewScreen } from "./preview";

export function Root(state: State) {
    let screen = <section>Unknown state :(</section>;

    if (!state.audio_allowed && !state.podium)
        // podium doesn't play sound
        screen = (
            <section key="title" class={"screen_title"}>
                <h1>Click to Activate</h1>
            </section>
        );
    else if (!state.room_name) screen = (
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

    return (
        <body
            onclick={(state) => ({ ...state, audio_allowed: true })}
            ondblclick={(state) => ({ ...state, show_settings: true })}
        >
            <main class={"theme-" + state.settings["karakara.player.theme"]}>
                {(!state.room_name || state.connected) || (
                    <h1 id={"error"}>Not Connected To Server</h1>
                )}
                {screen}
            </main>
            {state.show_settings && <SettingsMenu state={state} />}
        </body>
    );
}
