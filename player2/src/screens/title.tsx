import h from "hyperapp-jsx-pragma";

export const TitleScreen = ({ state }: { state: State }): VNode => (
    <section key="title" class={"screen_title"}>
        <div id={"splash"}>
            {state.images.map((item) => (
                <img
                    src={state.root + "/files/" + item.filename}
                    style={{
                        animationDelay: item.delay + "s",
                        left: item.x * 90 + "vw",
                    }}
                />
            ))}
        </div>
        <h1>{state.settings["karakara.player.title"]}</h1>
        <div id="join_info">
            Join at <strong>{state.root.replace("https://", "")}</strong> - Room
            Name is <strong>{state.room_name}</strong>
        </div>
    </section>
);
