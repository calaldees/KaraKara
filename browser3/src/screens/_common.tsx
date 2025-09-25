import { useContext, useRef } from "react";
import { Link } from "react-router-dom";
import {
    faCircleChevronLeft,
    faCircleXmark,
} from "@fortawesome/free-solid-svg-icons";

import { attachment_path, is_my_song } from "../utils";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";
import placeholder from "../static/placeholder.svg";
import { useScrollRestoration } from "../hooks/scrollrestoration";
import type { Track, QueueItem } from "../types";

// This is a minimal reimplementation of FontAwesomeIcon
// to avoid pulling in the whole ~80kb library
// See https://docs.fontawesome.com/v5/web/use-with/react
export function FontAwesomeIcon({icon, className=""}: {icon: any, className?: string}) {
    const [width, height, _aliases, _unicode, svgPathData] = icon.icon;
    return <svg
        aria-hidden="true"
        focusable="false"
        data-prefix={icon.prefix}
        data-icon={icon.iconName}
        className={`svg-inline--fa fa-${icon.iconName} ${className}`}
        role="img"
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${width} ${height}`}
    >
        <path fill="currentColor" d={svgPathData}></path>
    </svg>
}

export function Notification() {
    const { notification, setNotification } = useContext(ClientContext);

    return (
        notification && (
            <div
                className={"main-only notification " + notification.style}
                onClick={(_) => setNotification(null)}
            >
                <span>{notification.text}</span>
                <FontAwesomeIcon icon={faCircleXmark} />
            </div>
        )
    );
}

export function YoureNext({
    queue,
}: {
    queue: QueueItem[];
}): React.ReactElement {
    const { performerName } = useContext(ClientContext);
    const { sessionId } = useContext(RoomContext);
    const { tracks } = useContext(ServerContext);

    return (
        <>
            {(is_my_song(sessionId, performerName, queue[0]) && (
                <h2 className="main-only upnext">
                    Your song "{tracks[queue[0].track_id]?.tags.title[0]}" is up
                    now!
                </h2>
            )) ||
                (is_my_song(sessionId, performerName, queue[1]) && (
                    <h2 className="main-only upnext">
                        Your song "{tracks[queue[1].track_id]?.tags.title[0]}"
                        is up next!
                    </h2>
                ))}
        </>
    );
}

const EmptyHeaderLink = (): React.ReactElement => <a href="#" />;

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

export const BackToExplore = (): React.ReactElement => (
    <Link to={"../"} data-cy="back">
        <FontAwesomeIcon icon={faCircleChevronLeft} className="x2" />
    </Link>
);

export function Thumb({
    track,
    children,
    ...kwargs
}: {
    track: Track | undefined;
    children?: any;
    [Key: string]: any;
}): React.ReactElement {
    return (
        <div className={"thumb"} {...kwargs}>
            <picture>
                {track?.attachments.image.map((a, n) => (
                    <source
                        key={a.path + n}
                        srcSet={attachment_path(a)}
                        type={a.mime}
                    />
                ))}
                <img
                    alt=""
                    style={{ backgroundImage: `url("${placeholder}")` }}
                    draggable="false"
                />
            </picture>
            {children}
        </div>
    );
}
