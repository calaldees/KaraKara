import {
    faBackward,
    faCircleXmark,
    faForward,
    faForwardStep,
    faGripVertical,
    faPlay,
    faStop,
} from "@fortawesome/free-solid-svg-icons";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import { useContext, useState } from "react";
import { useParams } from "react-router-dom";

import { BackToExplore, FontAwesomeIcon, Screen, Thumb } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { QueueItem } from "@/types";
import { dict2css, time_until } from "@/utils";

function Playlist({ queue }: { queue: QueueItem[] }): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const { fullQueue, setOptimisticQueue } = useContext(RoomContext);
    const { booth } = useContext(ClientContext);
    const [dropSource, setDropSource] = useState<number | null>(null);
    const [dropTarget, setDropTarget] = useState<number | null>(null);
    const { request } = useApi();

    function onDragStart(e: any, src_id: number) {
        if (e.dataTransfer) e.dataTransfer.dropEffect = "move";
        setDropSource(src_id);
        setDropTarget(src_id);
    }
    function onDragOver(e: any, dst_id: number) {
        e.preventDefault();
        setDropTarget(dst_id);
    }
    function onDragLeave(e: any) {
        e.preventDefault();
        setDropTarget(null);
    }
    function onDrop(e: any, dst_id: number | null) {
        e.preventDefault();
        moveTrack(dropSource, dst_id);
    }

    function onTouchStart(e: TouchEvent, src_id: number) {
        e.preventDefault();
        setDropSource(src_id);
        setDropTarget(src_id);
    }
    function onTouchMove(e: TouchEvent) {
        // target = the innermost element of the heirachy that was touched
        // but we want to find the root UL
        let ul: HTMLElement | null = e.target as HTMLElement;
        while (ul && ul.tagName !== "UL") ul = ul.parentElement;
        if (!ul) return;

        const x = e.touches[0].clientX,
            y = e.touches[0].clientY;
        let tgt_id = null;
        ul.querySelectorAll("LI").forEach(function (el, key) {
            const r = el.getBoundingClientRect();
            if (x > r.left && x < r.right && y > r.top && y < r.bottom) {
                tgt_id = queue[key].id;
            }
        });

        setDropTarget(tgt_id);
    }
    function onTouchEnd(e: TouchEvent) {
        e.preventDefault();
        moveTrack(dropSource, dropTarget);
    }
    function onTouchCancel(e: TouchEvent) {
        e.preventDefault();
        setDropSource(null);
        setDropTarget(null);
    }

    function moveTrack(src_id: number | null, dst_id: number | null) {
        if (src_id === dst_id) {
            setDropSource(null);
            setDropTarget(null);
            return;
        }

        // find the dragged item by ID number, remove it from the list
        const src_ob = queue.find((x) => x.id === src_id);
        if (!src_ob) {
            setDropSource(null);
            setDropTarget(null);
            return;
        }
        const new_queue = queue.filter((x) => x.id !== src_id);

        // insert the dragged item above the drop target
        if (dst_id === -1) {
            new_queue.push(src_ob);
        } else {
            const dst_pos = new_queue.findIndex((x) => x.id === dst_id);
            new_queue.splice(dst_pos, 0, src_ob);
        }

        // update our local queue, tell the server to update server queue,
        setOptimisticQueue(new_queue);
        setDropSource(null);
        setDropTarget(null);
        request({
            function: "queue",
            options: {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    source: src_id,
                    target: dst_id,
                }),
            },
            // on network error, revert to original queue
            onException: () => setOptimisticQueue(null),
        });
    }

    function removeTrack(queue_item_id: number) {
        request({
            notify: "Removing track...",
            notify_ok: "Track removed!",
            function: "queue/" + queue_item_id.toString(),
            options: {
                method: "DELETE",
            },
        });
    }

    function airtime_text(performer_name: string, queue_item_id: number) {
        let n = 0;
        let airtime = 0;
        for (let i = 0; i < fullQueue.length; i++) {
            if (fullQueue[i].performer_name === performer_name) {
                n++;
                airtime += tracks[fullQueue[i].track_id].duration;
            }
            if (fullQueue[i].id === queue_item_id) {
                break;
            }
        }
        const nth = n === 1 ? "st" : n === 2 ? "nd" : n === 3 ? "rd" : "th";
        const airtime_mins = Math.floor(airtime / 60);
        const text = n + nth + " track, " + airtime_mins + " mins total";
        return text;
    }

    return (
        <section>
            <ul onDragLeave={(e) => onDragLeave(e)}>
                {queue.map((item, n) => (
                    <li
                        data-item-id={item.id}
                        key={item.id}
                        className={dict2css({
                            queue_item: true,
                            drop_source: dropSource === item.id,
                            drop_target: dropTarget === item.id,
                            public: !booth && n <= 5,
                        })}
                        draggable={true}
                        onDragStart={(e) => onDragStart(e, item.id)}
                        onDragOver={(e) => onDragOver(e, item.id)}
                        onDrop={(e) => onDrop(e, item.id)}
                    >
                        <Thumb
                            track={tracks[item.track_id]}
                            onTouchStart={(e: TouchEvent) =>
                                onTouchStart(e, item.id)
                            }
                            onTouchMove={(e: TouchEvent) => onTouchMove(e)}
                            onTouchEnd={(e: TouchEvent) => onTouchEnd(e)}
                            onTouchCancel={(e: TouchEvent) => onTouchCancel(e)}
                        >
                            <span className={"drag-handle"}>
                                <FontAwesomeIcon icon={faGripVertical} />
                            </span>
                        </Thumb>
                        <span className={"text queue_info"}>
                            <span className={"title"}>
                                {tracks[item.track_id]?.tags.title[0] ??
                                    `<${item.track_id} not found>`}
                            </span>
                            <br />
                            <span className={"performer"}>
                                {item.performer_name}
                                {!booth && (
                                    <>
                                        {" "}
                                        (
                                        {airtime_text(
                                            item.performer_name,
                                            item.id,
                                        )}
                                        )
                                    </>
                                )}
                            </span>
                        </span>
                        {item.start_time && (
                            <span className={"count"}>
                                {time_until(now, item.start_time)}
                            </span>
                        )}

                        <span
                            className={"go_arrow"}
                            onClick={(_) => removeTrack(item.id)}
                        >
                            <FontAwesomeIcon icon={faCircleXmark} />
                        </span>
                    </li>
                ))}
                {dropSource && (
                    <li
                        data-cy={"end-marker"}
                        className={dict2css({
                            queue_item: true,
                            drop_target: dropTarget === -1,
                            drop_last: true,
                        })}
                        onDragOver={(e) => onDragOver(e, -1)}
                        onDrop={(e) => onDrop(e, -1)}
                    >
                        <span className={"text"}>(Move to end)</span>
                    </li>
                )}
            </ul>
        </section>
    );
}

