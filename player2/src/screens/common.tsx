import h from "hyperapp-jsx-pragma";

export const AutoplayCountdown = ({
    state,
    show_if_disabled,
}: {
    state: State;
    show_if_disabled: boolean;
}): VNode =>
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
