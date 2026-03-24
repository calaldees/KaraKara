import { EventInfo } from "@/components/eventinfo";
import { Globe } from "@/components/globe";
import { JoinInfo } from "@/components/joininfo";

import "./title.scss";

export function TitleScreen() {
    return (
        <section key="title" className={"screen_title"}>
            <Globe />
            <JoinInfo />
            <EventInfo />
        </section>
    );
}
