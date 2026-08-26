import { useContext, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackOr, ButtonRow, LyricsEditor, Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { ServerContext } from "@/providers/server";
import type { Subtitle } from "@/types";
import { attachment_path } from "@/utils";

export function SubtitlesEdit(): React.ReactElement {
    const { trackId, subtitleVariant, roomName } = useParams();
    const { tracks } = useContext(ServerContext);
    const navigate = useNavigate();
    const { request } = useApi();

    const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [isDirty, setIsDirty] = useState<boolean>(false);

    const track = trackId ? tracks[trackId] : undefined;

    useEffect(() => {
        if (!track || !subtitleVariant) {
            return;
        }
        const subtitleAttachment = track.attachments.subtitle?.find(
            (a) =>
                a.mime === "application/json" && a.variant === subtitleVariant,
        );
        if (!subtitleAttachment) {
            return;
        }

        request({
            url: attachment_path(subtitleAttachment),
            options: { credentials: "omit" },
            onAction: (result) => {
                setSubtitles(result);
                setIsLoading(false);
            },
            onException: () => {
                setSubtitles([]);
                setIsLoading(false);
            },
        });
    }, [request, track, subtitleVariant]);

    if (!trackId) throw Error("Can't get here?");
    if (!subtitleVariant) throw Error("Subtitle variant required");
    if (!track) return <div>No track with ID {trackId}</div>;

    const handleChanged = (newLines: Subtitle[]) => {
        setSubtitles(newLines);
        setIsDirty(true);
    };

    const audioUrl = (() => {
        if (!track) return undefined;

        // Prefer vocal variants
        const vocalAttachment = track.attachments.video.find(
            (a) => a.variant === "vocal",
        );
        if (vocalAttachment) {
            return attachment_path(vocalAttachment);
        }

        // Fall back to any video attachment
        if (track.attachments.video.length > 0) {
            return attachment_path(track.attachments.video[0]);
        }

        return undefined;
    })();

    const handleSave = () => {
        request({
            notify: `Saving subtitles...`,
            notify_ok: `Saved subtitles`,
            function: `edit/${trackId}/subs/${subtitleVariant}`,
            options: {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(subtitles),
            },
            onAction: () => {
                setIsDirty(false);
                void navigate(`/${roomName}/edit/${trackId}`);
            },
        });
    };

    return (
        <Screen
            navLeft={<BackOr to={`/${roomName}/edit/${trackId}`} />}
            title={`Edit Subs: ${track.tags.title[0]} (${subtitleVariant})`}
            footer={
                <ButtonRow>
                    <button
                        type="button"
                        onClick={handleSave}
                        disabled={!isDirty}
                    >
                        Save
                    </button>
                </ButtonRow>
            }
        >
            {isLoading ? (
                <div>Loading subtitles...</div>
            ) : (
                <LyricsEditor
                    lines={subtitles}
                    onChanged={handleChanged}
                    audioUrl={audioUrl}
                />
            )}
        </Screen>
    );
}
