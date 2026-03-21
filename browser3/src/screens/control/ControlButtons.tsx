import {
    faBackward,
    faForward,
    faForwardStep,
    faPlay,
    faStop,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";

import { useApi } from "@/hooks/api";

import { ButtonRow } from "@/components";

export function ControlButtons(): React.ReactElement {
    const { sendCommand, loading } = useApi();

    const buttons = {
        seek_backwards: <FAIcon icon={faBackward} />,
        seek_forwards: <FAIcon icon={faForward} />,
        play: <FAIcon icon={faPlay} />,
        stop: <FAIcon icon={faStop} />,
        skip: <FAIcon icon={faForwardStep} />,
    };

    return (
        <ButtonRow>
            {Object.entries(buttons).map(([command, icon]) => (
                <button
                    key={command}
                    type="button"
                    onClick={(_) => sendCommand(command)}
                    disabled={loading}
                >
                    {icon}
                </button>
            ))}
        </ButtonRow>
    );
}
