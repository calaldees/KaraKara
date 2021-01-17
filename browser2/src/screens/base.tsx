import h from "hyperapp-jsx-pragma";

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
