import h from "hyperapp-jsx-pragma";
import { memo } from "hyperapp";
import { attachment_path } from "../utils";
import { EventInfo, JoinInfo } from "./_common";

export const Splash = ({
    track_list,
    root,
}: {
    track_list: Dictionary<Track>;
    root: string;
}): VNode => (
    <div id={"splash"}>
        {Object.values(track_list)
            // ignore instrumental tracks, because instrumentals
            // tend to have hard-subs, which makes ugly thumbnails
            .filter((track) => track.tags.vocaltrack?.[0] != "off")
            .slice(0, 25)
            .map((track) => track.attachments.image[0])
            .map((image, n, arr) => (
                <img
                    src={attachment_path(root, image)}
                    style={{
                        animationDelay: ((n % 5) + Math.random()) * 2 + "s",
                        animationDuration: 5 + Math.random() * 5 + "s",
                        left: (n / arr.length) * 90 + "vw",
                    }}
                />
            ))}
    </div>
);

export const TitleScreen = ({ state }: { state: State }): VNode => (
    <section key="title" class={"screen_title"}>
        {memo(Splash, { track_list: state.track_list, root: state.root })}
        <JoinInfo state={state} />
        <h1>{state.settings["title"]}</h1>
        <EventInfo state={state} />
    </section>
);
