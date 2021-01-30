import h from "hyperapp-jsx-pragma";
import { ApiRequest } from "../effects";

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
        className?: string;
        footer?: any;
        navLeft?: any;
        navRight?: any;
    },
    children,
) => (
    <main class={className}>
        <header>
            {navLeft}
            <h1 ondblclick={(state) => ({ ...state, show_settings: true })}>
                {title}
            </h1>
            {navRight}
        </header>
        {state.notification && (
            <div
                class={"notification " + state.notification.style}
                onclick={(state) => ({ ...state, notification: null })}
            >
                <span>{state.notification.text}</span>
                <i class={"fas fa-times-circle"} />
            </div>
        )}
        <article>{children}</article>
        {footer}
    </main>
);

export function refresh(state: State) {
    return [
        state,
        ApiRequest({
            function: "queue_items",
            state: state,
            action: (state, response) => ({
                ...state,
                queue: response.data.queue,
            }),
        }),
    ];
}

export const Refresh = ({ state }: { state: State }) => (
    <a onclick={refresh}>
        <i
            class={
                state.loading
                    ? "fas fa-2x fa-sync loading"
                    : "fas fa-2x fa-sync"
            }
        />
    </a>
);

export const BackToExplore = () => (
    <a onclick={(state) => ({ ...state, screen: "explore" })}>
        <i class={"fas fa-2x fa-chevron-circle-left"} />
    </a>
);
