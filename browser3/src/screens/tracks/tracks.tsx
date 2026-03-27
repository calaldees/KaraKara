import {
    faCircleChevronLeft,
    faListOl,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { type ReactElement, useContext } from "react";
import { Link, useParams } from "react-router-dom";

import { Screen } from "@/components";
import { useWidescreen } from "@/hooks/widescreen";
import { ClientContext } from "@/providers/client";
import { ExploreContext, ExploreProvider } from "@/providers/explore";
import { RoomContext } from "@/providers/room";

import { AdminButtons } from "./AdminButtons";
import { Explorer } from "./Explorer";

function TrackList(): ReactElement {
    return (
        <ExploreProvider>
            <TrackListInternal />
        </ExploreProvider>
    );
}

export default TrackList;

function TrackListInternal(): ReactElement {
    const { isAdmin } = useContext(RoomContext);
    const { booth } = useContext(ClientContext);
    const widescreen = useWidescreen();
    const { filters, setFilters } = useContext(ExploreContext);
    const { roomName } = useParams();

    return (
        <Screen
            navLeft={
                filters.length > 0 && (
                    <FAIcon
                        icon={faCircleChevronLeft}
                        onClick={(_) => setFilters(filters.slice(0, -1))}
                        data-cy="back"
                    />
                )
            }
            title={"Explore Tracks"}
            navRight={
                !widescreen && (
                    <Link to={`/${roomName}/queue`} data-cy="queue">
                        <FAIcon icon={faListOl} />
                    </Link>
                )
            }
            footer={isAdmin && !booth && <AdminButtons />}
        >
            <Explorer />
        </Screen>
    );
}
