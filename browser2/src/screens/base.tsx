import h from "hyperapp-jsx-pragma";
import { GoToScreen, ShowSettings, ClearNotification } from "../actions";

export const Notification = ({ state }: { state: State }) =>
    state.notification && (
        <div
            class={"main-only notification " + state.notification.style}
            onclick={ClearNotification()}
        >
            <span>{state.notification.text}</span>
            <i class={"fas fa-times-circle"} />
        </div>
    );

function isMySong(state: State, n: number) {
    return (
        state.queue.length > n &&
        (state.queue[n].session_owner == state.session_id ||
            state.queue[n].performer_name == state.performer_name)
    );
}

export const YoureNext = ({ state }: { state: State }) =>
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

export const EmptyHeaderLink = () => <a />;

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
) => (
    <main class={className}>
        <header>
            {navLeft}
            <h1 ondblclick={ShowSettings()}>{title}</h1>
            {navRight}
        </header>
        <Notification state={state} />
        <YoureNext state={state} />
        <article>{children}</article>
        {footer}
    </main>
);

export const BackToExplore = () => (
    <a onclick={GoToScreen("explore")}>
        <i class={"fas fa-2x fa-chevron-circle-left"} />
    </a>
);
