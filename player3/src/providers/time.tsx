import { useContext } from "react";
import { ServerTimeProvider } from "@shish2k/react-use-servertime";

import { ClientContext } from "../providers/client";


export const TimeProvider = (props: any) => {
    const { root } = useContext(ClientContext);
    return (
        <ServerTimeProvider url={`${root}/time.json`}>
            {props.children}
        </ServerTimeProvider>
    );
};
