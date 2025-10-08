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

describe("is_my_song", () => {
    test("match based only on session ID", () => {
        expect(utils.is_my_song("sess-1234", { session_id: "sess" })).toEqual(
            true,
        );
    });
    test("no-match based only on neither", () => {
        expect(utils.is_my_song("sess-1234", { session_id: "asdf" })).toEqual(
            false,
        );
    });
    test("no-match when track is missing", () => {
        expect(utils.is_my_song("sess-1234", undefined)).toEqual(false);
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
