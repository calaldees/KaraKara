import { useContext } from "react";
import { Link } from "react-router-dom";
import { attachment_path, is_my_song } from "../utils";
import * as icons from "../static/icons";
import { ServerContext } from "../providers/server";
import { ClientContext } from "../providers/client";
import { RoomContext } from "../providers/room";
import placeholder from "../static/placeholder.svg";

export function Notification() {
    const { notification, setNotification } = useContext(ClientContext);

    return (
        notification && (
            <div
                className={"main-only notification " + notification.style}
                onClick={(e) => setNotification(null)}
            >
                <span>{notification.text}</span>
                <icons.CircleXmark />
            </div>
        )
    );
}

export function YoureNext({
    queue,
}: {
    queue: Array<QueueItem>;
}): React.ReactElement {
    const { performerName } = useContext(ClientContext);
    const { sessionId } = useContext(RoomContext);
    const { tracks } = useContext(ServerContext);

    return (
        <>
            {(is_my_song(sessionId, performerName, queue[0]) && (
                <h2 className="main-only upnext">
                    Your song "{tracks[queue[0].track_id].tags.title[0]}" is up
                    now!
                </h2>
            )) ||
                (is_my_song(sessionId, performerName, queue[1]) && (
                    <h2 className="main-only upnext">
                        Your song "{tracks[queue[1].track_id].tags.title[0]}" is
                        up next!
                    </h2>
                ))}
        </>
    );
}

const EmptyHeaderLink = (): React.ReactElement => <a href="#" />;

export function Screen({
    title,
    className = undefined,
    footer = <div />,
    navLeft = null,
    navRight = null,
    children = [],
}: {
    title: string;
    className?: string | undefined;
    footer?: any;
    navLeft?: any;
    navRight?: any;
    children?: any;
}): React.ReactElement {
    const { setShowSettings } = useContext(ClientContext);
    const { queue } = useContext(RoomContext);

    return (
        <main className={className}>
            <header>
                {navLeft || <EmptyHeaderLink />}
                <h1 onDoubleClick={(e) => setShowSettings(true)}>{title}</h1>
                {navRight || <EmptyHeaderLink />}
            </header>
            <Notification />
            <YoureNext queue={queue} />
            <article>{children}</article>
            {footer}
        </main>
    );
}

export const BackToExplore = (): React.ReactElement => (
    <Link to={"../"} data-cy="back">
        <icons.CircleChevronLeft className="x2" />
    </Link>
);

export function Thumb({
    track,
    children,
    ...kwargs
}: {
    track: Track;
    children?: any;
    [Key: string]: any;
}): React.ReactElement {
    const { root } = useContext(ClientContext);

    return (
        <div className={"thumb"} {...kwargs}>
            <picture>
                {track.attachments.image.map((a) => (
                    <source
                        key={a.path}
                        srcSet={attachment_path(root, a)}
                        type={a.mime}
                    />
                ))}
                <img
                    alt=""
                    style={{ backgroundImage: `url(${placeholder})` }}
                />
            </picture>
            {children}
        </div>
    );
}
