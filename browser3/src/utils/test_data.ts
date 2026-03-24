import type { QueueItem, Settings, Track } from "@/types";

import _tracks from "../../fixtures/small_tracks.json";
export const tracks: Record<string, Track> = _tracks;

import _queue from "../../fixtures/small_queue.json";
export const queue: QueueItem[] = _queue;

import _settings from "../../fixtures/small_settings.json";
export const settings: Settings = _settings;
