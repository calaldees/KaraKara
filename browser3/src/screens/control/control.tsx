import { useContext } from "react";

import { BackToExplore, EventProgressBar, Screen } from "@/components";
import { useWidescreen } from "@/hooks/widescreen";
import { RoomContext } from "@/providers/room";

import { ControlButtons } from "./ControlButtons";
import { Playlist } from "./Playlist";
import { Readme } from "./Readme";

export function Control(): React.ReactElement {
    const widescreen = useWidescreen();
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
