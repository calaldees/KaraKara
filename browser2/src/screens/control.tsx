import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { get_attachment, title_case } from "../utils";
import { Http } from "hyperapp-fx";
import { refresh } from "./queue";
import { SendCommand, DisplayResponseMessage } from "../effects";

function createDragStart(src_id) {
    return function(state, event) {
        event.dataTransfer.dropEffect = "move";
        return {...state, drop_source: src_id};
    }
}

function createDragOver(dst_id) {
    return function(state, event) {
        event.preventDefault();
        return {...state, drop_target: dst_id};
    }
}

function createDrop(dst_id) {
    return function(state, event) {
        event.preventDefault();
        let src_id = state.drop_source;
        // find the dragged item by ID number, remove it from the list
        let src_ob = state.queue.find(x => x.id == src_id);
        let new_queue = state.queue.filter(x => x.id != src_id);
        // insert the dragged item above the drop target
        let dst_pos = new_queue.findIndex(x => x.id == dst_id);
        new_queue.splice(dst_pos, 0, src_ob);
        return [
            {...state, queue: new_queue, drop_source: null, drop_target: null},
            Http({
                url: state.root+'/queue/'+state.queue_id+'/queue_items.json',
                options: {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: new URLSearchParams({
                        'queue_item.id': src_id,
                        'queue_item.move.target_id': dst_id,
                    }),
                },
                action: (state, response) => [
                    {...state},
                    [DisplayResponseMessage, response],
                ],
                error: (state, response) => [
                    {...state},
                    [DisplayResponseMessage, response]
                ],
        })
        ];
    }
}

const Playlist = ({
    state,
    items,
}: {
    state: State;
    items: Array<QueueItem>;
}) => (
    <section>
        <ul>
            {items.map(item => (
                <QueueItemRender state={state} item={item} />
            ))}
            {state.drop_source && <li
                class={{"queue_item": true, "drop_target": state.drop_target == -1}}
                ondragover={createDragOver(-1)}
                ondrop={createDrop(-1)}
            >(Move to end)</li>}
        </ul>
    </section>
);

const QueueItemRender = ({
    state,
    item,
}: {
    state: State;
    item: QueueItem;
}) => (
    <li
        class={{"queue_item": true, "drop_target": state.drop_target == item.id}}
        draggable={true}
        ondragstart={createDragStart(item.id)}
        ondragover={createDragOver(item.id)}
        ondrop={createDrop(item.id)}
    >
        <span
            class={"thumb"}
            style={{
                "background-image":
                    "url(" + get_attachment(item.track, "image") + ")",
            }}
        />
        <span class={"text queue_info"}>
            <span class={"title"}>
                {title_case(item.track.tags["title"][0])}
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

        <span
            class={"go_arrow"}
            onclick={state => [
                { ...state, notification: "Removing track" },
                Http({
                    url:
                        state.root +
                        "/queue/" +
                        state.queue_id +
                        "/queue_items.json",
                    options: {
                        method: "DELETE",
                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded",
                        },
                        body: new URLSearchParams({
                            "queue_item.id": item.id.toString(),
                        }),
                    },
                    action: (state, response) => [
                        {...state},
                        [DisplayResponseMessage, response],
                    ],
                    error: (state, response) => [
                        {...state},
                        [DisplayResponseMessage, response],
                    ],
                }),
            ]}
        >
            <i class={"fas fa-times-circle"} />
        </span>
    </li>
);

const ControlButtons = ({ state }: { state: State }) => (
    <footer>
        <div class={"buttons"}>
            <button onclick={state => [state, SendCommand(state, "seek_backwards")]}>
                <i class={"fas fa-backward"} />
            </button>
            <button onclick={state => [state, SendCommand(state, "seek_forwards")]}>
                <i class={"fas fa-forward"} />
            </button>
            <button onclick={state => [state, SendCommand(state, "play")]}>
                <i class={"fas fa-play"} />
            </button>
            <button onclick={state => [state, SendCommand(state, "pause")]}>
                <i class={"fas fa-pause"} />
            </button>
            <button onclick={state => [state, SendCommand(state, "stop")]}>
                <i class={"fas fa-stop"} />
            </button>
            <button onclick={state => [state, SendCommand(state, "skip")]}>
                <i class={"fas fa-step-forward"} />
            </button>
        </div>
    </footer>
);

export const Control = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={
            <a onclick={state => ({ ...state, screen: "explore" })}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={"Remote Control"}
        navRight={
            <a onclick={refresh}>
                <i
                    class={
                        state.loading
                            ? "fas fa-2x fa-sync loading"
                            : "fas fa-2x fa-sync"
                    }
                />
            </a>
        }
        footer={<ControlButtons state={state} />}
    >
        {state.queue.length == 0 && <h2>Queue Empty</h2>}
        {state.queue.length > 1 && (
            <Playlist state={state} items={state.queue} />
        )}
    </Screen>
);
