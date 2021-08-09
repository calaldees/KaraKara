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
    children,
) => (
    <main class={className}>
        <header>
            {navLeft}
            <h1 ondblclick={ShowSettings()}>{title}</h1>
            {navRight}
        </header>
        <Notification state={state} />
        <article>{children}</article>
        {footer}
    </main>
);

export const BackToExplore = () => (
    <a onclick={GoToScreen("explore")}>
        <i class={"fas fa-2x fa-chevron-circle-left"} />
    </a>
);
