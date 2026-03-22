import { BackOr, Screen } from "@/components";
import { useWidescreen } from "@/hooks/widescreen";
import { PageContext } from "@/providers/page";
import { useContext } from "react";

import { ComingLater } from "./ComingLater";
import { ComingSoon } from "./ComingSoon";
import { MyEntries } from "./MyEntries";
import { NowPlaying } from "./NowPlaying";

export function Queue(): React.ReactElement {
    const widescreen = useWidescreen();
    const { roomName } = useContext(PageContext);

    return (
        <Screen
            className={"queue"}
            navLeft={!widescreen && <BackOr to={`/${roomName}`} />}
            title={"Now Playing"}
        >
            <NowPlaying />
            <ComingSoon />
            <ComingLater />
            <MyEntries />
        </Screen>
    );
}
