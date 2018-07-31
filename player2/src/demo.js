function choose(choices) {
    const index = Math.floor(Math.random() * choices.length);
    return choices[index];
}

const lyrics_lines = ("habatake sora e  takaku maiagare \n" +
    "RESUKYUU FAIAA GO! isoge!\n" +
    "hashiridase  yami o tsukinukero  RESUKYUU  yonde'ru ze \n" +
    "mukaikaze ni  kao o agero  soshite  me o hirake\n" +
    "dakishimero  chiisana sakebi o  RESUKYUU bokura wa ima \n" +
    "ai no tame  hitotsu ni nareru hazu sa\n" +
    "dakara motto motto  sou sa motto motto \n" +
    "tamashii yusaburu omoi  tokihanate \n" +
    "dakara motto motto  sou sa motto motto \n" +
    "WAN TSUU SURII  WAN TSUU SURII \n" +
    "bakuretsuteki ni BAANINGU SOURU\n").split("\n");
let lyrics = [];
for(let i=0; i<lyrics_lines.length; i++) {
    lyrics.push([(i+1)*3, lyrics_lines[i]]);
}

function random_track() {
    return {
        "track": choose([
            {
                "id": 1,
                "tags": {
                    "title": "OP",
                    "from": "Adventure Time"
                },
                "attachments": [
                    {"type": "video", "location": "adv.mp4"},
                    {"type": "preview", "location": "adv-pre.mp4"},
                    {"type": "thumbnail", "location": "adv.jpg"}
                ],
                "duration": 24,
                "lyrics": lyrics,
            },
            {
                "id": 2,
                "tags": {
                    "title": "The Only Thing I Know For Real",
                    "from": "Metal Gear Rising: Revengeance"
                },
                "attachments": [
                    {"type": "video", "location": "mgr.mp4"},
                    {"type": "preview", "location": "mgr-pre.mp4"},
                    {"type": "thumbnail", "location": "mgr.jpg"}
                ],
                "duration": 145,
                "lyrics": lyrics,
            },
            {
                "id": 3,
                "tags": {
                    "title": "Radical Dreamers",
                    "from": "Chronos Cross"
                },
                "attachments": [
                    {"type": "video", "location": "rad.mp4"},
                    {"type": "preview", "location": "rad-pre.mp4"},
                    {"type": "thumbnail", "location": "rad.jpg"}
                ],
                "duration": 279,
                "lyrics": lyrics,
            },
        ]),
        "performer_name": choose(["Vanilla", "Chocola", "Mint", "Coconut", "Cinamon", "Azuki", "Maple", "ReallyLongBadgeNameGuy"]),
        "total_duration": choose([90, 120, 180, 234]),
        "time_touched": ""+Math.random()
    };
}

export {random_track};
