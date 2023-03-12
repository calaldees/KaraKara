import h from "hyperapp-jsx-pragma";
import {
    attachment_path,
    current_and_future,
    percent,
    s_to_mns,
} from "../utils";
import { Video } from "./_common";
import { SendCommand } from "../effects";
import { delay } from "@hyperapp/time";

const StartAction = (state) => [
    { ...state, starting: true },
    SendCommand(state, "play"),
    delay(2000, (state) => ({ ...state, starting: false })),
];

///////////////////////////////////////////////////////////////////////
// Views

const StartingBar = (): VNode => (
    <div class={"startButton"}>
        <span>Starting Now!</span>
    </div>
);

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
        onclick={StartAction}
        style={{
            "background-position": percent(start_time - now, track_space),
        }}
    >
        <span>
            Tap Here to Start
            <small>Track autoplays in {s_to_mns(start_time - now)}</small>
        </span>
    </div>
);

const StartBar = (): VNode => (
    <div class={"startButton"} onclick={StartAction}>
        <span>
            Tap Here to Start
            <small>Autoplay Disabled</small>
        </span>
    </div>
);

const blank = new URL("../static/blank.mp4", import.meta.url);

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

        {state.blank_podium ?
            <video
                muted={true}
                key={
                    queue_item.id +
                    "-" +
                    (queue_item.start_time && queue_item.start_time < state.now)
                }
                autoPlay={true}
                crossorigin="anonymous"
            >
                <source src={blank} />
                {track.attachments.subtitle?.map((a) => (
                    <track
                        kind="subtitles"
                        src={attachment_path(state.root, a)}
                        default={true}
                        label="English"
                        srclang="en"
                    />
                ))}
            </video>
            :
            <Video
                state={state}
                track={track}
                lowres={true}
                loop={true}
            />
        }

        {state.starting ? (
            <StartingBar />
        ) : queue_item.start_time ? (
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
