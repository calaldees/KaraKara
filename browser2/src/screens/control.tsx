import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";
import { get_attachment, title_case } from "../utils";
import { Http } from "hyperapp-fx";
import { refresh } from "./queue";
import { SendCommand } from "../effects";

/*
 * Coming Soon
 */
const ComingSoon = ({
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
    <li class={"queue_item"}>
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

        {state.performer_name == item.performer_name && (
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
                                // method: "delete",
                                // format: "redirect",
                                "queue_item.id": item.id.toString(),
                            }),
                        },
                        action: (state, response) => ({
                            ...state,
                            notification: "Removed from queue",
                        }),
                        error: (state, response) => ({
                            ...state,
                            notification: "Error removing track from queue",
                        }),
                    }),
                ]}
            >
                <i class={"fas fa-times-circle"} />
            </span>
        )}
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
            <ComingSoon state={state} items={state.queue} />
        )}
    </Screen>
);
