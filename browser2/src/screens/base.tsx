import h from "hyperapp-jsx-pragma";
import { GoToScreen, ShowSettings, ClearNotification } from "../actions";
import { PopScrollPos } from "../effects";
import { timedelta_str } from "../utils";

export const Notification = ({ state }: { state: State }): VNode =>
    state.notification && (
        <div
            class={"main-only notification " + state.notification.style}
            onclick={ClearNotification()}
        >
            <span>{state.notification.text}</span>
            <i class={"fas fa-times-circle"} />
        </div>
    );

export function PriorityToken({ state }: { state: State }): VNode | null {
    if(!state.priority_token) return null;

    var now = new Date().getTime(); // TODO: - server_datetime_offset;

    var valid_start = new Date(state.priority_token.valid_start).getTime();
    var valid_end = new Date(state.priority_token.valid_end).getTime();
    var delta_start = valid_start - now;
    var delta_end = valid_end - now;

    if (delta_start > 0) {
        return <h2 class={"main-only priority_soon"}>
            Priority mode in {timedelta_str(delta_start)}
        </h2>;
    }
    if (delta_start < 0 && delta_end > 0) {
        return <h2 class={"main-only priority_now"}>
            Priority mode for {timedelta_str(delta_end)}
        </h2>;
    }
    return null;
}

function isMySong(state: State, n: number): boolean {
    return (
        state.queue.length > n &&
        (state.queue[n].session_owner == state.session_id ||
            state.queue[n].performer_name == state.performer_name)
    );
}

export const YoureNext = ({ state }: { state: State }): VNode =>
    (isMySong(state, 0) && (
        <h2 class="main-only upnext">
            Your song "{state.queue[0].track.title}" is up now!
        </h2>
    )) ||
    (isMySong(state, 1) && (
        <h2 class="main-only upnext">
            Your song "{state.queue[1].track.title}" is up next!
        </h2>
    ));

export const EmptyHeaderLink = (): VNode => <a />;

export const Screen = (
    {
        state,
        title,
        className = null,
        footer = <div />,
        navLeft = <EmptyHeaderLink />,
        navRight = <EmptyHeaderLink />,
    }: {
        state: State;
        title: string;
        className?: string | null;
        footer?: any;
        navLeft?: any;
        navRight?: any;
    },
    children,
): VNode => (
    <main class={className}>
        <header>
            {navLeft}
            <h1 ondblclick={ShowSettings()}>{title}</h1>
            {navRight}
        </header>
        <Notification state={state} />
        <PriorityToken state={state} />
        <YoureNext state={state} />
        <article>{children}</article>
        {footer}
    </main>
);

export const BackToExplore = (): VNode => (
    <a onclick={GoToScreen("explore", [PopScrollPos()])}>
        <i class={"fas fa-2x fa-chevron-circle-left"} />
    </a>
);
