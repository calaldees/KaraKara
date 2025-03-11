import { describe, expect, test } from "vitest";
import * as finder from "../track_finder";
import * as fs from "fs";

const track_dict: Record<string, Track> = JSON.parse(
    fs.readFileSync("./cypress/fixtures/small_tracks.json", "utf8"),
);
const tracks = Object.values(track_dict);

describe("apply_tags", () => {
    test("empty query returns full list", () => {
        expect(finder.apply_tags(tracks, []).map((track) => track.id)).toEqual([
            "track_id_1",
            "track_id_2",
        ]);
    });
    test("query for a tag returns tracks matching that tag", () => {
        expect(
            finder.apply_tags(tracks, ["from:Gundam"]).map((track) => track.id),
        ).toEqual(["track_id_2"]);
    });
    test("query for a non-existing tag key returns nothing", () => {
        expect(
            finder.apply_tags(tracks, ["asdf:anime"]).map((track) => track.id),
        ).toEqual([]);
    });
    test("query for a non-existing tag value returns nothing", () => {
        expect(
            finder.apply_tags(tracks, ["from:asdfa"]).map((track) => track.id),
        ).toEqual([]);
    });
});

describe("apply_search", () => {
    test("empty query returns full list", () => {
        expect(
            finder.apply_search(tracks, "").map((track) => track.id),
        ).toEqual(["track_id_1", "track_id_2"]);
    });
    test("query for a string returns tracks matching that string", () => {
        expect(
            finder.apply_search(tracks, "Love").map((track) => track.id),
        ).toEqual(["track_id_1"]);
    });
    test("query for a non-existing string returns nothing", () => {
        expect(
            finder.apply_search(tracks, "asdgadfgds").map((track) => track.id),
        ).toEqual([]);
    });
});

describe("apply_hidden", () => {
    test("empty query returns full list", () => {
        expect(
            finder.apply_hidden(tracks, []).map((track) => track.id),
        ).toEqual(["track_id_1", "track_id_2"]);
    });
    test("hidden top-level tag hides a track, even if it has other top-level tags", () => {
        expect(
            finder.apply_hidden(tracks, ["retro"]).map((track) => track.id),
        ).toEqual(["track_id_2"]);
    });
    test("invalid hidden top-level tag does nothing", () => {
        expect(
            finder.apply_hidden(tracks, ["asdfasd"]).map((track) => track.id),
        ).toEqual(["track_id_1", "track_id_2"]);
    });
    test("hidden sub-tag doesn't hide a track with other tags", () => {
        expect(
            finder
                .apply_hidden(tracks, ["category:anime"])
                .map((track) => track.id),
        ).toEqual(["track_id_2"]);
    });
    test("multiple hidden sub-tags hide tracks with all those tags but no others", () => {
        expect(
            finder
                .apply_hidden(tracks, ["category:anime", "category:jpop"])
                .map((track) => track.id),
        ).toEqual([]);
    });
    test("invalid hidden sub-tag key does nothing", () => {
        expect(
            finder
                .apply_hidden(tracks, ["asdfasd:anime"])
                .map((track) => track.id),
        ).toEqual(["track_id_1", "track_id_2"]);
    });
    test("invalid hidden sub-tag value does nothing", () => {
        expect(
            finder
                .apply_hidden(tracks, ["category:asdfasd"])
                .map((track) => track.id),
        ).toEqual(["track_id_1", "track_id_2"]);
    });
});

describe("text_to_filters", () => {
    test("leaves normal things alone", () => {
        expect(finder.text_to_filters(["foo:bar"], "baz")).toEqual([
            ["foo:bar"],
            "baz",
        ]);
    });
    test("handles empty", () => {
        expect(finder.text_to_filters([], "")).toEqual([[], ""]);
    });
    test("turns tag-search into filter", () => {
        expect(finder.text_to_filters([], "foo:bar")).toEqual([
            ["foo:bar"],
            "",
        ]);
    });
});

// find_tracks = apply_hidden + apply_tags(forced) + apply_tags(user) + apply_search
// I want one function which does it all for performance testing
describe("find_tracks", () => {
    // generate a large dataset, but do it outside of the test
    // so that it doesn't contribute to the test's performance
    const big_tracks: Record<string, Track> = {};
    for (let i = 0; i < 10000; i++) {
        big_tracks["track_id_" + i] = {
            id: "track_id_" + i,
            duration: 123,
            tags: {
                title: ["Test Track " + i],
                from: ["Macross"],
                category: ["anime"],
                "": ["retro"],
            },
            attachments: {
                video: [],
                preview: [],
                image: [],
                subtitle: [],
            },
            lyrics: [""],
        };
    }
    test("searching 10,000 tracks with every kind of filter performs ok", () => {
        // check that even though we have all the types of filters, and
        // none of them are narrowing down the list at all, we're still
        // doing ok
        const tracks = finder.find_tracks(
            Object.values(big_tracks),
            ["category:anime", "from:Macross"],
            "mac",
        );
        expect(tracks.length).toEqual(10000);
    });
});
