import { useContext } from "react";

import { BackToExplore, Screen } from "@/components";
import { ClientContext } from "@/providers/client";

import { ComingLater } from "./ComingLater";
import { ComingSoon } from "./ComingSoon";
import { MyEntries } from "./MyEntries";
import { NowPlaying } from "./NowPlaying";

export function Queue(): React.ReactElement {
    const { widescreen } = useContext(ClientContext);

    return (
        <Screen
            className={"queue"}
            navLeft={!widescreen && <BackToExplore />}
            title={"Now Playing"}
        >
            <NowPlaying />
            <ComingSoon />
            <ComingLater />
            <MyEntries />
        </Screen>
    );
}
