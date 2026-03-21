import { faPlay } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useParams } from "react-router-dom";

import styles from "./Readme.module.scss";

export function Readme(): React.ReactElement {
    const { roomName } = useParams();
    const root = window.location.protocol + "//" + window.location.host;

    return (
        <div className={styles.readme}>
            <h1>READ ME :)</h1>
            <ol>
                <li>
                    To avoid feedback loops, don't hold the microphone directly
                    in front of the speaker!
                </li>
                <li>
                    This admin laptop can drag &amp; drop to rearrange tracks in
                    the queue
                </li>
                <li>
                    Either use your phone (open <b>{root}</b> and enter room{" "}
                    <b>{roomName}</b>) or use the menu on the right to queue up
                    tracks.
                </li>
                <li>
                    Push the play button (
                    <FAIcon icon={faPlay} />) down below when you're ready to
                    start singing.
                </li>
            </ol>
        </div>
    );
}
