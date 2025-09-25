import { useContext } from "react";

import { EventInfo } from "@/components/eventinfo";
import { Globe } from "@/components/globe";
import { JoinInfo } from "@/components/joininfo";
import { Waterfall } from "@/components/waterfall";
import { RoomContext } from "@/providers/room";

import "./title.scss";

export function TitleScreen() {
    const { settings } = useContext(RoomContext);
    let splash = null;
    switch (settings["splash"]) {
        case "globe":
        default:
            splash = <Globe />;
            break;
        case "waterfall":
            splash = <Waterfall />;
            break;
    }

    return (
        <section key="title" className={"screen_title"}>
            {splash}
            <JoinInfo />
            <EventInfo />
        </section>
    );
}
