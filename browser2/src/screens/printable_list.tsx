import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import * as qrcode from "qrcode-generator";
import { shortest_tag, last_tag } from "../utils";


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
                {last_tag(track.tags as Dictionary<Array<string>>, "from")} ({shortest_tag(track.tags["use"])}){": "}
                {shortest_tag(track.tags.title)}
                {" - "}
                {track.tags["artist"] || "No Artist"} (
                {Math.floor(track.duration / 60)}m
                {Math.floor(track.duration % 60)})
            </p>
        ))}
    </Screen>
);
