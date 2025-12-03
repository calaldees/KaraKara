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
            <img
                alt=""
                draggable="false"
                src={
                    track?.attachments.image[0] &&
                    attachment_path(track.attachments.image[0])
                }
            />
            {children}
        </div>
    );
}
