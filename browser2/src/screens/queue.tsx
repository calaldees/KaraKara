import h from "hyperapp-jsx-pragma";
import { Screen, Refresh, BackToExplore } from "./base";
import { get_attachment, title_case, shuffle } from "../utils";
import { DisplayResponseMessage } from "../effects";
import { Http } from "hyperapp-fx";
import parseSRT from "parse-srt";

/*
 * Now Playing
 */
const NowPlaying = ({ state, item }: { state: State; item: QueueItem }) => (
    <div>
        <ul>
            <QueueItemRender state={state} item={item} />
            {state.track_list[item.track.id].srt && (
                <li>
                    <span class={"lyrics"}>
                        {parseSRT(state.track_list[item.track.id].srt).map(
                            item => (
                                <div>{item.text}</div>
                            ),
                        )}
                    </span>
                </li>
            )}
        </ul>
    </div>
);

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
        <h2>Coming Soon</h2>
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
    <li
        class={
            state.session_id == item.session_owner
                ? "queue_item me"
                : "queue_item"
        }
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

        {state.session_id == item.session_owner && (
            <span
                class={"go_arrow"}
                onclick={state => [
                    { ...state, notification: {text: "Removing track...", style: "warning"} },
                    Http({
                        url:
                            state.root +
                            "/queue/" +
                            state.room_name +
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
        )}
    </li>
);

/*
 * Coming Later
 */
const ComingLater = ({
    state,
    items,
}: {
    state: State;
    items: Array<QueueItem>;
}) => (
    <section>
        <h2>Coming Later</h2>
        <div class={"coming_later"}>
            {items.map(item => (
                <span>{item.performer_name}</span>
            ))}
        </div>
    </section>
);

/*
 * Page Layout
 */
export const Queue = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={<BackToExplore />}
        title={"Now Playing"}
        navRight={<Refresh state={state} />}
    >
        {state.queue.length == 0 && <h2>Queue Empty</h2>}
        {state.queue.length > 0 && (
            <NowPlaying state={state} item={state.queue[0]} />
        )}
        {state.queue.length > 1 && (
            <ComingSoon state={state} items={state.queue.slice(1, 6)} />
        )}
        {state.queue.length > 6 && (
            <ComingLater state={state} items={shuffle(state.queue.slice(6))} />
        )}
    </Screen>
);
