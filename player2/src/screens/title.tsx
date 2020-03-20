import {h} from "hyperapp";

export const TitleScreen = ({state}: { state: State }) => (
    <section key="title" className={"screen_title"}>
        <div id={"splash"}>
            {state.images.map((item) =>
                <img
                    src={state.root + "/files/" + item.filename}
                    style={{
                        animationDelay: item.delay + "s",
                        left: (item.x * 90) + "vw",
                    }}
                />)}
        </div>
        <h1>{state.settings["karakara.player.title"]}</h1>
        <div id="join_info">
            Join at <strong>{state.root.replace("https://", "")}</strong> -
            Room Name is <strong>{state.queue_id}</strong>
        </div>
    </section>
);