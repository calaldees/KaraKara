/**
 * Actions = things which change the state of the app, normally
 * in response to eg a button press
 */
import { SetTrackState } from "./effects";

// App controls
export function SetPreviewVolume(state: State, event): State {
    event.target.volume =
        state.settings["karakara.player.video.preview_volume"];
    return state;
}

export function UpdateProgress(state: State, event): State {
    return { ...state, progress: event.target.currentTime };
}

export function UpdatePodiumProgress(state: State, event): State {
    if (state.playing) return { ...state, progress: event.target.currentTime };
    return state;
}

// Current track controls
export function Play(state: State): State {
    return {
        ...state,
        playing: true,
        // if we're already playing, leave the state alone;
        // if we're starting a new song, start it un-paused from 0s
        paused: state.playing ? state.paused : false,
        progress: state.playing ? state.progress : 0,
    };
}

export function Pause(state: State): State {
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

export function Stop(state: State): State {
    return {
        ...state,
        playing: false,
        paused: false,
        progress: 0,
    };
}

export function SeekForwards(state: State, value): State {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime += skip;
    return { ...state, progress: state.progress + skip };
}

export function SeekBackwards(state: State, value): State {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime -= skip;
    return { ...state, progress: state.progress - skip };
}

// Playlist controls
export function SetQueue(state: State, value: Array<QueueItem>): State {
    // if the first song in the queue has changed, stop playing
    if (
        state.queue.length === 0 ||
        value.length === 0 ||
        state.queue[0].id !== value[0].id
    ) {
        return {
            ...state,
            queue: value,
            playing: false,
            paused: false,
            progress: 0,
        };
    } else {
        return { ...state, queue: value };
    }
}

export function Dequeue(state: State): State {
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

export function MarkTrackPlayed(state: State) {
    return [Dequeue(state), SetTrackState(state, "played")];
}

export function MarkTrackSkipped(state: State) {
    return [Dequeue(state), SetTrackState(state, "skipped")];
}
