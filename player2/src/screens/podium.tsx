import h from "hyperapp-jsx-pragma";
import { s_to_mns } from "../utils";
import { AutoplayCountdown, Video } from "./_common";
import { Dequeue, Stop } from "../actions";
import { SendCommand } from "../effects";


///////////////////////////////////////////////////////////////////////
// Actions

function UpdatePodiumProgress(state: State, event): Dispatchable {
    if (state.playing) return { ...state, progress: event.target.currentTime };
    return state;
}


///////////////////////////////////////////////////////////////////////
// Views

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
            {track.tags.title[0]}
            <br />
            Performed by <strong>{queue_item.performer_name}</strong>
        </h1>

        <div class="preview_holder">
            <Video
                state={state}
                track={track}
                ontimeupdate={UpdatePodiumProgress}
                onended={state.playing ? Dequeue : Stop}
                autoPlay={true}
                muted={true}
            />
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
