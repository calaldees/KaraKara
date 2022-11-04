import h from "hyperapp-jsx-pragma";
import { Screen, BackToExplore, Thumb } from "./_common";
import { shuffle, is_my_song, time_until, current_and_future } from "../utils";
import { RemoveTrack } from "../actions";

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
            me: is_my_song(state, item),
        }}
    >
        <Thumb state={state} track={state.track_list[item.track_id]} />
        <span class={"text queue_info"}>
            <span class={"title"}>
                {state.track_list[item.track_id].tags.title[0]}
            </span>
            <br />
            <span class={"performer"}>{item.performer_name}</span>
        </span>
        {item.start_time && (
            <span class={"count"}>
                {time_until(state.now, item.start_time)}
            </span>
        )}

        {state.session_id == item.session_id && (
            <span class={"go_arrow"} onclick={RemoveTrack(item.id)}>
                <i class={"fas fa-times-circle"} />
            </span>
        )}
    </li>
);

const Playlist = ({
    state,
    queue,
}: {
    state: State;
    queue: Array<QueueItem>;
}): VNode => (
    <div>
        {/* No items */}
        {queue.length == 0 && <h2>Queue Empty</h2>}

        {/* At least one item */}
        {queue.length > 0 && (
            <div>
                <ul>
                    <QueueItemRender state={state} item={queue[0]} />
                    {state.track_list[queue[0].track_id].lyrics.length > 0 && (
                        <li>
                            <span class={"lyrics"}>
                                {state.track_list[queue[0].track_id].lyrics.map(
                                    (line) => (
                                        <div>{line}</div>
                                    ),
                                )}
                            </span>
                        </li>
                    )}
                </ul>
            </div>
        )}

        {/* Some items */}
        {queue.length > 1 && (
            <section>
                <h2>Coming Soon</h2>
                <ul>
                    {queue.slice(1, 1+state.settings["coming_soon_length"]).map((item) => (
                        <QueueItemRender state={state} item={item} />
                    ))}
                </ul>
            </section>
        )}

        {/* Many items */}
        {queue.length > (1+state.settings["coming_soon_length"]) && (
            <section>
                <h2>Coming Later</h2>
                <div class={"coming_later"}>
                    {shuffle(queue.slice(1+state.settings["coming_soon_length"])).map((item) => (
                        <span>{item.performer_name}</span>
                    ))}
                </div>
            </section>
        )}
    </div>
);

export const Queue = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={!state.widescreen && <BackToExplore />}
        title={"Now Playing"}
    >
        <Playlist
            state={state}
            queue={current_and_future(state.now, state.queue)}
        />
    </Screen>
);
