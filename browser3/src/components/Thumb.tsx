import placeholder from "@/static/placeholder.svg";
import type { Track } from "@/types";
import { attachment_path } from "@/utils";

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
