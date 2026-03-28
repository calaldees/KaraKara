import { bench, describe } from "vitest";
import { generateTracks } from "./test_data";

import * as query from "./track_query";

describe("query_tracks", () => {
    const tracks = Object.values(generateTracks(10000));

    bench("empty query", () => {
        query.query_tracks(tracks, "");
    });

    bench("simple query", () => {
        query.query_tracks(tracks, "category=anime");
    });

    bench("complex query", () => {
        query.query_tracks(
            tracks,
            "(category=anime and from=Macross) or year<2000",
        );
    });
});
