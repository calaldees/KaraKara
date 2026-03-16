import { useContext, lazy } from "react";

import { EventInfo } from "@/components/eventinfo";
import { JoinInfo } from "@/components/joininfo";
import { Waterfall } from "@/components/waterfall";
import { RoomContext } from "@/providers/room";
const Globe = lazy(() => import("@/components/globe").then((mod) => ({ default: mod.Globe })));

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
