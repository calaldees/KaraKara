/// <reference path='../src/browser.d.ts'/>

import * as utils from '../src/utils';

import * as fs from 'fs';
import { TrackList } from '../src/screens/track_list';
let state: State = JSON.parse(fs.readFileSync('./tests/state.json', 'utf8'));
state.track_list = JSON.parse(fs.readFileSync('./tests/tracks.json', 'utf8'));
state.queue = JSON.parse(fs.readFileSync('./tests/queue.json', 'utf8'));


///////////////////////////////////////////////////////////////////////
// Misc one-off utils

describe('attachment_path', () => {
  const attachment = state.track_list["track_id_1"].attachments.video[0];
  test('should basically work', () => {
    expect(utils.attachment_path("http://example.com", attachment))
      .toEqual("http://example.com/files/f/foo.mp4");
  });
});

describe('shuffle', () => {
  test('should basically work', () => {
    expect(utils.shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
      .not.toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 0]);
  });
});

describe('mqtt_login_info', () => {
  test('should basically work', () => {
    expect(utils.mqtt_login_info(state)).toEqual({
      "url": "wss://example.com/mqtt",
      "username": "test",
      "password": "password-example",
    });
  });
});

describe('short_date', () => {
  test('should basically work', () => {
    expect(utils.short_date("2021-01-03T14:00:00")).toEqual("14:00");
  });
});

describe('percent', () => {
  test('should basically work', () => {
    expect(utils.percent(0, 2)).toEqual("0%");
    expect(utils.percent(1, 2)).toEqual("50%");
    expect(utils.percent(2, 2)).toEqual("100%");
    expect(utils.percent(1, 3)).toEqual("33%");
  });
});

describe('is_my_song', () => {
  test('match based only on session ID', () => {
    expect(utils.is_my_song(
      { session_id: "sess1", performer_name: "Jim" },
      { session_owner: "sess1", performer_name: "Bob" },
    )).toEqual(true);
  });
  test('match based only on performer name', () => {
    expect(utils.is_my_song(
      { session_id: "sess1", performer_name: "Jim" },
      { session_owner: "sess2", performer_name: "Jim" },
    )).toEqual(true);
  });
  test('match based on both', () => {
    expect(utils.is_my_song(
      { session_id: "sess1", performer_name: "Jim" },
      { session_owner: "sess1", performer_name: "Jim" },
    )).toEqual(true);
  });
  test('no-match based only on neither', () => {
    expect(utils.is_my_song(
      { session_id: "sess1", performer_name: "Jim" },
      { session_owner: "sess2", performer_name: "Bob" },
    )).toEqual(false);
  });
  test('no-match when track is missing', () => {
    expect(utils.is_my_song(
      { session_id: "sess1", performer_name: "Jim" },
      undefined,
    )).toEqual(false);
  });
});

describe('shortest_tag', () => {
  test('should handle undefined', () => {
    expect(utils.shortest_tag(undefined)).toEqual("");
  });
  test('should handle a list', () => {
    expect(utils.shortest_tag(["donkey", "foo", "cake"])).toEqual("foo");
  });
});

describe('last_tag', () => {
  test('should basically work', () => {
    expect(utils.last_tag({"from": ["Macross"], "Macross": ["Do You Remember Love?"]}, "from"))
      .toEqual("Do You Remember Love?");
  });
  test('handle invalid requests', () => {
    expect(utils.last_tag({"from": ["Macross"], "Macross": ["Do You Remember Love?"]}, "cake"))
      .toEqual("cake");
  });
});


///////////////////////////////////////////////////////////////////////
// Settings

describe('flatten_setting', () => {
  test('should handle strings', () => {
    expect(utils.flatten_setting("foo")).toEqual("foo");
  });
  test('should handle numbers', () => {
    expect(utils.flatten_setting(42)).toEqual("42");
  });
  test('should handle arrays', () => {
    expect(utils.flatten_setting(["foo", "bar"])).toEqual("[foo,bar]");
  });
});

describe('flatten_settings', () => {
  test('should basically work', () => {
    expect(utils.flatten_settings(state.settings)).toEqual([
      ["test.string", "foo"],
      ["test.int", "42"],
      ["test.array", "[yo,ho,ho]"],
    ]);
  });
});


