import { bench, describe } from "vitest";

import { generateTracks } from "./test_data";
import * as finder from "./track_finder";

describe("find_tracks", () => {
    const big_tracks = Object.values(generateTracks(10000));

    bench("find_tracks with tags and search", () => {
        finder.find_tracks(
            big_tracks,
            ["category:anime", "from:Macross"],
            "mac",
        );
    });

    bench("find_tracks with only tags", () => {
        finder.find_tracks(big_tracks, ["category:anime", "from:Macross"], "");
    });

    bench("find_tracks with only search", () => {
        finder.find_tracks(big_tracks, [], "macross");
    });
});

describe("apply_tags", () => {
    const big_tracks = Object.values(generateTracks(10000));

    bench("apply_tags with no tags", () => {
        finder.apply_tags(big_tracks, []);
    });

    bench("apply_tags with single tag", () => {
        finder.apply_tags(big_tracks, ["category:anime"]);
    });

    bench("apply_tags with multiple tags", () => {
        finder.apply_tags(big_tracks, [
            "category:anime",
            "from:Macross",
            "vocaltrack:on",
        ]);
    });
});

describe("apply_search", () => {
    const big_tracks = Object.values(generateTracks(10000));

    bench("apply_search with empty query", () => {
        finder.apply_search(big_tracks, "");
    });

    bench("apply_search with short query", () => {
        finder.apply_search(big_tracks, "mac");
    });

    bench("apply_search with longer query", () => {
        finder.apply_search(big_tracks, "macross");
    });

    bench("apply_search with multi-word query", () => {
        finder.apply_search(big_tracks, "macross gundam");
    });
});
