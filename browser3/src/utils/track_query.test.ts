import { describe, expect, test } from "vitest";
import type { QueryNode } from "./track_query";
import * as query from "./track_query";

import { tracks as track_dict } from "./test_data";
const tracks = Object.values(track_dict);

function qids(q: string): string[] {
    return query.query_tracks(tracks, q).map((track) => track.id);
}

describe("parseQuery", () => {
    test("empty query returns null", () => {
        expect(query.parseQuery("")).toBeNull();
        expect(query.parseQuery("   ")).toBeNull();
    });

    test("equals operator", () => {
        const node = query.parseQuery("from=Gundam");
        expect(node).toEqual({
            type: "equals",
            key: "from",
            value: "Gundam",
        });
    });

    test("equals with single quotes", () => {
        const node = query.parseQuery("title='Modern Track'");
        expect(node).toEqual({
            type: "equals",
            key: "title",
            value: "Modern Track",
        });
    });

    test("equals with double quotes", () => {
        const node = query.parseQuery('title="Modern Track"');
        expect(node).toEqual({
            type: "equals",
            key: "title",
            value: "Modern Track",
        });
    });

    test("notEquals operator", () => {
        const node = query.parseQuery("from!=Gundam");
        expect(node).toEqual({
            type: "notEquals",
            key: "from",
            value: "Gundam",
        });
    });

    test("notEquals with quotes", () => {
        const node = query.parseQuery("from!='Gundam'");
        expect(node).toEqual({
            type: "notEquals",
            key: "from",
            value: "Gundam",
        });
    });

    test("contains operator", () => {
        const node = query.parseQuery("title~Modern");
        expect(node).toEqual({
            type: "contains",
            key: "title",
            value: "Modern",
        });
    });

    test("contains with quotes", () => {
        const node = query.parseQuery("title~'Mod'");
        expect(node).toEqual({
            type: "contains",
            key: "title",
            value: "Mod",
        });
    });

    test("notContains operator", () => {
        const node = query.parseQuery("title!~Modern");
        expect(node).toEqual({
            type: "notContains",
            key: "title",
            value: "Modern",
        });
    });

    test("notContains with quotes", () => {
        const node = query.parseQuery("title!~'Mod'");
        expect(node).toEqual({
            type: "notContains",
            key: "title",
            value: "Mod",
        });
    });

    test("less than operator", () => {
        const node = query.parseQuery("year<2000");
        expect(node).toEqual({
            type: "less",
            key: "year",
            value: 2000,
        });
    });

    test("greater than operator", () => {
        const node = query.parseQuery("year>2000");
        expect(node).toEqual({
            type: "greater",
            key: "year",
            value: 2000,
        });
    });

    test("less or equal operator", () => {
        const node = query.parseQuery("year<=2000");
        expect(node).toEqual({
            type: "lessOrEqual",
            key: "year",
            value: 2000,
        });
    });

    test("greater or equal operator", () => {
        const node = query.parseQuery("year>=2000");
        expect(node).toEqual({
            type: "greaterOrEqual",
            key: "year",
            value: 2000,
        });
    });

    test("not operator", () => {
        const node = query.parseQuery("not year<2000");
        expect(node).toEqual({
            type: "not",
            child: {
                type: "less",
                key: "year",
                value: 2000,
            },
        });
    });

    test("and operator", () => {
        const node = query.parseQuery("category=anime and year<1990");
        expect(node).toEqual({
            type: "and",
            left: {
                type: "equals",
                key: "category",
                value: "anime",
            },
            right: {
                type: "less",
                key: "year",
                value: 1990,
            },
        });
    });

    test("or operator", () => {
        const node = query.parseQuery("category=anime or year<1990");
        expect(node).toEqual({
            type: "or",
            left: {
                type: "equals",
                key: "category",
                value: "anime",
            },
            right: {
                type: "less",
                key: "year",
                value: 1990,
            },
        });
    });

    test("parentheses for grouping", () => {
        const node = query.parseQuery(
            "category=anime and (year<1990 or title='Modern Track')",
        );
        expect(node).toEqual({
            type: "and",
            left: {
                type: "equals",
                key: "category",
                value: "anime",
            },
            right: {
                type: "or",
                left: {
                    type: "less",
                    key: "year",
                    value: 1990,
                },
                right: {
                    type: "equals",
                    key: "title",
                    value: "Modern Track",
                },
            },
        });
    });

    test("multiple not operators", () => {
        const node = query.parseQuery("not not year<2000");
        expect(node).toEqual({
            type: "not",
            child: {
                type: "not",
                child: {
                    type: "less",
                    key: "year",
                    value: 2000,
                },
            },
        });
    });
});

