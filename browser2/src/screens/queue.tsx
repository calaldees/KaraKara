import {h} from "hyperapp";
import {Screen} from "./base";
import {get_attachment, title_case, shuffle} from "../utils";
import { Http } from "hyperapp-fx";

/*
 * Now Playing
 */
const NowPlaying = ({state, item}: {state: State, item: QueueItem}) => (
    <div>
        <h2>Now Playing</h2>
        <ul>
            <QueueItemRender state={state} item={item} />
            <li>
                <span class={"lyrics"}>
                    {state.track_list[item.track.id].lyrics.split("\n").map((x) => (
                        <div>{x}</div>
                    ))}
                </span>
            </li>
        </ul>
    </div>
);

/*
 * Coming Soon
 */
const ComingSoon = ({state, items}: {state: State, items: Array<QueueItem>}) => (
    <section>
        <h2>Coming Soon</h2>
        <ul>
            {items.map((item) => (<QueueItemRender state={state} item={item} />))}
        </ul>
    </section>
);

const QueueItemRender = ({state, item}: {state: State, item: QueueItem}) => (
    <li class={state.performer_name == item.performer_name ? "queue_item me" : "queue_item"}>
        <span class={"thumb"} style={{"background-image": "url(" +get_attachment(item.track, "image") + ")"}} />
        <span class={"text queue_info"}>
            <span class={"title"}>{title_case(item.track.tags["title"][0])}</span>
            <br/><span class={"performer"}>{item.performer_name}</span>
        </span>
        {item.total_duration > 0 &&
            <span class={"count"}>In {Math.floor(item.total_duration/60)} min{item.total_duration > 120 ? "s" : ""}</span>}

        {state.performer_name == item.performer_name &&
            <span class={"go_arrow"}
                  onClick={(state) => [
                      {...state, notification: "Removing track"},
                      Http({
                          url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
                          options: {
                              method: "DELETE",
                              headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                              body: new URLSearchParams({
                                  // method: "delete",
                                  // format: "redirect",
                                  "queue_item.id": item.id.toString(),
                              }),
                          },
                          action: (state, response) => ({...state, notification: "Removed from queue"}),
                          error: (state, response) => ({...state, notification: "Error removing track from queue"})
                      })
                  ]}
            ><i class={"fas fa-times-circle"} /></span>}
    </li>
);

/*
 * Coming Later
 */
const ComingLater = ({state, items}: {state: State, items: Array<QueueItem>}) => (
    <section>
        <h2>Coming Later</h2>
        <div class={"coming_later"}>
            {items.map((item) => (<span>{item.performer_name}</span>))}
        </div>
    </section>
);

/*
 * Page Layout
 */
export function refresh(state: State) {
    return [
        {...state, loading: true},
        Http({
            url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
            action: (state, response) => ({...state, loading: false, queue: response.data.queue}),
            error: (state, response) => ({...state, loading: false, notification: ""+response})
        })
    ];
}

export const Queue = ({state}: {state: State}) => (
    <Screen
        state={state}
        className={"queue"}
        navLeft={<a onclick={(state) => ({...state, screen: "explore"})}><i class={"fas fa-2x fa-chevron-circle-left"} /></a>}
        title={"Now Playing"}
        navRight={<a onclick={refresh}><i class={state.loading ? "fas fa-2x fa-sync loading" : "fas fa-2x fa-sync"} /></a>}
    >
        {state.queue.length == 0 && <h2>Queue Empty</h2>}
        {state.queue.length > 0 && <NowPlaying state={state} item={state.queue[0]}/>}
        {state.queue.length > 1 && <ComingSoon state={state} items={state.queue.slice(1, 6)} />}
        {state.queue.length > 6 && <ComingLater state={state} items={shuffle(state.queue.slice(6))}/>}
    </Screen>
);