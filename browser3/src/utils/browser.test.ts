import { describe, expect, test } from "vitest";

import * as utils from "./browser";

describe("dict2css", () => {
    test("should basically work", () => {
        expect(utils.dict2css({ foo: true, bar: false })).toEqual("foo");
        expect(utils.dict2css({ foo: true, bar: false, baz: true })).toEqual(
            "foo baz",
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

describe("sorted", () => {
    test("should basically work", () => {
        expect(utils.sorted([5, 3, 1, 4, 2])).toEqual([1, 2, 3, 4, 5]);
    });
});

describe("unique", () => {
    test("should basically work", () => {
        expect(utils.unique([1, 2, 2, 3, 4, 4, 5])).toEqual([1, 2, 3, 4, 5]);
    });
});

describe("nth", () => {
    test("should basically work", () => {
        expect(utils.nth(1)).toEqual("1st");
        expect(utils.nth(2)).toEqual("2nd");
        expect(utils.nth(3)).toEqual("3rd");
        expect(utils.nth(4)).toEqual("4th");
        expect(utils.nth(11)).toEqual("11th");
        expect(utils.nth(22)).toEqual("22nd");
        expect(utils.nth(33)).toEqual("33rd");
        expect(utils.nth(44)).toEqual("44th");
    });
});

describe("is_my_song", () => {
    test("match based only on session ID", () => {
        expect(
            utils.is_my_song(
                { session_id: "sess", performer_name: "Bob" },
                "sess-1234",
            ),
        ).toEqual(true);
    });
    test("match based only on performer name", () => {
        expect(
            utils.is_my_song(
                { session_id: "asdf", performer_name: "Bob" },
                "sess-1234",
                "Bob",
            ),
        ).toEqual(true);
    });
    test("no-match based only on neither", () => {
        expect(
            utils.is_my_song(
                { session_id: "asdf", performer_name: "Bob" },
                "sess-1234",
            ),
        ).toEqual(false);
    });
    test("no-match when track is missing", () => {
        expect(utils.is_my_song(undefined, "sess-1234")).toEqual(false);
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

describe("preferred_variant", () => {
    test("vocal preferred", () => {
        expect(
            utils.preferred_variant(["Instrumental", "Vocal", "Karaoke"]),
        ).toEqual("Vocal");
    });
    test("romaji preferred", () => {
        expect(
            utils.preferred_variant(["Hiragana", "Romaji", "Hangul"]),
        ).toEqual("Romaji");
    });
    test("no preferred found", () => {
        expect(utils.preferred_variant(["Instrumental", "Karaoke"])).toEqual(
            "Instrumental",
        );
    });
    test("empty list", () => {
        expect(utils.preferred_variant([])).toEqual("Default");
    });
});

describe("is_queue_hog", () => {
    // Helper function to create queue items more concisely
    const _qi = (
        session_id: string,
        performer_name: string,
        track_duration: number,
    ) => ({
        session_id,
        performer_name,
        track_duration,
    });
    test("returns null when queue is short", () => {
        const queue = [
            _qi("sess1", "Alice", 180),
            _qi("sess2", "Bob", 200),
            _qi("sess1", "Alice", 220),
        ];
        expect(utils.is_queue_hog(queue, "Alice", "sess1-1234")).toBeNull();
    });

    test("returns null when user has average number of tracks", () => {
        const queue = [
            _qi("sess1", "Alice", 180),
            _qi("sess2", "Bob", 200),
            _qi("sess2", "Bob", 210),
            _qi("sess3", "Charlie", 220),
            _qi("sess3", "Charlie", 190),
        ];
        // Alice has 1, adding another would give her 2
        // Bob has 2, Charlie has 2, average is 2.0
        expect(utils.is_queue_hog(queue, "Alice", "sess1-1234")).toBeNull();
    });

    test("returns warning when user would have far above average tracks", () => {
        const queue = [
            _qi("sess1", "Alice", 180),
            _qi("sess1", "Alice", 190),
            _qi("sess1", "Alice", 200),
            _qi("sess2", "Bob", 210),
            _qi("sess2", "Bob", 210),
            _qi("sess3", "Charlie", 220),
        ];
        // Alice has 3, adding another would give her 4
        // Bob has 2, Charlie has 1, average is 1.5
        const result = utils.is_queue_hog(queue, "Alice", "sess1-1234");
        expect(result).toContain("The average person has 1.5 tracks");
        expect(result).toContain("this will be your 4th");
    });

    test("matches by sessionId OR name", () => {
        const queue = [
            _qi("sess1", "Alice", 180),
            _qi("sessX", "Alice", 190),
            _qi("sess1", "Alice Changed Name", 200),
            _qi("sess2", "Bob", 210),
        ];
        // sess1/Alice has 3, adding another would give it 4
        // Bob has 1, average is 1.0
        const result = utils.is_queue_hog(queue, "Alice", "sess1-1234");
        expect(result).toContain("this will be your 4th");
    });

    test("handles empty queue of other people gracefully", () => {
        const queue = [
            _qi("sess1", "Alice", 180),
            _qi("sess1", "Alice", 190),
            _qi("sess1", "Alice", 200),
            _qi("sess1", "Alice", 210),
        ];
        expect(utils.is_queue_hog(queue, "Alice", "sess1-1234")).toBeNull();
    });
});

describe("sort_tag_keys", () => {
    test("should sort priority tags in correct order", () => {
        const input = ["use", "title", "artist", "from", "category"];
        const expected = ["title", "from", "artist", "category", "use"];
        expect(utils.sort_tag_keys(input)).toEqual(expected);
    });

    test("should sort all priority tags in full order", () => {
        const input = [
            "vocalstyle",
            "lang",
            "use",
            "category",
            "artist",
            "from",
            "title",
            "vocaltrack",
        ];
        const expected = [
            "title",
            "from",
            "artist",
            "category",
            "use",
            "lang",
            "vocaltrack",
            "vocalstyle",
        ];
        expect(utils.sort_tag_keys(input)).toEqual(expected);
    });

    test("should place non-priority tags at the end, sorted alphabetically", () => {
        const input = ["title", "zebra", "from", "alpha", "beta"];
        const expected = ["title", "from", "alpha", "beta", "zebra"];
        expect(utils.sort_tag_keys(input)).toEqual(expected);
    });

    test("should sort only non-priority tags alphabetically", () => {
        const input = ["zebra", "charlie", "alpha", "beta"];
        const expected = ["alpha", "beta", "charlie", "zebra"];
        expect(utils.sort_tag_keys(input)).toEqual(expected);
    });

    test("should handle empty array", () => {
        expect(utils.sort_tag_keys([])).toEqual([]);
    });

    test("should handle single element", () => {
        expect(utils.sort_tag_keys(["title"])).toEqual(["title"]);
        expect(utils.sort_tag_keys(["random"])).toEqual(["random"]);
    });

    test("should not modify the original array", () => {
        const input = ["use", "title", "artist"];
        const original = [...input];
        utils.sort_tag_keys(input);
        expect(input).toEqual(original);
    });

    test("should handle mixed priority and non-priority tags", () => {
        const input = ["length", "title", "subs", "from", "artist", "released"];
        const expected = [
            "title",
            "from",
            "released",
            "artist",
            "length",
            "subs",
        ];
        expect(utils.sort_tag_keys(input)).toEqual(expected);
    });
});
