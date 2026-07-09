import {
    faCircleChevronRight,
    faEdit,
    faPlus,
    faTrash,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackOr, ButtonRow, List, ListItem, Screen } from "@/components";
import { ServerContext } from "@/providers/server";
import type { Track } from "@/types";
import { unique } from "@/utils";

export function TrackEdit(): React.ReactElement {
    const { trackId } = useParams();
    const { tracks } = useContext(ServerContext);
    if (!trackId) throw Error("Can't get here?");
    const track = tracks[trackId];
    if (!track) return <div>No track with ID {trackId}</div>;

    return <TrackEditInternal key={trackId} track={track} />;
}

function TrackEditInternal({ track }: { track: Track }): React.ReactElement {
    const { roomName } = useParams();
    const navigate = useNavigate();

    const subtitleVariants = unique(
        track.attachments.subtitle?.map((a) => a.variant) ?? [],
    );
    const videoVariants = unique(track.attachments.video.map((a) => a.variant));

    const handleAddSubtitle = () => {
        const variant = prompt("Enter subtitle variant name:");
        if (variant) {
            // TODO: Implement API call to add subtitle variant
            console.log("Add subtitle variant:", variant);
        }
    };

    const handleRenameSubtitle = (variant: string) => {
        const newVariant = prompt("Enter new subtitle variant name:", variant);
        if (newVariant && newVariant !== variant) {
            // TODO: Implement API call to rename subtitle variant
            console.log("Rename subtitle variant:", variant, "to", newVariant);
        }
    };

    const handleAddMedia = () => {
        const variant = prompt("Enter media variant name:");
        if (variant) {
            // TODO: Implement API call to add media variant
            console.log("Add media variant:", variant);
        }
    };

    const handleRenameMedia = (variant: string) => {
        const newVariant = prompt("Enter new media variant name:", variant);
        if (newVariant && newVariant !== variant) {
            // TODO: Implement API call to rename media variant
            console.log("Rename media variant:", variant, "to", newVariant);
        }
    };

    const handleDeleteMedia = (variant: string) => {
        if (confirm(`Delete media variant "${variant}"?`)) {
            // TODO: Implement API call to delete media variant
            console.log("Delete media variant:", variant);
        }
    };

    return (
        <Screen
            navLeft={<BackOr to={`/${roomName}/tracks/${track.id}`} />}
            title={`Edit: ${track.tags.title[0]}`}
        >
            <h2>Track</h2>
            <input type="text" value={track.id} disabled={true} />
            <List>
                <ListItem
                    title="Edit Tags"
                    onClick={(_) =>
                        void navigate(`/${roomName}/edit/${track.id}/tags`)
                    }
                    action={<FAIcon icon={faCircleChevronRight} />}
                />
            </List>

            <h2>Subtitles</h2>
            <List>
                {subtitleVariants.map((variant) => (
                    <ListItem
                        key={`subtitle-${variant}`}
                        title={variant}
                        //info={"Subtitle"}
                        onClick={(_) =>
                            void navigate(
                                `/${roomName}/edit/${track.id}/subtitles/${variant}`,
                            )
                        }
                        action={
                            <ButtonRow>
                                <FAIcon
                                    icon={faEdit}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleRenameSubtitle(variant);
                                    }}
                                    role="button"
                                    aria-label="Rename Subtitle"
                                />
                                <FAIcon icon={faCircleChevronRight} />
                            </ButtonRow>
                        }
                    />
                ))}
                <ListItem
                    onClick={handleAddSubtitle}
                    title={"Add new subtitle"}
                    action={<FAIcon icon={faPlus} />}
                />
            </List>

            <h2>Media</h2>
            <List>
                {videoVariants.map((variant) => (
                    <ListItem
                        key={`media-${variant}`}
                        title={variant}
                        count={"mp4"}
                        action={
                            <ButtonRow>
                                <FAIcon
                                    icon={faEdit}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleRenameMedia(variant);
                                    }}
                                    role="button"
                                    aria-label="Rename Media"
                                />
                                <FAIcon
                                    icon={faTrash}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteMedia(variant);
                                    }}
                                    role="button"
                                    aria-label="Delete Media"
                                />
                            </ButtonRow>
                        }
                    />
                ))}
                <ListItem
                    onClick={handleAddMedia}
                    title={"Add new media"}
                    action={<FAIcon icon={faPlus} />}
                />
            </List>
        </Screen>
    );
}
