/*
 * Actions: functions which take app state as input,
 * and return modified state (optionally including
 * side effects) as output
 */
import { SetTrackState } from "./effects";

// App controls
export function SetRoom(state: State, room: string): Dispatchable {
    return { ...state, room_name: room };
}

export function SetPreviewVolume(state: State, event): Dispatchable {
    event.target.volume =
        state.settings["karakara.player.video.preview_volume"];
    return state;
}

export function UpdateProgress(state: State, event): Dispatchable {
    return { ...state, progress: event.target.currentTime };
}

export function UpdatePodiumProgress(state: State, event): Dispatchable {
    if (state.playing) return { ...state, progress: event.target.currentTime };
    return state;
}

// Current track controls
export function Play(state: State): Dispatchable {
    return {
        ...state,
        playing: true,
        // if we're already playing, leave the state alone;
        // if we're starting a new song, start it un-paused from 0s
        paused: state.playing ? state.paused : false,
        progress: state.playing ? state.progress : 0,
    };
}

export function Pause(state: State): Dispatchable {
    const video = document.getElementsByTagName("video")[0];
    if (video) {
        if (state.paused) {
            video.play();
        } else {
            video.pause();
        }
    }
    return { ...state, paused: !state.paused };
}

export function Stop(state: State): Dispatchable {
    return {
        ...state,
        playing: false,
        paused: false,
        progress: 0,
    };
}

export function SeekForwards(state: State, value: number | null): Dispatchable {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime += skip;
    return { ...state, progress: state.progress + skip };
}

export function SeekBackwards(state: State, value: number | null): Dispatchable {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime -= skip;
    return { ...state, progress: state.progress - skip };
}

// Playlist controls
export function UpdateQueue(state: State, new_queue: Array<QueueItem>): Dispatchable {
    // still waiting for the queue to return the new format, hard-coding for now
    return {
        ...state, queue: [
            {
                id: 1,
                track_id: "rgll4djKoy9",
                performer_name: "testo",
                total_duration: 123,
            },
            {
                id: 2,
                track_id: "jWBWalw4cbn",
                performer_name: "alice",
                total_duration: 123,
            },
            {
                id: 3,
                track_id: "GjwjyEGOUtz",
                performer_name: "bob",
                total_duration: 123,
            },
        ]
    };
    // if the first song in the queue has changed, stop playing
    if (
        state.queue.length === 0 ||
        new_queue.length === 0 ||
        state.queue[0].id !== new_queue[0].id
    ) {
        return {
            ...state,
            queue: new_queue,
            playing: false,
            paused: false,
            progress: 0,
        };
    } else {
        return { ...state, queue: new_queue };
    }
}

function _dequeue(state: State): State {
    return {
        ...state,
        // remove the first song
        queue: state.queue.slice(1),
        // and stop playing (same as .stop(), but we
        // want to do it all in a single state update
        // to avoid rendering an incomplete state)
        playing: false,
        paused: false,
        progress: 0,
    };
}

export function Dequeue(state: State): Dispatchable {
    return _dequeue(state);
}

export function MarkTrackPlayed(state: State): Dispatchable {
    return [_dequeue(state), SetTrackState(state, "played")];
}

export function MarkTrackSkipped(state: State): Dispatchable {
    return [_dequeue(state), SetTrackState(state, "skipped")];
}
