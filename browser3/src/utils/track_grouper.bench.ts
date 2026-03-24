import { bench, describe } from "vitest";

import { generateTracks } from "./test_data";
import * as grouper from "./track_grouper";

describe("summarise_tags", () => {
    const tracks = Object.values(generateTracks(10000));
    const subset = tracks.slice(0, 100);

    bench("full library", () => {
        grouper.summarise_tags(tracks);
    });

    bench("subset", () => {
        grouper.summarise_tags(subset);
    });
});

describe("suggest_next_filters", () => {
    const summary = {
        macross: {
            "movie 1": 2,
            "movie 2": 1,
        },
        pokemon: {
            johto: 2,
        },
        artist: {
            "artist 1": 10,
            "artist 2": 20,
            "artist 3": 30,
        },
        category: {
            anime: 100,
            jpop: 50,
            game: 25,
        },
    };

    bench("no filters", () => {
        grouper.suggest_next_filters([], summary);
    });

    bench("curated tag", () => {
        grouper.suggest_next_filters(["category:anime"], summary);
    });

    bench("tag having children", () => {
        grouper.suggest_next_filters(["from:macross"], summary);
    });

    bench("multiple filters", () => {
        grouper.suggest_next_filters(
            ["category:anime", "vocaltrack:on", "lang:jp"],
            summary,
        );
    });
});

describe("group_tracks", () => {
    const tracks = Object.values(generateTracks(10000));

    bench("no filters", () => {
        grouper.group_tracks([], tracks);
    });

    bench("single filter", () => {
        grouper.group_tracks(["category:anime"], tracks);
    });

    bench("multiple filters", () => {
        grouper.group_tracks(["category:anime", "vocaltrack:on"], tracks);
    });

    bench("category:new filter", () => {
        grouper.group_tracks(["category:new"], tracks);
    });
});
