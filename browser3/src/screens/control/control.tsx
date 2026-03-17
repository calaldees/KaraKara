import {
    faBackward,
    faCircleXmark,
    faForward,
    faForwardStep,
    faGripVertical,
    faPlay,
    faStop,
} from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import type { DragEvent, TouchEvent } from "react";
import { useContext, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { BackToExplore, Screen, Thumb } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { QueueItem } from "@/types";
import { dict2css, nth, time_until } from "@/utils";

import "./control.scss";

function Playlist({ queue }: { queue: QueueItem[] }): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const { fullQueue, setOptimisticQueue } = useContext(RoomContext);
    const { booth } = useContext(ClientContext);
    const [dropSource, setDropSource] = useState<number | null>(null);
    const [dropTarget, setDropTarget] = useState<number | null>(null);
    const { request } = useApi();
    const { roomName } = useParams();

    function onDragStart(e: DragEvent, src_id: number) {
        if (e.dataTransfer && e.currentTarget) {
            e.dataTransfer.dropEffect = "move";
            // Set the drag ghost to the entire list item, even though
            // the drag events are fired on the thumbnail
            const listItem = (e.target as HTMLElement).closest("li");
            if (listItem) {
                const rect = (
                    e.currentTarget as HTMLElement
                ).getBoundingClientRect();
                e.dataTransfer.setDragImage(
                    listItem,
                    rect.width / 2,
                    rect.height,
                );
            }
        }
        setDropSource(src_id);
        setDropTarget(src_id);
    }
    function onDragOver(e: DragEvent, dst_id: number) {
        e.preventDefault();
        setDropTarget(dst_id);
    }
    function onDragLeave(e: DragEvent) {
        // prevent firing when moving between child elements
        const li = e.currentTarget as HTMLElement;
        const handle = e.relatedTarget as HTMLElement;
        if (li.contains(handle)) return;
        e.preventDefault();
        setDropTarget(null);
    }
    function onDrop(e: DragEvent, dst_id: number | null) {
        e.preventDefault();
        moveTrack(dropSource, dst_id);
    }
    function onDragEnd(e: DragEvent) {
        e.preventDefault();
        setDropSource(null);
        setDropTarget(null);
    }

    function onTouchStart(e: TouchEvent, src_id: number) {
        e.preventDefault();
        setDropSource(src_id);
        setDropTarget(src_id);
    }
    function onTouchMove(e: TouchEvent) {
        // target = the innermost element of the heirachy that was touched
        // but we want to find the root UL
        let ul: HTMLElement | null = e.currentTarget as HTMLElement;
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
                headers: { "Content-Type": "application/json" },
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
                airtime += fullQueue[i].track_duration;
            }
            if (fullQueue[i].id === queue_item_id) {
                break;
            }
        }
        const airtime_mins = Math.floor(airtime / 60);
        const text = `${nth(n)} track, ${airtime_mins} mins total`;
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
                            drop_target:
                                dropTarget === item.id &&
                                dropSource !== item.id,
                            public: !booth && n <= 5,
                        })}
                        onDragOver={(e: DragEvent) => onDragOver(e, item.id)}
                        onDrop={(e: DragEvent) => onDrop(e, item.id)}
                    >
                        <Thumb
                            track={tracks[item.track_id]}
                            draggable={true}
                            onDragStart={(e: DragEvent) =>
                                onDragStart(e, item.id)
                            }
                            onDragEnd={(e: DragEvent) => onDragEnd(e)}
                            onTouchStart={(e: TouchEvent) =>
                                onTouchStart(e, item.id)
                            }
                            onTouchMove={(e: TouchEvent) => onTouchMove(e)}
                            onTouchEnd={(e: TouchEvent) => onTouchEnd(e)}
                            onTouchCancel={(e: TouchEvent) => onTouchCancel(e)}
                        >
                            <FAIcon
                                icon={faGripVertical}
                                className={"drag-handle"}
                            />
                        </Thumb>
                        <span className={"text queue_info"}>
                            <Link
                                to={`/${roomName}/tracks/${item.track_id}`}
                                className={"title"}
                            >
                                {tracks[item.track_id]?.tags.title[0] ??
                                    `<${item.track_id} not found>`}
                            </Link>
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

                        <FAIcon
                            icon={faCircleXmark}
                            className={"go_arrow"}
                            onClick={(_) =>
                                confirm(
                                    `Delete ${item.performer_name}'s track?`,
                                ) && removeTrack(item.id)
                            }
                        />
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
        seek_backwards: <FAIcon icon={faBackward} />,
        seek_forwards: <FAIcon icon={faForward} />,
        play: <FAIcon icon={faPlay} />,
        stop: <FAIcon icon={faStop} />,
        skip: <FAIcon icon={faForwardStep} />,
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

function MaybeProgressBar({
    queue,
    startDateTime,
    endDateTime,
}: {
    queue: QueueItem[];
    startDateTime: string;
    endDateTime: string;
}): React.ReactElement | null {
    const { now } = useContext(ServerTimeContext);
    if (!queue.length) return null;
    const queueLast = queue[queue.length - 1];
    if (!queueLast.start_time) return null;
    if (!startDateTime || !endDateTime) return null;

    return (
        <ProgressBar
            startTime={Date.parse(startDateTime) / 1000}
            queueEnd={queueLast.start_time + queueLast.track_duration}
            now={now}
            endTime={Date.parse(endDateTime) / 1000}
        />
    );
}

/**
 * All times in seconds since epoch
 */
function ProgressBar({
    startTime,
    now,
    queueEnd,
    endTime,
}: {
    startTime: number;
    now: number;
    queueEnd: number;
    endTime: number;
}) {
    const eventDuration = endTime - startTime;
    return (
        <div className="event_progress">
            <div
                className="played"
                style={{
                    width: `${((now - startTime) / eventDuration) * 100}%`,
                }}
                title={`Played until ${new Date(now * 1000).toLocaleString()}`}
            />
            <div
                className="queued"
                style={{
                    width: `${((queueEnd - now) / eventDuration) * 100}%`,
                }}
                title={`Queued until ${new Date(queueEnd * 1000).toLocaleString()}`}
            />
            <div
                className="space"
                style={{
                    width: `${((endTime - queueEnd) / eventDuration) * 100}%`,
                }}
                title={`Remaining time ${Math.floor((endTime - queueEnd) / 60)} minutes`}
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
            className={"control"}
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
                            <FAIcon icon={faPlay} />) down below when you're
                            ready to start singing.
                        </li>
                    </ol>
                </div>
            ) : (
                <>
                    <MaybeProgressBar
                        queue={fullQueue}
                        startDateTime={
                            settings["validation_event_start_datetime"]
                        }
                        endDateTime={settings["validation_event_end_datetime"]}
                    />
                    <Playlist queue={queue} />
                </>
            )}
        </Screen>
    );
}
