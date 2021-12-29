import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./base";
import * as qrcode from "qrcode-generator";

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

function t(n) {
    if (n === undefined) {
        return "";
    }
    if (typeof n === "string") {
        return n;
    }
    return n.sort((a, b) => a.length > b.length)[0];
}

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
        <br/><QrCode text={state.root + "/browser2/?r=" + state.room_name} />
        {/* fields = ['id_short'] + settings['karakara.print_tracks.fields'] */}
        {Object.values(state.track_list).map((track: Track) => (
            <p>
                <code>
                    {track.id.substring(
                        0,
                        state.settings[
                            "karakara.print_tracks.short_id_length"
                        ] || 6,
                    )}
                </code>
                {": "}
                {t(track.tags["from"])} ({t(track.tags["use"])}){": "}
                {t(track.tags["title"])}
                {" - "}
                {track.tags["artist"] || "No Artist"} (
                {Math.floor(track.duration / 60)}m
                {Math.floor(track.duration % 60)})
            </p>
        ))}
    </Screen>
);
