import h from "hyperapp-jsx-pragma";
import { s_to_mns } from "../utils";
import { AutoplayCountdown, Video } from "./_common";
import { SendCommand } from "../effects";


///////////////////////////////////////////////////////////////////////
// Views

export const PodiumScreen = ({ state }: { state: State }): VNode => (
    <PodiumInternal
        state={state}
        track={state.track_list[state.queue[0].track_id]}
        queue_item={state.queue[0]}
    />
);

const ProgressBar = ({now, start_time, duration}: {now: number, start_time: number, duration: number}): VNode => (
    <div
        class={"progressBar"}
        style={{
            "background-position":
                100 -
                ((now - start_time) / duration) * 100 +
                "%",
        }}
    >
        Track Playing
        <small>
            ({s_to_mns(now - start_time)} /{" "}
            {s_to_mns(duration)})
        </small>
    </div>
);

const AutoplayBar = ({now, start_time, track_space}: {now: number, start_time: number, track_space: number}): VNode => (
    <div
        class={"startButton"}
        onclick={(state) => [state, SendCommand(state, "play")]}
        style={{
            "background-position":
                100 -
                ((start_time - now) / track_space) *
                100 +
                "%",
        }}
    >
        <span>
            Track starts in {s_to_mns(start_time - now)}
        </span>
    </div>
);

const StartBar = (): VNode => (
    <div
        class={"startButton"}
        onclick={(state) => [state, SendCommand(state, "play")]}
    >
        <span>
            Press to Start
        </span>
    </div>
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
                autoPlay={true}
                muted={true}
            />
        </div>

        {state.queue[0].start_time ? (
            state.queue[0].start_time < state.now ? 
                <ProgressBar now={state.now} start_time={state.queue[0].start_time} duration={track.duration} /> :
                <AutoplayBar now={state.now} start_time={state.queue[0].start_time} track_space={state.settings["track_space"]} />
        ) : (
            <StartBar />
        )}
    </section>
);
