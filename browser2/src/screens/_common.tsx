import h from "hyperapp-jsx-pragma";
import { GoToScreen } from "../actions";
import { PopScrollPos } from "../effects";
import { attachment_path, current_and_future, is_my_song } from "../utils";
import * as placeholder from "data-url:../static/placeholder.svg";
import * as icons from "../static/icons";

export const Notification = ({ state }: { state: State }): VNode =>
    state.notification && (
        <div
            class={"main-only notification " + state.notification.style}
            onclick={(state: State): State => ({
                ...state,
                notification: null,
            })}
        >
            <span>{state.notification.text}</span>
            <icons.CircleXmark />
        </div>
    );

function hhmm(d: Date): string {
    function twoz(n: number): string {
        return n.toString().padStart(2, "0");
    }
    return twoz(d.getHours()) + ":" + twoz(d.getMinutes());
}
export function PriorityToken({ state }: { state: State }): VNode | null {
    if (!state.priority_token) return null;

    var now = new Date(); // TODO: - server_datetime_offset;

    var valid_start = new Date(state.priority_token.valid_start);
    var valid_end = new Date(state.priority_token.valid_end);
    var delta_start = valid_start.getTime() - now.getTime();
    var delta_end = valid_end.getTime() - now.getTime();

    if (delta_start > 0) {
        return (
            <h2 class={"main-only priority_soon"}>
                Priority mode at {hhmm(valid_start)}
            </h2>
        );
    }
    if (delta_start < 0 && delta_end > 0) {
        return (
            <h2 class={"main-only priority_now"}>
                Priority mode until {hhmm(valid_end)}
            </h2>
        );
    }
    return null;
}

export const YoureNext = ({
    state,
    queue,
}: {
    state: State;
    queue: Array<QueueItem>;
}): VNode =>
    (is_my_song(state, queue[0]) && (
        <h2 class="main-only upnext">
            Your song "{state.track_list[queue[0].track_id].tags.title[0]}" is
            up now!
        </h2>
    )) ||
    (is_my_song(state, queue[1]) && (
        <h2 class="main-only upnext">
            Your song "{state.track_list[queue[1].track_id].tags.title[0]}" is
            up next!
        </h2>
    ));

export const EmptyHeaderLink = (): VNode => <a />;

export const Screen = (
    {
        state,
        title,
        className = null,
        footer = <div />,
        navLeft = null,
        navRight = null,
    }: {
        state: State;
        title: string;
        className?: string | null;
        footer?: any;
        navLeft?: any;
        navRight?: any;
    },
    children: any,
): VNode => (
    <main class={className}>
        <header>
            {navLeft || <EmptyHeaderLink />}
            <h1
                ondblclick={(state: State): State => ({
                    ...state,
                    show_settings: true,
                })}
            >
                {title}
            </h1>
            {navRight || <EmptyHeaderLink />}
        </header>
        <Notification state={state} />
        <PriorityToken state={state} />
        <YoureNext
            state={state}
            queue={current_and_future(state.now, state.queue)}
        />
        <article>{children}</article>
        {footer}
    </main>
);

export const BackToExplore = (): VNode => (
    <a onclick={GoToScreen("explore", [PopScrollPos()])} data-cy="back">
        <icons.CircleChevronLeft class="x2" />
    </a>
);

// I don't know how to type ...kwargs correctly
export const Thumb = ({ state, track, ...kwargs }: {state: State, track: Track}, children: any): VNode => (
    <div class={"thumb"} {...kwargs}>
        <img src={placeholder} />
        <picture>
            {track.attachments.image.map((a: Attachment) => (
                <source srcset={attachment_path(state.root, a)} type={a.mime} />
            ))}
            <img src={placeholder} />
        </picture>
        {children}
    </div>
);
