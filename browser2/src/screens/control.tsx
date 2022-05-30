import h from "hyperapp-jsx-pragma";
import { Screen, BackToExplore } from "./base";
import { attachment_path } from "../utils";
import { ApiRequest } from "../effects";
import { RemoveTrack, Command } from "../actions";

function createDragStart(src_id) {
    return function (state, event) {
        event.dataTransfer.dropEffect = "move";
        return { ...state, drop_source: src_id, drop_target: src_id };
    };
}
function createDragOver(dst_id) {
    return function (state, event) {
        event.preventDefault();
        return { ...state, drop_target: dst_id };
    };
}
function createDragLeave() {
    return function (state, event) {
        event.preventDefault();
        return { ...state, drop_target: null };
    };
}
function createDrop(dst_id) {
    return function (state, event) {
        event.preventDefault();
        return moveTrack(state, state.drop_source, dst_id);
    };
}

function createTouchStart(src_id) {
    return function (state, event) {
        event.preventDefault();
        return { ...state, drop_source: src_id, drop_target: src_id };
    };
}
function createTouchMove() {
    return function (state, event) {
        // target = the innermost element of the heirachy that was touched
        // but we want to find the root UL
        let ul: HTMLElement | null = event.target as HTMLElement;
        while (ul && ul.tagName != "UL") ul = ul.parentElement;
        if (!ul) return { state };

        let x = event.touches[0].clientX,
            y = event.touches[0].clientY;
        let tgt_id = null;
        ul.querySelectorAll("LI").forEach(function (el, key) {
            let r = el.getBoundingClientRect();
            if (x > r.left && x < r.right && y > r.top && y < r.bottom) {
                tgt_id = state.queue[key].id;
            }
        });

        return { ...state, drop_target: tgt_id };
    };
}
function createTouchEnd() {
    return function (state, event) {
        event.preventDefault();
        return moveTrack(state, state.drop_source, state.drop_target);
    };
}
function createTouchCancel() {
    return function (state, event) {
        event.preventDefault();
        return { ...state, drop_source: null, drop_target: null };
    };
}

function moveTrack(
    state: State,
    src_id: number | null,
    dst_id: number | null,
): Dispatchable {
    let cancel = { ...state, drop_source: null, drop_target: null };
    if (src_id === dst_id) return cancel;

    // find the dragged item by ID number, remove it from the list
    let src_ob = state.queue.find((x) => x.id == src_id);
    if (!src_ob) return cancel;
    let new_queue = state.queue.filter((x) => x.id != src_id);

    // insert the dragged item above the drop target
    if (dst_id === -1) {
        new_queue.push(src_ob);
    } else {
        let dst_pos = new_queue.findIndex((x) => x.id == dst_id);
        new_queue.splice(dst_pos, 0, src_ob);
    }

    // update our local queue, tell the server to update server queue,
    let original_queue = state.queue;
    return [
        {
            ...state,
            queue: new_queue,
            drop_source: null,
            drop_target: null,
        },
        ApiRequest({
            function: "queue_items",
            state: state,
            options: {
                method: "PUT",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    "queue_item.id": "" + src_id,
                    "queue_item.move.target_id": "" + dst_id,
                }),
            },
            // on server-side error, revert to original queue
            action: function (state, response) {
                if (response.status == "ok") return state;
                return { ...state, queue: original_queue };
            },
            // on network error, revert to original queue
            exception: function (state) {
                return { ...state, queue: original_queue };
            },
        }),
    ];
}

const Playlist = ({
    state,
    items,
}: {
    state: State;
    items: Array<QueueItem>;
}): VNode => (
    <section>
        <ul ondragleave={createDragLeave()}>
            {items.map((item) => (
                <QueueItemRender state={state} item={item} />
            ))}
            {state.drop_source && (
                <li
                    class={{
                        queue_item: true,
                        drop_target: state.drop_target == -1,
                        drop_last: true,
                    }}
                    ondragover={createDragOver(-1)}
                    ondrop={createDrop(-1)}
                >
                    <span class={"text"}>(Move to end)</span>
                </li>
            )}
        </ul>
    </section>
);

const QueueItemRender = ({
    state,
    item,
}: {
    state: State;
    item: QueueItem;
}): VNode => (
    <li
        class={{
            queue_item: true,
            drop_source: state.drop_source == item.id,
            drop_target: state.drop_target == item.id,
        }}
        draggable={true}
        ondragstart={createDragStart(item.id)}
        ondragover={createDragOver(item.id)}
        ondrop={createDrop(item.id)}
    >
        <span
            class={"thumb"}
            ontouchstart={createTouchStart(item.id)}
            ontouchmove={createTouchMove()}
            ontouchend={createTouchEnd()}
            ontouchcancel={createTouchCancel()}
        >
            <div
                style={{
                    "background-image":
                        "url(" +
                        attachment_path(state.root, state.track_list[item.track_id].attachments.image?.[0]) +
                        ")",
                }}
            />
            <span class={"drag-handle"}>
                <i class="fas fa-grip-vertical" />
            </span>
        </span>
        <span class={"text queue_info"}>
            <span class={"title"}>
                {state.track_list[item.track_id].tags.title[0]}
            </span>
            <br />
            <span class={"performer"}>{item.performer_name}</span>
        </span>
        {item.total_duration > 0 && (
            <span class={"count"}>
                In {Math.floor(item.total_duration / 60)} min
                {item.total_duration > 120 ? "s" : ""}
            </span>
        )}

        <span class={"go_arrow"} onclick={RemoveTrack(item.id)}>
            <i class={"fas fa-times-circle"} />
        </span>
    </li>
);

const ControlButtons = ({ state }: { state: State }): VNode => (
    <footer>
        <div class={"buttons"}>
            <button onclick={Command("seek_backwards")}>
                <i class={"fas fa-backward"} />
            </button>
            <button onclick={Command("seek_forwards")}>
                <i class={"fas fa-forward"} />
            </button>
            <button onclick={Command("play")}>
                <i class={"fas fa-play"} />
            </button>
            <button onclick={Command("pause")}>
                <i class={"fas fa-pause"} />
            </button>
            <button onclick={Command("stop")}>
                <i class={"fas fa-stop"} />
            </button>
            <button onclick={Command("skip")}>
                <i class={"fas fa-step-forward"} />
            </button>
        </div>
    </footer>
);

export const Control = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={!state.widescreen && <BackToExplore />}
        title={"Remote Control"}
        // navRight={}
        footer={<ControlButtons state={state} />}
    >
        {state.queue.length == 0 ? (
            <div class="readme">
                <h1>READ ME :)</h1>
                <ol>
                    <li>Please use hand sanitiser, a lot of different people
                    are going to use this laptop and the microphones :)</li>
                    <li>To avoid feedback loops, don't hold the microphone
                    directly in front of the speaker!</li>
                    <li>This admin laptop can drag &amp; drop to rearrange
                    tracks in the queue</li>
                    <li>Either use your phone (open <b>{state.root}</b> and
                    enter room <b>{state.room_name}</b>) or use the menu on the
                    right to queue up tracks.</li>
                    <li>Push the play button (<i class={"fas fa-play"} />) down
                    below when you're ready to start singing.</li>
                </ol>
            </div>
        ) : (
            <Playlist state={state} items={state.queue} />
        )}
    </Screen>
);
