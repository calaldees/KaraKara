import { useContext } from "react";

import { BackOr, EventProgressBar, Screen } from "@/components";
import { useWidescreen } from "@/hooks/widescreen";
import { PageContext } from "@/providers/page";
import { RoomContext } from "@/providers/room";

import { ControlButtons } from "./ControlButtons";
import { Playlist } from "./Playlist";
import { Readme } from "./Readme";

function Control(): React.ReactElement {
    const widescreen = useWidescreen();
    const { roomName } = useContext(PageContext);
    const { queue } = useContext(RoomContext);

    return (
        <Screen
            className={"control"}
            navLeft={!widescreen && <BackOr to={`/${roomName}`} />}
            title={"Remote Control"}
            footer={<ControlButtons />}
        >
            {queue.length === 0 ? (
                <Readme />
            ) : (
                <>
                    <EventProgressBar />
                    <Playlist queue={queue} />
                </>
            )}
        </Screen>
    );
}

export default Control;
