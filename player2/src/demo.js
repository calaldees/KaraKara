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
        "track": {
            "id": 2,
            "tags": {
                "title": choose(["Hello Song", "Let's Get To Burning", "Random Title #3", "The Song of My People", "Hello Song with a really long title: The Song of the Lengthening Words"]),
                "from": choose(["Animu", "That Show with the Things", "Demo Game", "Animu with a stupendously long name: The sequelising, the subtitle"])
            },
            "attachments": choose([
                [
                    {"type": "video", "location": "moo1.webm"},
                    {"type": "preview", "location": "moo1.webm"},
                    {"type": "thumbnail", "location": "moo1.jpg"}
                ],
                [
                    {"type": "video", "location": "moo2.webm"},
                    {"type": "preview", "location": "moo2.webm"},
                    {"type": "thumbnail", "location": "moo2.jpg"}
                ],
                [
                    {"type": "video", "location": "moo3.webm"},
                    {"type": "preview", "location": "moo3.webm"},
                    {"type": "thumbnail", "location": "moo3.jpg"}
                ],
            ]),
            "duration": choose([10, 20, 30, 12.34]),
            "lyrics": lyrics,
        },
        "performer_name": choose(["Vanilla", "Chocola", "Mint", "Coconut", "Cinamon", "Azuki", "Maple", "ReallyLongBadgeNameGuy"]),
        "total_duration": choose([90, 120, 180, 234]),
        "time_touched": ""+Math.random()
    };
}

export {random_track};
