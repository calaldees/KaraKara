import h from "hyperapp-jsx-pragma";
import { current_and_future, percent, s_to_mns } from "../utils";
import { Video } from "./_common";
import { SendCommand } from "../effects";

///////////////////////////////////////////////////////////////////////
// Views

const ProgressBar = ({
    now,
    start_time,
    duration,
}: {
    now: number;
    start_time: number;
    duration: number;
}): VNode => (
    <div
        class={"progressBar"}
        style={{
            "background-position": percent(
                duration - (now - start_time),
                duration,
            ),
        }}
    >
        Track Playing
        <small>
            ({s_to_mns(now - start_time)} / {s_to_mns(duration)})
        </small>
    </div>
);

const AutoplayBar = ({
    now,
    start_time,
    track_space,
}: {
    now: number;
    start_time: number;
    track_space: number;
}): VNode => (
    <div
        class={"startButton"}
        onclick={(state) => [state, SendCommand(state, "play")]}
        style={{
            "background-position": percent(start_time - now, track_space),
        }}
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

export const PodiumScreen = ({
    state,
    track,
    queue_item,
}: {
    state: State;
    track: Track;
    queue_item: QueueItem;
}): VNode => (
    <section key="podium" class={"screen_podium"}>
        <h1>
            {track.tags.title[0]}
            <br />
            Performed by <strong>{queue_item.performer_name}</strong>
        </h1>

        <Video
            state={state}
            track={track}
            muted={true}
            lowres={true}
            // ensure the video element gets re-created when switching
            // between queue items (even if it's the same track), and
            // also when the podium switches from "preview" to "play" mode
            key={
                queue_item.id +
                "-" +
                (queue_item.start_time && queue_item.start_time < state.now)
            }
        />

        {queue_item.start_time ? (
            queue_item.start_time < state.now ? (
                <ProgressBar
                    now={state.now}
                    start_time={queue_item.start_time}
                    duration={track.duration}
                />
            ) : (
                <AutoplayBar
                    now={state.now}
                    start_time={queue_item.start_time}
                    track_space={state.settings["track_space"]}
                />
            )
        ) : (
            <StartBar />
        )}
    </section>
);
