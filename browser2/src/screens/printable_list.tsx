import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import * as qrcode from "qrcode-generator";


///////////////////////////////////////////////////////////////////////
// Utils

function shortest_tag(n: Array<string>): string {
    if (n === undefined) {
        return "";
    }
    if (typeof n === "string") {
        return n;
    }
    return n.sort((a, b) => a.length > b.length ? 1 : -1)[0];
}

/*
Given a tag set like

  from:macross
  macross:macross frontier

we want last_tag("from") to get "macross frontier"
*/
function last_tag(tags: Dictionary<Array<string>>, start: string): string {
    let tag = start;
    while(tags[tag]) {
        tag = tags[tag][0];
    }
    return tag;
}


///////////////////////////////////////////////////////////////////////
// Views

const PrintButtons = (): VNode => (
    <footer>
        <div class={"buttons"}>
            <button
                onclick={function (state) {
                    window.print();
                    return state;
                }}
            >
                Print
            </button>
        </div>
    </footer>
);

// You'd think this needs memoising to avoid heavy CPU load,
// but it actually renders in under 15ms (60fps)
function QrCode({text}: {text: string}): VNode {
    let qr = qrcode(3, 'L');
    qr.addData(text);
    qr.make();
    let data = qr.createDataURL(4);
    return <div class={"qr_container"}><img class={"qr_code"} src={data} /></div>;
}

export const PrintableList = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"track_list"}
        navLeft={<BackToExplore />}
        title={"Track List"}
        //navRight={}
        footer={<PrintButtons />}
    >
        To get an interactive track list on your phone, scan this QR code or
        visit {state.root} and use room name "{state.room_name}".
        <br/><QrCode text={state.root + "/browser2/#" + JSON.stringify({room_name: state.room_name})} />
        {Object.values(state.track_list).map((track: Track) => (
            <p>
                {last_tag(track.tags, "from")} ({shortest_tag(track.tags["use"])}){": "}
                {shortest_tag(track.tags.title)}
                {" - "}
                {track.tags["artist"] || "No Artist"} (
                {Math.floor(track.duration / 60)}m
                {Math.floor(track.duration % 60)})
            </p>
        ))}
    </Screen>
);
