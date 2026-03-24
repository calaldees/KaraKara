import { bench, describe } from "vitest";

import { generateTracks } from "./test_data";
import * as finder from "./track_finder";

describe("find_tracks", () => {
    const tracks = Object.values(generateTracks(10000));
    const subset = tracks.slice(0, 1000);

    bench("tags and search (full)", () => {
        finder.find_tracks(tracks, ["category:anime", "from:Macross"], "mac");
    });

    bench("tags and search (subset)", () => {
        finder.find_tracks(subset, ["category:anime", "from:Macross"], "mac");
    });

    bench("only tags (full)", () => {
        finder.find_tracks(tracks, ["category:anime", "from:Macross"], "");
    });

    bench("only tags (subset)", () => {
        finder.find_tracks(subset, ["category:anime", "from:Macross"], "");
    });

    bench("only search (full)", () => {
        finder.find_tracks(tracks, [], "macross");
    });

    bench("only search (subset)", () => {
        finder.find_tracks(subset, [], "macross");
    });
});

describe("apply_tags", () => {
    const tracks = Object.values(generateTracks(10000));

    bench("no tags", () => {
        finder.apply_tags(tracks, []);
    });

    bench("single tag", () => {
        finder.apply_tags(tracks, ["category:anime"]);
    });

    bench("multiple tags", () => {
        finder.apply_tags(tracks, [
            "category:anime",
            "from:Macross",
            "vocaltrack:on",
        ]);
    });
});

describe("apply_search", () => {
    const tracks = Object.values(generateTracks(10000));

    bench("empty query", () => {
        finder.apply_search(tracks, "");
    });

    bench("short query", () => {
        finder.apply_search(tracks, "mac");
    });

    bench("longer query", () => {
        finder.apply_search(tracks, "macross");
    });

    bench("multi-word query", () => {
        finder.apply_search(tracks, "macross gundam");
    });
});
