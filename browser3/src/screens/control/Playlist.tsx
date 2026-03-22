import { faCircleXmark } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import type { DragEvent, TouchEvent } from "react";
import { useContext, useState } from "react";
import { Link } from "react-router-dom";

import { ListItem, Thumb } from "@/components";
import { useApi } from "@/hooks/api";
import { ClientContext } from "@/providers/client";
import { PageContext } from "@/providers/page";
import { RoomContext } from "@/providers/room";
import { ServerContext } from "@/providers/server";
import type { QueueItem } from "@/types";
import { dict2css, nth, time_until } from "@/utils";

import { List } from "@/components";
import styles from "./Playlist.module.scss";

export function Playlist({
    queue,
}: {
    queue: QueueItem[];
}): React.ReactElement {
    const { tracks } = useContext(ServerContext);
    const { now } = useContext(ServerTimeContext);
    const { fullQueue, setOptimisticQueue } = useContext(RoomContext);
    const { booth } = useContext(ClientContext);
    const [dropSource, setDropSource] = useState<number | null>(null);
    const [dropTarget, setDropTarget] = useState<number | null>(null);
    const { request } = useApi();
    const { roomName } = useContext(PageContext);

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
            <List onDragLeave={(e) => onDragLeave(e)}>
                {queue.map((item, n) => (
                    <ListItem
                        key={item.id}
                        data-item-id={item.id}
                        onDragOver={(e: DragEvent) => onDragOver(e, item.id)}
                        onDrop={(e: DragEvent) => onDrop(e, item.id)}
                        className={dict2css({
                            [styles.queueItem]: true,
                            [styles.dropSource]: dropSource === item.id,
                            [styles.dropTarget]:
                                dropTarget === item.id &&
                                dropSource !== item.id,
                            [styles.public]: !booth && n <= 5,
                        })}
                        thumb={
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
                                onTouchCancel={(e: TouchEvent) =>
                                    onTouchCancel(e)
                                }
                                dragHandle={true}
                            />
                        }
                        title={
                            <Link
                                to={`/${roomName}/tracks/${item.track_id}`}
                                className={styles.title}
                            >
                                {tracks[item.track_id]?.tags.title[0] ??
                                    `<${item.track_id} not found>`}
                            </Link>
                        }
                        info={
                            <>
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
                            </>
                        }
                        count={
                            item.start_time
                                ? time_until(now, item.start_time)
                                : undefined
                        }
                        action={
                            <FAIcon
                                icon={faCircleXmark}
                                className={styles.goArrow}
                                onClick={(_) =>
                                    confirm(
                                        `Delete ${item.performer_name}'s track?`,
                                    ) && removeTrack(item.id)
                                }
                            />
                        }
                    />
                ))}
                {dropSource && (
                    <li
                        data-cy={"end-marker"}
                        className={dict2css({
                            [styles.queueItem]: true,
                            [styles.dropTarget]: dropTarget === -1,
                            [styles.dropLast]: true,
                        })}
                        onDragOver={(e) => onDragOver(e, -1)}
                        onDrop={(e) => onDrop(e, -1)}
                    >
                        <span className={"text"}>(Move to end)</span>
                    </li>
                )}
            </List>
        </section>
    );
}
