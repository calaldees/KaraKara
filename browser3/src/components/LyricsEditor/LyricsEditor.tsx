import { faPlay, faPlus, faTrash } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useRef } from "react";

import type { Subtitle } from "@/types";

import styles from "./LyricsEditor.module.scss";

function SubtitleRow({
    subtitle,
    index,
    audioUrl,
    onUpdate,
    onDelete,
    onPlay,
}: {
    subtitle: Subtitle;
    index: number;
    audioUrl?: string;
    onUpdate: (index: number, field: keyof Subtitle, value: any) => void;
    onDelete: (index: number) => void;
    onPlay: (start: number, end: number) => void;
}) {
    return (
        <tbody>
            <tr>
                <td>
                    {audioUrl && (
                        <FAIcon
                            icon={faPlay}
                            className={styles.playIcon}
                            onClick={() => onPlay(subtitle.start, subtitle.end)}
                            role="button"
                            aria-label="Play Subtitle"
                        />
                    )}
                </td>
                <td>
                    <input
                        type="number"
                        step="0.001"
                        value={subtitle.start}
                        onChange={(e) =>
                            onUpdate(index, "start", parseFloat(e.target.value))
                        }
                        className={styles.timeInput}
                    />
                </td>
                <td>
                    <input
                        type="number"
                        step="0.001"
                        value={subtitle.end}
                        onChange={(e) =>
                            onUpdate(index, "end", parseFloat(e.target.value))
                        }
                        className={styles.timeInput}
                    />
                </td>
                <td>
                    <input
                        type="checkbox"
                        checked={subtitle.top}
                        onChange={(e) =>
                            onUpdate(index, "top", e.target.checked)
                        }
                        className={styles.checkbox}
                    />
                </td>
                <td>
                    <FAIcon
                        icon={faTrash}
                        className={styles.deleteIcon}
                        onClick={() => onDelete(index)}
                        role="button"
                        aria-label="Delete Subtitle"
                    />
                </td>
            </tr>
            <tr>
                <td colSpan={5}>
                    <input
                        type="text"
                        value={subtitle.text}
                        onChange={(e) =>
                            onUpdate(index, "text", e.target.value)
                        }
                        className={styles.textInput}
                    />
                </td>
            </tr>
        </tbody>
    );
}

export function LyricsEditor({
    lines,
    onChanged,
    audioUrl,
}: {
    lines: Subtitle[];
    onChanged: (lines: Subtitle[]) => void;
    audioUrl?: string;
}) {
    const audioRef = useRef<HTMLAudioElement>(null);
    const handleUpdateSubtitle = (
        index: number,
        field: keyof Subtitle,
        value: any,
    ) => {
        const updated = [...lines];
        updated[index] = { ...updated[index], [field]: value };
        onChanged(updated);
    };

    const handleDeleteSubtitle = (index: number) => {
        if (confirm("Delete this subtitle?")) {
            onChanged(lines.filter((_, i) => i !== index));
        }
    };

    const handleAddSubtitle = () => {
        const newSubtitle: Subtitle = {
            start: 0,
            end: 0,
            text: "",
            top: false,
        };
        onChanged([...lines, newSubtitle]);
    };

    const handlePlaySubtitle = (start: number, end: number) => {
        if (!audioRef.current) return;

        const audio = audioRef.current;
        audio.currentTime = start;
        void audio.play();

        const handleTimeUpdate = () => {
            if (audio.currentTime >= end) {
                audio.pause();
                audio.removeEventListener("timeupdate", handleTimeUpdate);
            }
        };

        audio.addEventListener("timeupdate", handleTimeUpdate);
    };

    return (
        <div className={styles.lyricsEditor}>
            {audioUrl && (
                <audio ref={audioRef} src={audioUrl} preload="metadata" />
            )}
            <table className={styles.subtitlesTable}>
                <thead>
                    <tr>
                        <th></th>
                        <th>Start</th>
                        <th>End</th>
                        <th>Top</th>
                        <th></th>
                    </tr>
                </thead>
                {lines.map((subtitle, index) => (
                    <SubtitleRow
                        key={index}
                        subtitle={subtitle}
                        index={index}
                        audioUrl={audioUrl}
                        onUpdate={handleUpdateSubtitle}
                        onDelete={handleDeleteSubtitle}
                        onPlay={handlePlaySubtitle}
                    />
                ))}
            </table>
            <button
                type="button"
                onClick={handleAddSubtitle}
                className={styles.addButton}
            >
                <FAIcon icon={faPlus} /> Add Subtitle
            </button>
        </div>
    );
}
