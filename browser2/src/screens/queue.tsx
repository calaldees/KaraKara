import h from "hyperapp-jsx-pragma";
import { Screen, BackToExplore } from "./base";
import { attachment_path, shuffle } from "../utils";
import { RemoveTrack } from "../actions";

const QueueItemRender = ({
    state,
    item,
}: {
    state: State;
    item: QueueItem;
}): VNode => (
    <li
        class={
            state.session_id == item.session_owner
                ? "queue_item me"
                : "queue_item"
        }
    >
        <span class={"thumb"}>
            <picture>
                {state.track_list[item.track_id].attachments.image.map(a => 
                <source
                    src={attachment_path(state.root, a)}
                    type={a.mime}
                />)}
            </picture>
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

        {state.session_id == item.session_owner && (
            <span class={"go_arrow"} onclick={RemoveTrack(item.id)}>
                <i class={"fas fa-times-circle"} />
            </span>
        )}
    </li>
);

/*
 * Page Layout
 */
export const Queue = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={!state.widescreen && <BackToExplore />}
        title={"Now Playing"}
        // navRight={}
    >
        {/* No items */}
        {state.queue.length == 0 && <h2>Queue Empty</h2>}

        {/* At least one item */}
        {state.queue.length > 0 && (
            <div>
                <ul>
                    <QueueItemRender state={state} item={state.queue[0]} />
                    {state.track_list[state.queue[0].track_id].lyrics && (
                        <li>
                            <span class={"lyrics"}>
                                {state.track_list[state.queue[0].track_id].lyrics.split("\n").map((line) => (
                                    <div>
                                        {line.replace(/^\{.*?\}/, "")}
                                    </div>
                                ))}
                            </span>
                        </li>
                    )}
                </ul>
            </div>
        )}

        {/* Some items */}
        {state.queue.length > 1 && (
            <section>
                <h2>Coming Soon</h2>
                <ul>
                    {state.queue.slice(1, 6).map((item) => (
                        <QueueItemRender state={state} item={item} />
                    ))}
                </ul>
            </section>
        )}

        {/* Many items */}
        {state.queue.length > 6 && (
            <section>
                <h2>Coming Later</h2>
                <div class={"coming_later"}>
                    {shuffle(state.queue.slice(6)).map((item) => (
                        <span>{item.performer_name}</span>
                    ))}
                </div>
            </section>
        )}
    </Screen>
);
