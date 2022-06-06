import h from "hyperapp-jsx-pragma";
import { memo } from "hyperapp";
import { attachment_path } from "../utils";

export const Splash = ({ track_list, root }: { track_list: Dictionary<Track>, root: string }): VNode => (
    <div id={"splash"}>
        {Object
            .values(track_list)
            .slice(0, 25)
            .map(track => track.attachments.image[0])
            .map((image, n, arr) => (
                <img
                    src={attachment_path(root, image)}
                    style={{
                        animationDelay: (((n % 5) + Math.random()) * 2) + "s",
                        animationDuration: (5 + Math.random() * 5) + "s",
                        left: (n / arr.length) * 90 + "vw",
                    }}
                />
            ))}
    </div>
);

export const TitleScreen = ({ state }: { state: State }): VNode => (
    <section key="title" class={"screen_title"}>
        {memo(Splash, {track_list: state.track_list, root: state.root})}
        <h1>{state.settings["karakara.player.title"]}</h1>
        <div id="join_info">
            Join at <strong>{state.root.replace("https://", "")}</strong> -
            Room Name is <strong>{state.room_name}</strong>
        </div>
    </section>
);
