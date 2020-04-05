import { h } from "hyperapp";

function _lineStyle(item, state: State) {
    // show subs a little faster, to counteract podium lag
    const ts = state.progress + state.settings["karakara.podium.soft_sub_lag"];
    if (!state.playing) return "future";
    if (item.text === "-") return "past";
    if (item.start < ts && item.end > ts) return "present";
    if (item.end < ts) return "past";
    if (item.start > ts) return "future";
}

export const Lyrics = ({ state }: { state: State }) => (
    <div className={"lyrics"}>
        <ol>
            {state.queue[0].track.srt_lyrics.map(item => (
                <li key={item.id} className={_lineStyle(item, state)}>
                    <span>{item.text}</span>
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
    state.settings["karakara.player.autoplay"] === 0 ? (
        show_if_disabled && <small>(autoplay disabled)</small>
    ) : (
        <small>
            (autoplay in{" "}
            {Math.ceil(
                state.settings["karakara.player.autoplay"] - state.progress,
            )}{" "}
            seconds)
        </small>
    );
