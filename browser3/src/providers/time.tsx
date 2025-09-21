import { useContext } from "react";
import { ClientContext } from "../providers/client";
import { ServerTimeProvider } from "@shish2k/react-use-servertime";

export const TimeProvider = (props: any) => {
    const { root } = useContext(ClientContext);
    return (
        <ServerTimeProvider url={`${root}/time.json`}>
            {props.children}
        </ServerTimeProvider>
    );
};
