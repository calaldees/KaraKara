import h from "hyperapp-jsx-pragma";
import { attachment_path } from "../utils";

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

export const Video = ({state, track, ...kwargs}) => (
    <video
        autoPlay={true}
        poster={attachment_path(state.root, track.attachments.image[0])}
        // ensure the video element gets re-created when <source> changes
        // and also when the podium switches from "preview" to "play" mode
        key={track.id + state.playing}
        {...kwargs}
    >
        {track.attachments.video.map(a =>
            <source src={attachment_path(state.root, a)} type={a.mime} />
        )}
        {track.attachments.subtitle?.map(a =>
            <track
                kind="subtitles"
                src={attachment_path(state.root, a)}
                default={true}
                label="English"
                srclang="en"
            />
        )}
    </video>
);
    