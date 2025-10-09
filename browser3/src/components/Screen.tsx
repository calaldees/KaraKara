import { useContext, useRef } from "react";

import { useScrollRestoration } from "@/hooks/scrollrestoration";
import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import { Notification } from "./Notification";
import { YoureNext } from "./YoureNext";

const EmptyHeaderLink = (): React.ReactElement => <div />;

export function Screen({
    title,
    className = undefined,
    footer = null,
    navLeft = null,
    navRight = null,
    children = null,
}: {
    title: string;
    className?: string | undefined;
    footer?: React.ReactElement | null | false;
    navLeft?: React.ReactElement | null | false;
    navRight?: React.ReactElement | null | false;
    children?: React.ReactNode;
}): React.ReactElement {
    const { setShowSettings } = useContext(ClientContext);
    const { queue } = useContext(RoomContext);
    const scroller = useRef<HTMLElement | null>(null);
    useScrollRestoration(scroller);

    return (
        <main className={className}>
            <header>
                {navLeft || <EmptyHeaderLink />}
                <h1 onDoubleClick={(_) => setShowSettings(true)}>{title}</h1>
                {navRight || <EmptyHeaderLink />}
            </header>
            <Notification />
            {queue && <YoureNext queue={queue} />}
            <article ref={scroller}>{children}</article>
            {footer}
        </main>
    );
}
