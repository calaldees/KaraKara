import { useContext, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { BackOr, ButtonRow, Screen, TagsEditor } from "@/components";
import { useApi } from "@/hooks/api";
import { ServerContext } from "@/providers/server";
import { sort_tag_keys } from "@/utils/browser";

// Tags that should use checkbox editors with values from the database
const CHECKBOX_TAG_KEYS = [
    "category",
    "use",
    "vocaltrack",
    "vocalstyle",
    "lang",
];

export function TagsEdit(): React.ReactElement {
    const { trackId, roomName } = useParams();
    const { tracks } = useContext(ServerContext);
    const navigate = useNavigate();
    const { request } = useApi();

    const [pendingChanges, setPendingChanges] = useState<
        Record<string, string[]>
    >({});

    const track = trackId ? tracks[trackId] : undefined;

    // Gather all possible values for checkbox-based tags from all tracks
    const possibleValuesByKey = useMemo(() => {
        const result: Record<string, Set<string>> = {};

        CHECKBOX_TAG_KEYS.forEach((key) => {
            result[key] = new Set<string>();
        });

        Object.values(tracks).forEach((t) => {
            CHECKBOX_TAG_KEYS.forEach((key) => {
                const values = t.tags[key];
                if (values) {
                    values.forEach((value) => result[key].add(value));
                }
            });
        });

        return Object.fromEntries(
            Object.entries(result).map(([key, set]) => [
                key,
                Array.from(set).sort(),
            ]),
        );
    }, [tracks]);

    const editableTags = useMemo(() => {
        if (!track) return [];
        return sort_tag_keys(Object.keys(track.tags)).filter(
            (key) => !key.startsWith("_"),
        );
    }, [track]);

    const currentTags = useMemo(() => {
        if (!track) return {};
        const tags: Record<string, string[]> = {};
        editableTags.forEach((key) => {
            tags[key] = pendingChanges[key] ?? track.tags[key] ?? [];
        });
        return tags;
    }, [editableTags, pendingChanges, track]);

    const isDirty = Object.keys(pendingChanges).length > 0;

    if (!trackId) throw Error("Can't get here?");
    if (!track) return <div>No track with ID {trackId}</div>;

    const handleChanged = (tagKey: string, newValues: string[]) => {
        setPendingChanges((prev) => ({
            ...prev,
            [tagKey]: newValues,
        }));
    };

    const handleSave = () => {
        // Build the complete tags object with pending changes applied
        const updatedTags: Record<string, string[]> = {};
        editableTags.forEach((key) => {
            const values = pendingChanges[key] ?? track.tags[key] ?? [];
            // Filter out empty values
            updatedTags[key] = values.filter((v) => v.trim());
        });

        request({
            notify: `Saving tags...`,
            notify_ok: `Saved tags`,
            function: `edit/${trackId}/tags`,
            options: {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(updatedTags),
            },
            onAction: () => {
                setPendingChanges({});
                void navigate(`/${roomName}/edit/${trackId}`);
            },
        });
    };

    return (
        <Screen
            navLeft={<BackOr to={`/${roomName}/edit/${trackId}`} />}
            title={`Edit Tags: ${track.tags.title[0]}`}
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
            <TagsEditor
                tags={currentTags}
                possibleValuesByKey={possibleValuesByKey}
                onChanged={handleChanged}
            />
        </Screen>
    );
}
