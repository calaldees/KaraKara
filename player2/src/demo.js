import Subtitle from 'subtitle';

function choose(choices) {
    const index = Math.floor(Math.random() * choices.length);
    return choices[index];
}

function get_lyrics(srt) {
    let xhr = new XMLHttpRequest();
    let data = "";
    xhr.open('GET', "https://files.shishnet.org/karakara-demo/"+srt, false);
    xhr.onload = function(e) {
        data = e.target.responseText;
    };
    xhr.send();
    return Subtitle.parse(data);
}

function random_track() {
    return {
        "track": choose([
            {
                "id": 1,
                "tags": {
                    "title": "OP",
                    "from": "Adventure Time",
                    "artist": "An Artist",
                    "contributor": "choco"
                },
                "attachments": [
                    {"type": "video", "location": "adv.mp4"},
                    {"type": "preview", "location": "adv-pre.mp4"},
                    {"type": "srt", "location": "adv.srt"},
                    {"type": "thumbnail", "location": "adv.jpg"}
                ],
                "duration": 24,
                "lyrics": get_lyrics("adv.srt"),
            },
            {
                "id": 2,
                "tags": {
                    "title": "The Only Thing I Know For Real",
                    "from": "Metal Gear Rising: Revengeance",
                    "artist": "An Artist",
                    "contributor": "choco"
                },
                "attachments": [
                    {"type": "video", "location": "mgr.mp4"},
                    {"type": "preview", "location": "mgr-pre.mp4"},
                    {"type": "srt", "location": "mgr.srt"},
                    {"type": "thumbnail", "location": "mgr.jpg"}
                ],
                "duration": 145,
                "lyrics": get_lyrics("mgr.srt"),
            },
            {
                "id": 3,
                "tags": {
                    "title": "Radical Dreamers",
                    "from": "Chrono Cross",
                    "artist": "An Artist",
                    "contributor": "choco"
                },
                "attachments": [
                    {"type": "video", "location": "rad.mp4"},
                    {"type": "preview", "location": "rad-pre.mp4"},
                    {"type": "srt", "location": "rad.srt"},
                    {"type": "thumbnail", "location": "rad.jpg"}
                ],
                "duration": 279,
                "lyrics": get_lyrics("rad.srt"),
            },
        ]),
        "performer_name": choose(["Vanilla", "Chocola", "Mint", "Coconut", "Cinamon", "Azuki", "Maple", "ReallyLongBadgeNameGuy"]),
        "total_duration": choose([90, 120, 180, 234]),
        "time_touched": ""+Math.random()
    };
}

export {random_track};