describe("evaluateQuery", () => {
    const track_anime_1980 = track_dict.track_id_1; // category=anime, year=1980
    const track_anime_gundam = track_dict.track_id_2; // category=anime, from=Gundam, year=2000
    const track_modern = track_dict.track_2010; // title='Modern Track', year=2010

    test("equals - match", () => {
        const node: QueryNode = {
            type: "equals",
            key: "from",
            value: "Gundam",
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(true);
    });

    test("equals - no match", () => {
        const node: QueryNode = {
            type: "equals",
            key: "from",
            value: "Gundam",
        };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(false);
    });

    test("equals - case insensitive", () => {
        const node: QueryNode = {
            type: "equals",
            key: "from",
            value: "gundam",
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(true);
    });

    test("notEquals - match", () => {
        const node: QueryNode = {
            type: "notEquals",
            key: "from",
            value: "Gundam",
        };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(true);
    });

    test("notEquals - no match", () => {
        const node: QueryNode = {
            type: "notEquals",
            key: "from",
            value: "Gundam",
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(false);
    });

    test("notEquals - case insensitive", () => {
        const node: QueryNode = {
            type: "notEquals",
            key: "from",
            value: "GUNDAM",
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(false);
    });

    test("contains - match", () => {
        const node: QueryNode = {
            type: "contains",
            key: "title",
            value: "Mod",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(true);
    });

    test("contains - no match", () => {
        const node: QueryNode = {
            type: "contains",
            key: "title",
            value: "Xyz",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(false);
    });

    test("contains - case insensitive", () => {
        const node: QueryNode = {
            type: "contains",
            key: "title",
            value: "MODERN",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(true);
    });

    test("notContains - match", () => {
        const node: QueryNode = {
            type: "notContains",
            key: "title",
            value: "Xyz",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(true);
    });

    test("notContains - no match", () => {
        const node: QueryNode = {
            type: "notContains",
            key: "title",
            value: "Mod",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(false);
    });

    test("notContains - case insensitive", () => {
        const node: QueryNode = {
            type: "notContains",
            key: "title",
            value: "mOdErN",
        };
        expect(query.evaluateQuery(track_modern, node)).toBe(false);
    });

    test("less - match", () => {
        const node: QueryNode = { type: "less", key: "year", value: 2000 };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(true);
    });

    test("less - no match", () => {
        const node: QueryNode = { type: "less", key: "year", value: 2000 };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(false);
    });

    test("greater - match", () => {
        const node: QueryNode = { type: "greater", key: "year", value: 2000 };
        expect(query.evaluateQuery(track_modern, node)).toBe(true);
    });

    test("greater - no match", () => {
        const node: QueryNode = { type: "greater", key: "year", value: 2000 };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(false);
    });

    test("not - inverts result", () => {
        const node: QueryNode = {
            type: "not",
            child: { type: "less", key: "year", value: 2000 },
        };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(false);
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(true);
    });

    test("and - both true", () => {
        const node: QueryNode = {
            type: "and",
            left: { type: "equals", key: "category", value: "anime" },
            right: { type: "less", key: "year", value: 1990 },
        };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(true);
    });

    test("and - one false", () => {
        const node: QueryNode = {
            type: "and",
            left: { type: "equals", key: "category", value: "anime" },
            right: { type: "less", key: "year", value: 1990 },
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(false);
    });

    test("or - one true", () => {
        const node: QueryNode = {
            type: "or",
            left: { type: "equals", key: "category", value: "anime" },
            right: { type: "less", key: "year", value: 1990 },
        };
        expect(query.evaluateQuery(track_anime_gundam, node)).toBe(true);
    });

    test("or - both false", () => {
        const node: QueryNode = {
            type: "or",
            left: { type: "equals", key: "category", value: "rock" },
            right: { type: "less", key: "year", value: 1970 },
        };
        expect(query.evaluateQuery(track_anime_1980, node)).toBe(false);
    });
});

describe("tracks_query (empty)", () => {
    test("empty query returns full list", () => {
        expect(qids("")).toEqual([
            "track_id_1",
            "track_id_2",
            "track_1990",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
        ]);
    });
});

describe("tracks_query (equals)", () => {
    test("query for a tag returns tracks matching that tag", () => {
        expect(qids("from=Gundam")).toEqual(["track_id_2"]);
    });
    test("query for a non-existing tag key returns nothing", () => {
        expect(qids("asdf=Gundam")).toEqual([]);
    });
    test("query for a non-existing tag value returns nothing", () => {
        expect(qids("from=asdfa")).toEqual([]);
    });
    test("case insensitive", () => {
        expect(qids("from=gundam")).toEqual(["track_id_2"]);
    });
});

describe("tracks_query (notEquals)", () => {
    test("all tracks without the specified value", () => {
        expect(qids("from!=Gundam")).toEqual([
            "track_id_1",
            "track_1990",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
        ]);
    });
    test("case insensitive", () => {
        expect(qids("from!=gUnDaM")).toEqual([
            "track_id_1",
            "track_1990",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
        ]);
    });
});

describe("tracks_query (contains)", () => {
    test("tracks with titles containing substring", () => {
        expect(qids("title~'Mod'")).toEqual(["track_2010"]);
    });
    test("tracks with titles containing substring (unquoted)", () => {
        expect(qids("title~Recent")).toEqual(["track_2020"]);
    });
    test("case insensitive", () => {
        expect(qids("title~'MODERN'")).toEqual(["track_2010"]);
    });
});

describe("tracks_query (notContains)", () => {
    test("tracks without substring in title", () => {
        expect(qids("title!~'Mod'")).toEqual([
            "track_id_1",
            "track_id_2",
            "track_1990",
            "track_2000",
            "track_2020",
            "track_no_year",
        ]);
    });
    test("case insensitive", () => {
        expect(qids("title!~'mOdErN'")).toEqual([
            "track_id_1",
            "track_id_2",
            "track_1990",
            "track_2000",
            "track_2020",
            "track_no_year",
        ]);
    });
});

describe("tracks_query (range)", () => {
    test("year<2000", () => {
        expect(qids("year<2000")).toEqual(["track_id_1", "track_1990"]);
    });
});

describe("tracks_query (not)", () => {
    test("not year<2000", () => {
        expect(qids("not year<2000")).toEqual([
            "track_id_2",
            "track_2000",
            "track_2010",
            "track_2020",
            "track_no_year",
        ]);
    });
});

describe("tracks_query (complex)", () => {
    test("category=anime and (year<1990 or title='Modern Track')", () => {
        expect(
            qids("category=anime and (year<1990 or title='Modern Track')"),
        ).toEqual(["track_id_1"]);
    });
});
