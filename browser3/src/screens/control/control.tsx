import { useContext } from "react";

import { BackToExplore, EventProgressBar, Screen } from "@/components";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";

import { ControlButtons } from "./ControlButtons";
import { Playlist } from "./Playlist";
import { Readme } from "./Readme";

export function Control(): React.ReactElement {
    const { widescreen } = useContext(ClientContext);
    const { queue } = useContext(RoomContext);

    return (
        <Screen
            className={"control"}
            navLeft={!widescreen && <BackToExplore />}
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
