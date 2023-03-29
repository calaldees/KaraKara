import { useContext, useState } from "react";
import { Screen, BackToExplore, Thumb } from "./_common";
import { dict2css, time_until } from "../utils";
import * as icons from "../static/icons";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";
import { ServerContext } from "../providers/server";
import { useApi } from "../hooks/api";
import { useParams } from "react-router-dom";

function Playlist({ queue }: { queue: Array<QueueItem> }): React.ReactElement {
    const { tracks, now } = useContext(ServerContext);
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

        let x = e.touches[0].clientX,
            y = e.touches[0].clientY;
        let tgt_id = null;
        ul.querySelectorAll("LI").forEach(function (el, key) {
            let r = el.getBoundingClientRect();
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
        let src_ob = queue.find((x) => x.id === src_id);
        if (!src_ob) {
            setDropSource(null);
            setDropTarget(null);
            return;
        }
        let new_queue = queue.filter((x) => x.id !== src_id);

        // insert the dragged item above the drop target
        if (dst_id === -1) {
            new_queue.push(src_ob);
        } else {
            let dst_pos = new_queue.findIndex((x) => x.id === dst_id);
            new_queue.splice(dst_pos, 0, src_ob);
        }

        // FIXME: update our local queue, tell the server to update server queue,
        // setQueue(new_queue);
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
                    source: "" + src_id,
                    target: "" + dst_id,
                }),
            },
            // FIXME: on network error, revert to original queue
            // onException: () => setQueue(queue),
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

    return (
        <section>
            <ul onDragLeave={(e) => onDragLeave(e)}>
                {queue.map((item) => (
                    <li
                        data-item-id={item.id}
                        key={item.id}
                        className={dict2css({
                            queue_item: true,
                            drop_source: dropSource === item.id,
                            drop_target: dropTarget === item.id,
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
                                <icons.GripVertical />
                            </span>
                        </Thumb>
                        <span className={"text queue_info"}>
                            <span className={"title"}>
                                {tracks[item.track_id].tags.title[0]}
                            </span>
                            <br />
                            <span className={"performer"}>
                                {item.performer_name}
                            </span>
                        </span>
                        {item.start_time && (
                            <span className={"count"}>
                                {time_until(now, item.start_time)}
                            </span>
                        )}

                        <span
                            className={"go_arrow"}
                            onClick={(e) => removeTrack(item.id)}
                        >
                            <icons.CircleXmark />
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
        seek_backwards: <icons.Backward />,
        seek_forwards: <icons.Forward />,
        play: <icons.Play />,
        stop: <icons.Stop />,
        skip: <icons.ForwardStep />,
    };

    return (
        <footer>
            <div className={"buttons"}>
                {Object.entries(buttons).map(([command, icon]) => (
                    <button
                        key={command}
                        onClick={(e) => sendCommand(command)}
                        disabled={loading}
                    >
                        {icon}
                    </button>
                ))}
            </div>
        </footer>
    );
}

export function Control(): React.ReactElement {
    const { roomName } = useParams();
    const { root, widescreen } = useContext(ClientContext);
    const { queue } = useContext(RoomContext);

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
                            Push the play button (<icons.Play />) down below
                            when you're ready to start singing.
                        </li>
                    </ol>
                </div>
            ) : (
                <Playlist queue={queue} />
            )}
        </Screen>
    );
}
