import h from "hyperapp-jsx-pragma";

function log_state(state: State): State {
    console.log(state);
    return state;
}

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
    <main className={className}>
        <header>
            {navLeft}
            <h1 onclick={log_state}>{title}</h1>
            {navRight}
        </header>
        {state.notification && (
            <div
                class={"notification"}
                onclick={state => ({ ...state, notification: null })}
            >
                <span>{state.notification}</span>
                <i class={"fas fa-times-circle"} />
            </div>
        )}
        <article>{children}</article>
        {footer}
    </main>
);
