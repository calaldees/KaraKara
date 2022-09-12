/*
 * Actions: functions which take app state as input,
 * and return modified state (optionally including
 * side effects) as output
 */
import { SetTrackState } from "./effects";

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
    const skip = value || state.settings["skip_seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime += skip;
    return { ...state, progress: state.progress + skip };
}

export function SeekBackwards(state: State, value: number | null): Dispatchable {
    const skip = value || state.settings["skip_seconds"];
    const video = document.getElementsByTagName("video")[0];
    if (video) video.currentTime -= skip;
    return { ...state, progress: state.progress - skip };
}

// Playlist controls
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
