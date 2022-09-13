/// <reference path='../src/browser.d.ts'/>

import * as utils from '../src/utils';

import * as fs from 'fs';
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

describe('time_until', () => {
    test('should basically work', () => {
        expect(utils.time_until((Date.now()/1000) + 120)).toEqual("In 2 mins");
        expect(utils.time_until((Date.now()/1000) + 60)).toEqual("In 1 min");
        expect(utils.time_until((Date.now()/1000) + 30)).toEqual("In 30 secs");
        expect(utils.time_until((Date.now()/1000) + 1)).toEqual("Now");
        expect(utils.time_until(null)).toEqual("");
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
            { session_id: "sess1", performer_name: "Bob" },
        )).toEqual(true);
    });
    test('match based only on performer name', () => {
        expect(utils.is_my_song(
            { session_id: "sess1", performer_name: "Jim" },
            { session_id: "sess2", performer_name: "Jim" },
        )).toEqual(true);
    });
    test('match based on both', () => {
        expect(utils.is_my_song(
            { session_id: "sess1", performer_name: "Jim" },
            { session_id: "sess1", performer_name: "Jim" },
        )).toEqual(true);
    });
    test('no-match based only on neither', () => {
        expect(utils.is_my_song(
            { session_id: "sess1", performer_name: "Jim" },
            { session_id: "sess2", performer_name: "Bob" },
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
        expect(utils.last_tag({ "from": ["Macross"], "Macross": ["Do You Remember Love?"] }, "from"))
            .toEqual("Do You Remember Love?");
    });
    test('handle invalid requests', () => {
        expect(utils.last_tag({ "from": ["Macross"], "Macross": ["Do You Remember Love?"] }, "cake"))
            .toEqual("cake");
    });
});

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

describe('copy_type', () => {
    test('default', () => {
        expect(utils.copy_type("Macross", "Gundam")).toEqual("Gundam");
        expect(utils.copy_type("Macross", "")).toEqual("");
    });
    test('array', () => {
        expect(utils.copy_type(["Macross", "Gundam"], "Gundam,Cake")).toEqual(["Gundam", "Cake"]);
        expect(utils.copy_type(["Macross", "Gundam"], "")).toEqual([]);
    });
    test('int', () => {
        expect(utils.copy_type(2, "42")).toEqual(42);
    });
    test('float', () => {
        expect(utils.copy_type(12.34, "43.21")).toEqual(43.21);
    });
});
