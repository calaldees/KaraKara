import { describe, expect, test } from "vitest";

import { tracks as track_dict } from "./test_data";

import * as finder from "./track_finder";

const tracks = Object.values(track_dict);

describe("apply_tags", () => {
    test("empty query returns full list", () => {
        expect(finder.apply_tags(tracks, []).map((track) => track.id)).toEqual([
            "track_id_1",
            "track_id_2",
            "track_1990",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
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
        ).toEqual([
            "track_id_1",
            "track_id_2",
            "track_1990",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
        ]);
    });
    test("query for a string returns tracks matching that string", () => {
        expect(
            finder.apply_search(tracks, "Love").map((track) => track.id),
        ).toEqual(["track_id_1", "track_2000"]);
    });
    test("query for a non-existing string returns nothing", () => {
        expect(
            finder.apply_search(tracks, "asdgadfgds").map((track) => track.id),
        ).toEqual([]);
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
