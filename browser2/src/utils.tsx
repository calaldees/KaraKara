export function title_case(str) {
    return str
        .toLowerCase()
        .split(" ")
        .map(function (word) {
            return word.charAt(0).toUpperCase() + word.slice(1);
        })
        .join(" ");
}

export function attachment_url(path) {
    return "https://karakara.org.uk/files/" + path;
}

export function get_attachment(track: Track, type: string) {
    for (let i = 0; i < track.attachments.length; i++) {
        let a = track.attachments[i];
        if (a.type == type) {
            return attachment_url(a.location);
        }
    }
    return null;
}

export function shuffle(array) {
    let currentIndex = array.length;
    let temporaryValue, randomIndex;

    // While there remain elements to shuffle...
    while (0 !== currentIndex) {
        // Pick a remaining element...
        randomIndex = Math.floor(Math.random() * currentIndex);
        currentIndex -= 1;

        // And swap it with the current element.
        temporaryValue = array[currentIndex];
        array[currentIndex] = array[randomIndex];
        array[randomIndex] = temporaryValue;
    }

    return array;
}

export function http2ws(str: string) {
    return str.replace("https://", "wss://").replace("http://", "ws://");
}
