import type { QueueItem, Settings, Track } from "@/types";

import _tracks from "../../fixtures/small_tracks.json";
export const tracks: Record<string, Track> = _tracks;

import _queue from "../../fixtures/small_queue.json";
export const queue: QueueItem[] = _queue;

import _settings from "../../fixtures/small_settings.json";
export const settings: Settings = _settings;

export function generateTracks(count: number): Record<string, Track> {
    const trackList = Object.values(tracks);
    const generatedTracks: Record<string, Track> = {};
    for (let i = 0; i < count; i++) {
        const trackId = `track_id_${i}`;
        generatedTracks[trackId] = {
            ...trackList[i % trackList.length],
            id: trackId,
            duration: 180 + (i % 60),
        };
    }
    return generatedTracks;
}
