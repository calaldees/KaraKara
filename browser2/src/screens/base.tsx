import h from "hyperapp-jsx-pragma";
import { DisplayResponseMessage } from "../effects";
import { Http } from "hyperapp-fx";

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
            <h1 ondblclick={(state) => ({...state, show_settings: true})}>{title}</h1>
            {navRight}
        </header>
        {state.notification && (
            <div
                class={"notification "+state.notification.style}
                onclick={state => ({ ...state, notification: null })}
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
        { ...state, loading: true },
        Http({
            url: state.root + "/queue/" + state.queue_id + "/queue_items.json",
            action: (state, response) => ({
                ...state,
                loading: false,
                queue: response.data.queue,
            }),
            error: (state, response) => [
                {...state, loading: false},
                [DisplayResponseMessage, response],
            ],
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
)

export const BackToExplore = () => (
    <a onclick={state => ({ ...state, screen: "explore" })}>
        <i class={"fas fa-2x fa-chevron-circle-left"} />
    </a>
)
