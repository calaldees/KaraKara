import { faCircleChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { ListItem, Thumb } from "@/components";
import { PageContext } from "@/providers/page";
import type { Track } from "@/types";
import { track_info } from "@/utils";

export function TrackItem({
    track,
    filters,
}: {
    track: Track;
    filters: string[];
}): React.ReactElement {
    const { roomName, navigate } = useContext(PageContext);

    let extra = "";
    if (
        track.tags.vocaltrack?.includes("on") &&
        track.tags.vocaltrack?.includes("off")
    ) {
        extra = " (Vocal + Instr.)";
    } else if (track.tags.vocaltrack?.includes("off")) {
        extra = " (Instrumental)";
    }

    return (
        <ListItem
            thumb={<Thumb track={track} />}
            title={`${track.tags.title[0]}${extra}`}
            info={track_info(filters, track)}
            action={<FAIcon icon={faCircleChevronRight} />}
            onClick={(_) => void navigate(`/${roomName}/tracks/${track.id}`)}
        />
    );
}
