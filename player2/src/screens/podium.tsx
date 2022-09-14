import h from "hyperapp-jsx-pragma";
import { current_and_future, percent, s_to_mns } from "../utils";
import { Video } from "./_common";
import { SendCommand } from "../effects";


///////////////////////////////////////////////////////////////////////
// Views

export const PodiumScreen = ({ state }: { state: State }): VNode => (
    <PodiumInternal
        state={state}
        track={state.track_list[current_and_future(state.now, state.queue)[0].track_id]}
        queue_item={current_and_future(state.now, state.queue)[0]}
    />
);

const ProgressBar = ({now, start_time, duration}: {now: number, start_time: number, duration: number}): VNode => (
    <div
        class={"progressBar"}
        style={{"background-position": percent(duration - (now - start_time), duration)}}
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
        style={{"background-position": percent(start_time - now, track_space)}}
    >
        <span>
            Press to Start
            <small>Track autoplays in {s_to_mns(start_time - now)}</small>
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
            <small>Autoplay Disabled</small>
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

        {queue_item.start_time ? (
            queue_item.start_time < state.now ?
                <ProgressBar now={state.now} start_time={queue_item.start_time} duration={track.duration} /> :
                <AutoplayBar now={state.now} start_time={queue_item.start_time} track_space={state.settings["track_space"]} />
        ) : (
            <StartBar />
        )}
    </section>
);
