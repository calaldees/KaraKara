import { describe, expect, test } from "vitest";
import * as utils from "../utils";
import * as fs from "fs";

const track_dict = JSON.parse(
    fs.readFileSync("./cypress/fixtures/small_tracks.json", "utf8"),
);

///////////////////////////////////////////////////////////////////////
// Misc one-off utils

describe("dict2css", () => {
    test("should basically work", () => {
        expect(utils.dict2css({ foo: true, bar: false })).toEqual("foo");
        expect(utils.dict2css({ foo: true, bar: false, baz: true })).toEqual(
            "foo baz",
        );
    });
});

describe("attachment_path", () => {
    const attachment = track_dict["track_id_1"].attachments.video[0];
    test("should basically work", () => {
        expect(utils.attachment_path("http://example.com", attachment)).toEqual(
            "http://example.com/files/f/foo.mp4",
        );
    });
});

describe("shuffle", () => {
    test("should basically work", () => {
        expect(utils.shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])).not.toEqual([
            1, 2, 3, 4, 5, 6, 7, 8, 9, 0,
        ]);
    });
});

describe("mqtt_url", () => {
    test("should basically work", () => {
        expect(utils.mqtt_url("https://example.com")).toEqual(
            "wss://example.com/mqtt",
        );
    });
});

describe("short_date", () => {
    test("should basically work", () => {
        expect(utils.short_date("2021-01-03T14:00:00")).toEqual("14:00");
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

describe("is_my_song", () => {
    test("match based only on session ID", () => {
        expect(
            utils.is_my_song("sess1", "Jim", {
                session_id: "sess1",
                performer_name: "Bob",
            }),
        ).toEqual(true);
    });
    test("match based only on performer name", () => {
        expect(
            utils.is_my_song("sess1", "Jim", {
                session_id: "sess2",
                performer_name: "Jim",
            }),
        ).toEqual(true);
    });
    test("match based on both", () => {
        expect(
            utils.is_my_song("sess1", "Jim", {
                session_id: "sess1",
                performer_name: "Jim",
            }),
        ).toEqual(true);
    });
    test("no-match based only on neither", () => {
        expect(
            utils.is_my_song("sess1", "Jim", {
                session_id: "sess2",
                performer_name: "Bob",
            }),
        ).toEqual(false);
    });
    test("no-match when track is missing", () => {
        expect(utils.is_my_song("sess1", "Jim", undefined)).toEqual(false);
    });
});

describe("shortest_tag", () => {
    test("should handle undefined", () => {
        expect(utils.shortest_tag(undefined)).toEqual("");
    });
    test("should handle a list", () => {
        expect(utils.shortest_tag(["donkey", "foo", "cake"])).toEqual("foo");
    });
});

describe("last_tag", () => {
    test("should basically work", () => {
        expect(
            utils.last_tag(
                { from: ["Macross"], Macross: ["Do You Remember Love?"] },
                "from",
            ),
        ).toEqual("Do You Remember Love?");
    });
    test("handle invalid requests", () => {
        expect(
            utils.last_tag(
                { from: ["Macross"], Macross: ["Do You Remember Love?"] },
                "cake",
            ),
        ).toEqual("cake");
    });
});

describe("track_info", () => {
    test("should basically work", () => {
        expect(
            utils.track_info([], {
                tags: {
                    title: ["Fake Track Name"],
                    from: ["Macross"],
                    Macross: ["Do You Remember Love?"],
                    use: ["opening", "op1"],
                    length: ["short"],
                },
            }),
        ).toEqual("Macross - opening, op1 - short");
    });
    test("searching for a series should avoid showing that series", () => {
        expect(
            utils.track_info(["from:Macross"], {
                tags: {
                    title: ["Fake Track Name"],
                    from: ["Macross"],
                    Macross: ["Do You Remember Love?"],
                    use: ["opening", "op1"],
                    length: ["short"],
                },
            }),
        ).toEqual("opening, op1 - short");
    });
    test("avoid duplicating the title in the info", () => {
        expect(
            utils.track_info([], {
                tags: {
                    title: ["Fake Track Name"],
                    from: ["Fake Track Name"],
                    use: ["opening", "op1"],
                    length: ["short"],
                },
            }),
        ).toEqual("opening, op1 - short");
    });
    test("some categories have specific rules", () => {
        expect(
            utils.track_info([], {
                tags: {
                    title: ["Fake Track Name"],
                    artist: ["Billy Rock"],
                    category: ["jpop"],
                },
            }),
        ).toEqual("Billy Rock");
    });
    test("unrecognised categories should use default rules", () => {
        expect(
            utils.track_info([], {
                tags: {
                    title: ["Fake Track Name"],
                    from: ["Macross"],
                    category: ["example"],
                    use: ["opening", "op1"],
                    length: ["short"],
                },
            }),
        ).toEqual("Macross - opening, op1 - short");
    });
});

describe("copy_type", () => {
    test("default", () => {
        expect(utils.copy_type("Macross", "Gundam")).toEqual("Gundam");
        expect(utils.copy_type("Macross", "")).toEqual("");
    });
    test("array", () => {
        expect(utils.copy_type(["Macross", "Gundam"], "Gundam,Cake")).toEqual([
            "Gundam",
            "Cake",
        ]);
        expect(utils.copy_type(["Macross", "Gundam"], "")).toEqual([]);
    });
    test("int", () => {
        expect(utils.copy_type(2, "42")).toEqual(42);
    });
    test("float", () => {
        expect(utils.copy_type(12.34, "43.21")).toEqual(43.21);
    });
});

describe("current_and_future", () => {
    var item: QueueItem = {
        id: 4567,
        performer_name: "test",
        session_id: "test",
        start_time: 0,
        track_duration: 100,
        track_id: "My_Song",
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

describe("normalise_name", () => {
    test("plain", () => {
        expect(utils.normalise_name("Macross")).toEqual("MACROSS");
    });
    test("punctuation", () => {
        expect(utils.normalise_name("_Macross_")).toEqual("MACROSS");
    });
    test("all punctuation", () => {
        expect(utils.normalise_name("?!?")).toEqual("?!?");
    });
});

describe("normalise_cmp", () => {
    test("plain", () => {
        expect(utils.normalise_cmp("A", "B")).toEqual(-1);
        expect(utils.normalise_cmp("B", "A")).toEqual(1);
    });
    test("punctuation", () => {
        expect(utils.normalise_cmp("A", "_B_")).toEqual(-1);
        expect(utils.normalise_cmp("B", "_A_")).toEqual(1);
    });
    test("case", () => {
        expect(utils.normalise_cmp("A", "b")).toEqual(-1);
        expect(utils.normalise_cmp("B", "a")).toEqual(1);
    });
});
