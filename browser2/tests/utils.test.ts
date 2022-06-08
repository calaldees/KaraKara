/// <reference path='../src/browser.d.ts'/>

import * as utils from '../src/utils';

import * as fs from 'fs';
let state: State = JSON.parse(fs.readFileSync('./tests/state.json', 'utf8'));
state.track_list = JSON.parse(fs.readFileSync('./tests/tracks.json', 'utf8'));
state.queue = JSON.parse(fs.readFileSync('./tests/queue.json', 'utf8'));

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

describe('short_date', () => {
  test('should basically work', () => {
    expect(utils.short_date("2021-01-03T14:00:00")).toEqual("14:00");
  });
});

describe('is_my_song', () => {
  test('should match based on session ID', () => {
    expect(utils.is_my_song(state, state.queue[0])).toEqual(true);
  });
  test('should not-match based on session ID', () => {
    expect(utils.is_my_song(state, state.queue[1])).toEqual(false);
  });
});

describe('percent', () => {
  test('should basically work', () => {
    expect(utils.percent(1, 2)).toEqual("50%");
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
    expect(utils.last_tag(state.track_list["track_id_1"].tags, "from"))
      .toEqual("Do You Remember Love?");
  });
});

describe('track_info', () => {
  test('should basically work', () => {
    expect(utils.track_info(
      { filters: [] },
      state.track_list["track_id_1"]
    ))
      .toEqual("Macross - opening, op1 - short");
  });
});

// shortcut to make make tests shorter
function find_tracks(
  hidden: Array<string>,
  forced: Array<string>,
  filters: Array<string>,
  search: string,
): Array<string> {
  return utils.find_tracks(
    state.track_list,
    hidden,
    forced,
    filters,
    search
  ).map(track => track.id)
}
// each filtering method (hidden, forced, filters, search) acts
// independently to remove tracks from the list (in theory we
// could have four separate functions, each of which takes a
// list of tracks and returns a shorter list), so in theory there
// should be no need to test combinations of filter methods...
describe('find_tracks (empty)', () => {
  test('empty query should return all tracks', () => {
    expect(find_tracks([], [], [], ""))
      .toEqual([
        "track_id_1",
        "track_id_2",
      ]);
  });
});
describe('find_tracks (filters)', () => {
  test('query for a tag returns the right thing', () => {
    expect(find_tracks([], [], ["from:Gundam"], ""))
      .toEqual([
        "track_id_2",
      ]);
  });
});
describe('find_tracks (search)', () => {
  test('query for a string returns the right thing', () => {
    expect(find_tracks([], [], [], "Love"))
      .toEqual([
        "track_id_1",
      ]);
  });
});
describe('find_tracks (hidden)', () => {
  test('silent_hidden top-level tag hides a track, even if it has other tags', () => {
    expect(find_tracks(["retro"], [], [], ""))
      .toEqual([
        "track_id_2",
      ]);
  });
  test("silent_hidden=cateogory:anime doesn't hide a track with category:anime+category:cartoon", () => {
    expect(find_tracks(["category:anime"], [], [], ""))
      .toEqual([
        "track_id_2",
      ]);
  });
  test("silent_hidden=cateogory:anime,category:cartoon does hide a track with category:anime+category:cartoon", () => {
    expect(find_tracks(["category:anime", "category:cartoon"], [], [], ""))
      .toEqual([
      ]);
  });
});
describe('find_tracks (forced)', () => {
  test('silent_forced basically works', () => {
    expect(find_tracks([], ["retro"], [], ""))
      .toEqual([
        "track_id_1",
      ]);
  });
});

describe('choose_section_names', () => {
  const groups = {
    macross: ["movie 1", "movie 2"],
    pokemon: ["johto"],
  };
  test('with no filters, return default sections', () => {
    expect(utils.choose_section_names({ filters: [] }, groups))
      .toEqual(["category", "vocalstyle", "vocaltrack", "lang"]);
  });
  test('with a known filter, return known sections', () => {
    expect(utils.choose_section_names({ filters: ["category:jpop"] }, groups))
      .toEqual(["artist", "from"]);
  });
  test('when searching for a tag which has children', () => {
    expect(utils.choose_section_names({ filters: ["from:macross"] }, groups))
      .toEqual(["macross"]);
  });
  // is this right??
  test('when searching for a tag which doesn\'t have children', () => {
    expect(utils.choose_section_names({ filters: ["from:gundam"] }, groups))
      .toEqual(["macross", "pokemon"]);
  });
});

describe('find_all_tags', () => {
  test('should basically work', () => {
    expect(utils.find_all_tags(Object.values(state.track_list)))
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
