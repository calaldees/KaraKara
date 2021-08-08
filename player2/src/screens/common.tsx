import h from "hyperapp-jsx-pragma";

function _lineStyle(item: SrtLine, state: State) {
    // show subs a little faster, to counteract podium lag
    const ts = state.progress + state.settings["karakara.podium.soft_sub_lag"];

    if (!state.playing) return "future";
    if (item.text === "-") return "past";
    if (item.start < ts && item.end > ts) return "present";
    if (item.end < ts) return "past";
    if (item.start > ts) return "future";
}

function _lyricStyle(lyrics: Array<SrtLine>) {
    // TODO: check current lyric alignment instead of first lyric?
    if (lyrics && lyrics.length && lyrics[0].text.startsWith("{\\a6}")) {
        return "top lyrics";
    }
    return "bottom lyrics";
}

export const Lyrics = ({ state }: { state: State }) => (
    <div class={_lyricStyle(state.queue[0].track.lyrics)}>
        <ol>
            {state.queue[0].track.lyrics &&
                state.queue[0].track.lyrics.map((item) => (
                    <li key={item.id} class={_lineStyle(item, state)}>
                        <span>{item.text.replace(/^\{.*?\}/, "")}</span>
                    </li>
                ))}
        </ol>
    </div>
);

export const AutoplayCountdown = ({
    state,
    show_if_disabled,
}: {
    state: State;
    show_if_disabled: boolean;
}) =>
    state.settings["karakara.player.autoplay.seconds"] === 0 ? (
        show_if_disabled && <small>(autoplay disabled)</small>
    ) : (
        <small>
            (autoplay in{" "}
            {Math.ceil(
                state.settings["karakara.player.autoplay.seconds"] -
                    state.progress,
            )}{" "}
            seconds)
        </small>
    );
