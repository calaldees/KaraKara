import { describe, expect, test } from "vitest";

import type { QueueItem } from "@/types";
import * as utils from "./common";
import { tracks } from "./test_data";

describe("attachment_path", () => {
    test("relative path - same origin", () => {
        expect(utils.attachment_path({ path: "f/foo.mp4" })).toEqual(
            "/files/f/foo.mp4",
        );
    });

    test("absolute path - same origin", () => {
        expect(utils.attachment_path({ path: "/files/f/bar.mp4" })).toEqual(
            "/files/f/bar.mp4",
        );
    });

    test("absolute URL - same origin", () => {
        expect(
            utils.attachment_path({
                path: "http://localhost:3000/files/f/baz.mp4",
            }),
        ).toEqual("/files/f/baz.mp4");
    });

    test("absolute URL - different origin", () => {
        expect(
            utils.attachment_path({
                path: "https://cdn.example.com/files/f/external.mp4",
            }),
        ).toEqual("https://cdn.example.com/files/f/external.mp4");
    });

    test("fixture data works", () => {
        expect(
            utils.attachment_path(tracks["track_id_1"].attachments.video[0]),
        ).toEqual("/files/f/foo.mp4");
    });
});

describe("time_until", () => {
    test("should basically work", () => {
        expect(utils.time_until(0, 125)).toEqual("In 2 mins");
        expect(utils.time_until(0, 65)).toEqual("In 1 min");
        expect(utils.time_until(0, 30)).toEqual("In 30 secs");
        expect(utils.time_until(0, 0)).toEqual("Now");
        expect(utils.time_until(0, null)).toEqual("");
    });
});

describe("percent", () => {
    test("should basically work", () => {
        expect(utils.percent(0, 2)).toEqual("0%");
        expect(utils.percent(1, 2)).toEqual("50%");
        expect(utils.percent(2, 2)).toEqual("100%");
        expect(utils.percent(1, 3)).toEqual("33%");
    });
});

describe("current_and_future", () => {
    const item: QueueItem = {
        id: 4567,
        performer_name: "test",
        session_id: "test",
        start_time: 0,
        track_duration: 100,
        track_id: "My_Song",
        video_variant: "Default",
        subtitle_variant: "Default",
    };
    test("empty", () => {
        expect(utils.current_and_future(1000, [])).toEqual([]);
    });
    test("past", () => {
        item.start_time = 123;
        expect(utils.current_and_future(1000, [item])).toEqual([]);
    });
    test("present", () => {
        item.start_time = 970; // started 30 seconds ago
        expect(utils.current_and_future(1000, [item])).toEqual([item]);
    });
    test("future", () => {
        item.start_time = 1030; // starts in 30 seconds
        expect(utils.current_and_future(1000, [item])).toEqual([item]);
    });
    test("stopped", () => {
        item.start_time = null; // item is in a paused queue
        expect(utils.current_and_future(1000, [item])).toEqual([item]);
    });
});
