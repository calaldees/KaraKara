import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./base";

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
        <br/>{state.qr_data && <img class={"qr_code"} src={state.qr_data} />}
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