///////////////////////////////////////////////////////////////////////
// Tracks

describe('track_info', () => {
  test('should basically work', () => {
    expect(utils.track_info(
      [],
      {
        tags: {
          "title": ["Fake Track Name"],
          "from": ["Macross"],
          "Macross": ["Do You Remember Love?"],
          "use": ["opening", "op1"],
          "length": ["short"],
        }
      }
    ))
      .toEqual("Macross - opening, op1 - short");
  });
  test('searching for a series should avoid showing that series', () => {
    expect(utils.track_info(
      ["from:Macross"],
      {
        tags: {
          "title": ["Fake Track Name"],
          "from": ["Macross"],
          "Macross": ["Do You Remember Love?"],
          "use": ["opening", "op1"],
          "length": ["short"],
        }
      }
    ))
      .toEqual("opening, op1 - short");
  });
  test('avoid duplicating the title in the info', () => {
    expect(utils.track_info(
      [],
      {
        tags: {
          "title": ["Fake Track Name"],
          "from": ["Fake Track Name"],
          "use": ["opening", "op1"],
          "length": ["short"],
        }
      }
    ))
      .toEqual("opening, op1 - short");
  });
  test('some categories have specific rules', () => {
    expect(utils.track_info(
      [],
      {
        tags: {
          "title": ["Fake Track Name"],
          "artist": ["Billy Rock"],
          "category": ["jpop"],
        }
      }
    ))
      .toEqual("Billy Rock");
  });
  test('unrecognised categories should use default rules', () => {
    expect(utils.track_info(
      [],
      {
        tags: {
          "title": ["Fake Track Name"],
          "from": ["Macross"],
          "category": ["example"],
          "use": ["opening", "op1"],
          "length": ["short"],
        }
      }
    ))
      .toEqual("Macross - opening, op1 - short");
  });
});


///////////////////////////////////////////////////////////////////////
// Searching

const tracks = Object.values(state.track_list);

