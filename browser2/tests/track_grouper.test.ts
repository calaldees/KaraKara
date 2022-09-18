/// <reference path='../src/browser.d.ts'/>

import * as grouper from '../src/track_grouper';

import * as fs from 'fs';
let state: State = JSON.parse(fs.readFileSync('./tests/state.json', 'utf8'));
state.track_list = JSON.parse(fs.readFileSync('./tests/tracks.json', 'utf8'));
state.queue = JSON.parse(fs.readFileSync('./tests/queue.json', 'utf8'));

describe('summarise_tags', () => {
    test('should basically work', () => {
        expect(grouper.summarise_tags(Object.values(state.track_list)))
            .toEqual({
                "": {
                    "minami": 1,
                    "retro": 1,
                },
                "from": {
                    "Macross": 1,
                    "Gundam": 1,
                },
                "length": {
                    "short": 2,
                },
                "use": {
                    "op1": 1,
                    "op2": 1,
                    "opening": 2,
                },
                "Macross": {
                    "Do You Remember Love?": 1,
                },
                "category": {
                    "anime": 2,
                    "cartoon": 1,
                },
            });
    });
});

describe('suggest_next_filters', () => {
    const summary = {
        macross: {
            "movie 1": 2,
            "movie 2": 1,
        },
        pokemon: {
            "johto": 2
        },
    };
    test('when not searching for any tag, return default suggestions', () => {
        expect(grouper.suggest_next_filters([], summary))
            .toEqual(["category", "vocalstyle", "vocaltrack", "lang"]);
    });
    test('when searching for a curated tag, return curated suggestions', () => {
        expect(grouper.suggest_next_filters(["category:jpop"], summary))
            .toEqual(["artist", "from"]);
    });
    test('when searching for a tag which has children, show that tag as the parent', () => {
        expect(grouper.suggest_next_filters(["from:macross"], summary))
            .toEqual(["macross"]);
    });
    test("when searching for a tag which doesn't have children, show full summary", () => {
        expect(grouper.suggest_next_filters(["category:popular"], summary))
            .toEqual(["macross", "pokemon"]);
    });
});


describe('group_tracks', () => {
    let many_tracks: Array<Track> = [];
    for (let i = 0; i < 1000; i++) {
        many_tracks.push(state.track_list["track_id_1"]);
    }
    many_tracks.push(state.track_list["track_id_2"]);

    test("when there are no tracks, show 'No Results'", () => {
        let results = grouper.group_tracks([], []);
        expect(results.length).toEqual(1);
        expect(results[0][0]).toEqual("No Results");
    });
    test("when there are only a few tracks, show all of them", () => {
        let results = grouper.group_tracks(
            [],
            [state.track_list["track_id_1"], state.track_list["track_id_2"]]
        );
        expect(results.length).toEqual(1);
        expect(results[0][0]).toEqual("");
        expect(results[0][1].tracks).toBeDefined();
    });
    test("with many tracks and no filters, prompt for default filters", () => {
        let results = grouper.group_tracks([], many_tracks);
        expect(results.length).toBeGreaterThanOrEqual(1);
        expect(results[0][0]).toEqual("category");
        expect(results[0][1].filters).toBeDefined();
    });
    test("with many tracks and a filter, prompt for relevant sub-filters", () => {
        let results = grouper.group_tracks(["category:anime"], many_tracks);
        expect(results.length).toBeGreaterThanOrEqual(1);
        expect(results[0][0]).toEqual("from");
        expect(results[0][1].filters).toBeDefined();
    });
    test("show grouped filters if a tag has a ton of children", () => {
        // Generate a track list with a lot of "from:..." variants
        function random_title(length: number): string {
            var result = '';
            var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
            var charactersLength = characters.length;
            for (var i = 0; i < length; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }
        let many_froms = many_tracks.map(
            track => ({ ...track, tags: { ...track.tags, "from": [random_title(2)] } })
        );
        // When searching for category:anime, it's hard-coded that the next prompt
        // should be "from", and we have many froms, so they should be grouped
        let results = grouper.group_tracks(["category:anime"], many_froms);
        expect(results.length).toEqual(1);
        expect(results[0][0]).toEqual("from");
        expect(results[0][1].groups).toBeDefined();
    });
    test("group the wombles under both t and w", () => {
        // Generate a track list with a lot of "from:..." variants, but none
        // of them containing a T or a W
        function random_title(length: number): string {
            var result = '';
            var characters = 'ABCDEFGHIJKLMNOPQRSUVXYZabcdefghijklmnopqrsuvxyz';
            var charactersLength = characters.length;
            for (var i = 0; i < length; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }
        let many_froms = many_tracks.map(
            track => ({ ...track, tags: { ...track.tags, "from": [random_title(2)] } })
        );
        many_froms[0].tags.from = ["The Wombles"];
        let results = grouper.group_tracks(["category:anime"], many_froms);
        expect(results.length).toEqual(1);
        expect(results[0][0]).toEqual("from");
        expect(results[0][1].groups).toBeDefined();
        expect(results[0][1].groups['T']).toEqual({"The Wombles": 1});
        expect(results[0][1].groups['W']).toEqual({"Wombles, The": 1});
    });
    test("show leftovers if some tracks don't match the suggested sections", () => {
        let results = grouper.group_tracks(["from:Macross"], many_tracks);
        expect(results.length).toBeGreaterThanOrEqual(2);
        expect(results[0][0]).toEqual("Macross");
        expect(results[0][1].filters).toBeDefined();
        expect(results[1][0]).toEqual("Tracks");
        expect(results[1][1].tracks).toBeDefined();
    });
});
