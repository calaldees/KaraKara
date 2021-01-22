import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";

const PrintButtons = () => (
    <footer>
        <div class={"buttons"}>
            <button onclick={function(state) {window.print(); return state;}}>
                Print
            </button>
        </div>
    </footer>
);

function t(n) {
    if (n === undefined) {return "";}
    if (typeof n === "string") {return n;}
    return n.sort((a, b) => (a.length > b.length))[0];
}
export const PrintableList = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"track_list"}
        navLeft={
            <a onclick={(state) => [{...state, screen: "explore"}]}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={"Track List"}
        //navRight={}
        footer={<PrintButtons />}
    >
        {/* fields = ['id_short'] + settings['karakara.print_tracks.fields'] */}
        {Object.values(state.track_list).map((track: Track) =>
            <p>
                <code>{track.id_short}</code>:{" "}
                {t(track.tags['from'])}{" "}
                ({t(track.tags['use'])}){": "}
                {track.title}{" - "}
                {track.tags['artist'] || "No Artist"}{" "}
                ({Math.floor(track.duration/60)}m{Math.floor(track.duration%60)})
            </p>
        )}
    </Screen>
);
