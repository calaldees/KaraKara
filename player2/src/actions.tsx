/**
 * Actions = things which change the state of the app, normally
 * in response to eg a button press
 */
import {CheckQueue, CheckSettings, SendCommand, SetTrackState} from "./effects";

// App controls
export function SetPreviewVolume(state: State, event): State {
    event.target.volume = state.settings["karakara.player.video.preview_volume"];
    return state;
}

export function UpdateProgress(state: State, event): State {
    return {...state, progress: event.target.currentTime};
}

export function UpdatePodiumProgress(state: State, event): State {
    if(state.playing) return {...state, progress: event.target.currentTime};
    return state;
}

export function SetImages(state: State, response): State {
    return {
        ...state,
        images: response.data.images.map((fn, n) => ({
            filename: fn,
            x: (n / response.data.images.length),
            delay: Math.random() * 10,
        }))
    }
}

export function OnWsOpen(state: State, _) {
    return [{...state, connected: true}, CheckSettings(state), CheckQueue(state)];
}

export function OnWsClosed(state: State, _): State {
    return {...state, connected: false};
}

export function OnWsCommand(state: State, msg): State|Array<any> {
    const cmd = msg.data.trim();
    console.log("websocket_onmessage("+ cmd +")");
    switch(cmd) {
        case "play": return Play(state);
        case "stop": return Stop(state);
        case "pause": return Pause(state);
        case "seek_forwards": return SeekForwards(state, null);
        case "seek_backwards": return SeekBackwards(state, null);
        case "played": return Dequeue(state);
        case "queue_updated": return [state, CheckQueue(state)];
        case "settings": return [state, CheckSettings(state)];
        // Only one instance should mark the current track as skipped, to avoid
        // skipping two tracks
        case "skip": return state.is_podium ? Dequeue(state) : MarkTrackSkipped(state);
        default: console.log("unknown command: " + cmd); return state;
    }
}

export function OnKeyDown(state: State, event): State {
    let action = null;
    switch (event.key) {
        case "s"          : action = Dequeue; break; // skip
        case "Enter"      : action = Play; break;
        case "Escape"     : action = Stop; break;
        case "ArrowLeft"  : action = SeekBackwards; break;
        case "ArrowRight" : action = SeekForwards; break;
        case " "          : action = Pause; break;
        case "d"          : action = (state) => ({...state, connected: !state.connected}); break;
    }
    if (action) {
        event.preventDefault();
        return action(state);
    }
    return state;
}

export function OnCountdown(state: State, timestamp) {
    if(state.progress >= state.settings["karakara.player.autoplay"]) {
        return [state, SendCommand(state, "play")];
    }
    else {
        return {...state, progress: state.progress + 1/5};
    }
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
        if (state.paused) {video.play();}
        else              {video.pause();}
    }
    return {...state, paused: !state.paused};
}

export function Stop(state: State): State {
    return {
        ...state,
        playing: false,
        paused: false,
        progress: 0,
    }
}

export function SeekForwards(state: State, value): State {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if(video) video.currentTime += skip;
    return {...state, progress: state.progress + skip};
}

export function SeekBackwards(state: State, value): State {
    const skip = value || state.settings["karakara.player.video.skip.seconds"];
    const video = document.getElementsByTagName("video")[0];
    if(video) video.currentTime -= skip;
    return {...state, progress: state.progress - skip};
}

// Playlist controls
export function SetQueue(state: State, value: Array<QueueItem>): State {
    // if the first song in the queue has changed, stop playing
    if(state.queue.length === 0 || value.length === 0 || state.queue[0].id !== value[0].id) {
        return { ...state, queue: value, playing: false, paused: false, progress: 0 };
    }
    else {
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
    state = Dequeue(state);
    return [state, SetTrackState(state, "played")];
}

export function MarkTrackSkipped(state: State) {
    state = Dequeue(state);
    return [state, SetTrackState(state, "skipped")];
}
