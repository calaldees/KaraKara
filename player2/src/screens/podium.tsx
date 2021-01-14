import h from "hyperapp-jsx-pragma";
import { get_attachment, get_tag, s_to_mns, title_case } from "../utils";
import { Lyrics, AutoplayCountdown } from "./common";
import { Dequeue, Stop, UpdatePodiumProgress } from "../actions";
import { SendCommand } from "../effects";

export const PodiumScreen = ({ state }: { state: State }) => (
    <section
        key="podium"
        className={
            "screen_podium" +
            (state.queue[0].track.srt_lyrics ? "" : " no_lyrics")
        }
    >
        <h1>
            {title_case(get_tag(state.queue[0].track.tags.title))}
            <br />
            Performed by <strong>{state.queue[0].performer_name}</strong>
        </h1>

        {/*
        Give the video key=playing so that it creates a new
        object when switching from preview to play
         */}
        <div className="preview_holder">
            <video
                src={get_attachment(state, state.queue[0].track, "preview")}
                ontimeupdate={UpdatePodiumProgress}
                onended={state.playing ? Dequeue : Stop}
                autoPlay={true}
                muted={true}
                key={state.playing}
            />
        </div>
        <Lyrics state={state} />

        {state.playing ? (
            <div
                className={"progressBar"}
                style={{
                    "background-position":
                        100 -
                        (state.progress / state.queue[0].track.duration) * 100 +
                        "%",
                }}
            >
                Track Playing
                <small>
                    ({s_to_mns(state.progress)} /{" "}
                    {s_to_mns(state.queue[0].track.duration)})
                </small>
            </div>
        ) : (
            <div
                className={"startButton"}
                onclick={state => [state, SendCommand(state, "play")]}
                style={{
                    "background-position":
                        100 -
                        (state.progress /
                            state.settings["karakara.player.autoplay"]) *
                            100 +
                        "%",
                }}
            >
                <span>
                    Press to Start
                    <AutoplayCountdown state={state} show_if_disabled={true} />
                </span>
            </div>
        )}
    </section>
);
