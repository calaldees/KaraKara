import h from "hyperapp-jsx-pragma";
import { attachment_path, get_tag, s_to_mns } from "../utils";
import { AutoplayCountdown } from "./common";
import { Dequeue, Stop, UpdatePodiumProgress } from "../actions";
import { SendCommand } from "../effects";

export const PodiumScreen = ({ state }: { state: State }): VNode => (
    <PodiumInternal
        state={state}
        track={state.track_list[state.queue[0].track_id]}
        queue_item={state.queue[0]}
    />
);

const PodiumInternal = ({ state, track, queue_item }: { state: State, track: Track, queue_item: QueueItem }): VNode => (
    <section
        key="podium"
        class={"screen_podium"}
    >
        <h1>
            {get_tag(track.tags.title)}
            <br />
            Performed by <strong>{queue_item.performer_name}</strong>
        </h1>

        {/*
        Give the video key=playing so that it creates a new
        object when switching from preview to play
         */}
        <div class="preview_holder">
            <video
                ontimeupdate={UpdatePodiumProgress}
                onended={state.playing ? Dequeue : Stop}
                autoPlay={true}
                muted={true}
                key={state.playing}
            >
                {track.attachments.video.map(a =>
                    <source src={attachment_path(state.root, a)} type={a.mime} />
                )}
                {track.attachments.subtitle?.map(a =>
                    <track
                        kind="subtitles"
                        src={attachment_path(state.root, a)}
                        default={true}
                        label="English"
                        srclang="en"
                    />
                )}
            </video>
        </div>

        {state.playing ? (
            <div
                class={"progressBar"}
                style={{
                    "background-position":
                        100 -
                        (state.progress / track.duration) * 100 +
                        "%",
                }}
            >
                Track Playing
                <small>
                    ({s_to_mns(state.progress)} /{" "}
                    {s_to_mns(track.duration)})
                </small>
            </div>
        ) : (
            <div
                class={"startButton"}
                onclick={(state) => [state, SendCommand(state, "play")]}
                style={{
                    "background-position":
                        100 -
                        (state.progress /
                            state.settings[
                            "karakara.player.autoplay.seconds"
                            ]) *
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