function ControlButtons(): React.ReactElement {
    const { sendCommand, loading } = useApi();

    const buttons = {
        seek_backwards: <FontAwesomeIcon icon={faBackward} />,
        seek_forwards: <FontAwesomeIcon icon={faForward} />,
        play: <FontAwesomeIcon icon={faPlay} />,
        stop: <FontAwesomeIcon icon={faStop} />,
        skip: <FontAwesomeIcon icon={faForwardStep} />,
    };

    return (
        <footer>
            <div className={"buttons"}>
                {Object.entries(buttons).map(([command, icon]) => (
                    <button
                        key={command}
                        type="button"
                        onClick={(_) => sendCommand(command)}
                        disabled={loading}
                    >
                        {icon}
                    </button>
                ))}
            </div>
        </footer>
    );
}

function ProgressBar({
    queue,
    startDateTime,
    endDateTime,
}: {
    queue: QueueItem[];
    startDateTime: string;
    endDateTime: string;
}) {
    const { now } = useContext(ServerTimeContext);
    if (!queue.length) return null;
    const queue_last = queue[queue.length - 1];
    if (!queue_last.start_time) return null;
    const start = Date.parse(startDateTime);
    const current = now - start;
    const queue_end =
        (queue_last.start_time + queue_last.track_duration) * 1000 - start;
    const end = Date.parse(endDateTime) - start;
    return (
        <div className="progress_bar">
            <div
                className="played"
                style={{ width: `${(current / end) * 100}%` }}
                title={`Played until ${new Date(
                    start + current,
                ).toLocaleString()}`}
            />
            <div
                className="queued"
                style={{ width: `${((queue_end - current) / end) * 100}%` }}
                title={`Queued until ${new Date(
                    start + queue_end,
                ).toLocaleString()}`}
            />
            <div
                className="space"
                style={{ width: `${((end - queue_end) / end) * 100}%` }}
                title={`Remaining time ${Math.floor(
                    (end - queue_end) / 60000,
                )} minutes`}
            />
        </div>
    );
}

export function Control(): React.ReactElement {
    const { roomName } = useParams();
    const { widescreen } = useContext(ClientContext);
    const { queue, fullQueue, settings } = useContext(RoomContext);

    const root = window.location.protocol + "//" + window.location.host;
    return (
        <Screen
            className={"queue"}
            navLeft={!widescreen && <BackToExplore />}
            title={"Remote Control"}
            // navRight={}
            footer={<ControlButtons />}
        >
            {queue.length === 0 ? (
                <div className="readme">
                    <h1>READ ME :)</h1>
                    <ol>
                        <li>
                            To avoid feedback loops, don't hold the microphone
                            directly in front of the speaker!
                        </li>
                        <li>
                            This admin laptop can drag &amp; drop to rearrange
                            tracks in the queue
                        </li>
                        <li>
                            Either use your phone (open <b>{root}</b> and enter
                            room <b>{roomName}</b>) or use the menu on the right
                            to queue up tracks.
                        </li>
                        <li>
                            Push the play button (
                            <FontAwesomeIcon icon={faPlay} />) down below when
                            you're ready to start singing.
                        </li>
                    </ol>
                </div>
            ) : (
                <>
                    {fullQueue.length > 0 &&
                        settings["validation_event_start_datetime"] &&
                        settings["validation_event_end_datetime"] && (
                            <ProgressBar
                                queue={fullQueue}
                                startDateTime={
                                    settings["validation_event_start_datetime"]
                                }
                                endDateTime={
                                    settings["validation_event_end_datetime"]
                                }
                            />
                        )}
                    <Playlist queue={queue} />
                </>
            )}
        </Screen>
    );
}