describe('apply_tags', () => {
  test('empty query returns full list', () => {
    expect(utils.apply_tags(tracks, []).map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
  test('query for a tag returns the right thing', () => {
    expect(utils.apply_tags(tracks, ["from:Gundam"]).map(track => track.id))
      .toEqual([
        "track_id_2",
      ]);
  });
  test('query for a non-existing tag returns nothing', () => {
    expect(utils.apply_tags(tracks, ["from:asdfa"]).map(track => track.id))
      .toEqual([
      ]);
  });
});

describe('apply_search', () => {
  test('empty query returns full list', () => {
    expect(utils.apply_search(tracks, "").map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
  test('query for a string returns the right thing', () => {
    expect(utils.apply_search(tracks, "Love").map(track => track.id))
      .toEqual([
        "track_id_1",
      ]);
  });
  test('query for a non-existing string returns nothing', () => {
    expect(utils.apply_search(tracks, "asdgadfgds").map(track => track.id))
      .toEqual([
      ]);
  });
});

describe('apply_hidden', () => {
  test('empty query returns full list', () => {
    expect(utils.apply_hidden(tracks, []).map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
  test('silent_hidden top-level tag hides a track, even if it has other tags', () => {
    expect(utils.apply_hidden(tracks, ["retro"]).map(track => track.id))
      .toEqual([
        "track_id_2",
      ]);
  });
  test('invalid silent_hidden top-level tag does nothing', () => {
    expect(utils.apply_hidden(tracks, ["asdfasd"]).map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
  test("silent_hidden=cateogory:anime doesn't hide a track with category:anime+category:cartoon", () => {
    expect(utils.apply_hidden(tracks, ["category:anime"]).map(track => track.id))
      .toEqual([
        "track_id_2",
      ]);
  });
  test("silent_hidden=cateogory:anime,category:cartoon does hide a track with category:anime+category:cartoon", () => {
    expect(utils.apply_hidden(tracks, ["category:anime", "category:cartoon"]).map(track => track.id))
      .toEqual([
      ]);
  });
  test('invalid silent_hidden tag key does nothing', () => {
    expect(utils.apply_hidden(tracks, ["asdfasd:acsdsa"]).map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
  test('invalid silent_hidden tag value does nothing', () => {
    expect(utils.apply_hidden(tracks, ["category:asdfasd"]).map(track => track.id))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
});

// find_tracks = apply_hidden + apply_tags(forced) + apply_tags(user) + apply_search
// I want one function which does it all for performance testing
describe('find_tracks', () => {
  // generate a large dataset, but do it outside of the test
  // so that it doesn't contribute to the test's performance
  let big_tracks: Dictionary<Track> = {};
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
      lyrics: [""]
    };
  }
  let big_state: State = {
    ...state,
    settings: {
      "karakara.search.tag.silent_forced": ["retro"],
      "karakara.search.tag.silent_hidden": ["todo", "delete", "broken"],
    },
    filters: ["category:anime"],
    search: "mac",
    track_list: big_tracks,
  };
  test("Performance is OK with many active filters", () => {
    // check that even though we have all the types of filters, and
    // none of them are narrowing down the list at all, we're still
    // doing ok
    let tracks = utils.find_tracks(big_state);
    expect(tracks.length).toEqual(10000);
  });
});


///////////////////////////////////////////////////////////////////////
// Track List Rendering

describe('choose_section_names', () => {
  const summary = {
    macross: {
      "movie 1": 2,
      "movie 2": 1,
    },
    pokemon: {
      "johto": 2
    },
  };
  test('with no filters, return default sections', () => {
    expect(utils.choose_section_names([], summary))
      .toEqual(["category", "vocalstyle", "vocaltrack", "lang"]);
  });
  test('with a known filter, return known sections', () => {
    expect(utils.choose_section_names(["category:jpop"], summary))
      .toEqual(["artist", "from"]);
  });
  test('when searching for a tag which has children, show that tag as the parent', () => {
    expect(utils.choose_section_names(["from:macross"], summary))
      .toEqual(["macross"]);
  });
  test("when searching for a tag which doesn't have children, show full summary", () => {
    expect(utils.choose_section_names(["category:popular"], summary))
      .toEqual(["macross", "pokemon"]);
  });
});

describe('summarise_tags', () => {
  test('should basically work', () => {
    expect(utils.summarise_tags(Object.values(state.track_list)))
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

describe('calculate_list_sections', () => {
  let many_tracks: Array<Track> = [];
  for (let i = 0; i < 1000; i++) {
    many_tracks.push(state.track_list["track_id_1"]);
  }
  many_tracks.push(state.track_list["track_id_2"]);

  test("Show 'No Results' if there are no tracks", () => {
    let results = utils.calculate_list_sections([], []);
    expect(results.length).toEqual(1);
    expect(results[0][0]).toEqual("No Results");
  });
  test("Show all tracks if there are only a few results", () => {
    let results = utils.calculate_list_sections(
      [],
      [state.track_list["track_id_1"], state.track_list["track_id_2"]]
    );
    expect(results.length).toEqual(1);
    expect(results[0][0]).toEqual("");
    expect(results[0][1].tracks).toBeDefined();
  });
  test("With many tracks and no filters, prompt for default filters", () => {
    let results = utils.calculate_list_sections([], many_tracks);
    expect(results.length).toBeGreaterThanOrEqual(1);
    expect(results[0][0]).toEqual("category");
    expect(results[0][1].filters).toBeDefined();
  });
  test("With many tracks and a filter, prompt for relevant sub-filters", () => {
    let results = utils.calculate_list_sections(["category:anime"], many_tracks);
    expect(results.length).toBeGreaterThanOrEqual(1);
    expect(results[0][0]).toEqual("from");
    expect(results[0][1].filters).toBeDefined();
  });
  test("Show grouped filters if a tag has a ton of children", () => {
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
    let results = utils.calculate_list_sections(["category:anime"], many_froms);
    expect(results.length).toEqual(1);
    expect(results[0][0]).toEqual("from");
    expect(results[0][1].groups).toBeDefined();
  });
  test("Show leftovers if some tracks don't match the suggested sections", () => {
    let results = utils.calculate_list_sections(["from:Macross"], many_tracks);
    expect(results.length).toBeGreaterThanOrEqual(2);
    expect(results[0][0]).toEqual("Macross");
    expect(results[0][1].filters).toBeDefined();
    expect(results[1][0]).toEqual("Tracks");
    expect(results[1][1].tracks).toBeDefined();
  });
});
