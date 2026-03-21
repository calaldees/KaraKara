import { BackToExplore, Screen } from "@/components";
import { useWidescreen } from "@/hooks/widescreen";

import { ComingLater } from "./ComingLater";
import { ComingSoon } from "./ComingSoon";
import { MyEntries } from "./MyEntries";
import { NowPlaying } from "./NowPlaying";

export function Queue(): React.ReactElement {
    const widescreen = useWidescreen();

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
