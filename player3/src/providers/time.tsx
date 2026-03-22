import { ServerTimeProvider } from "@shish2k/react-use-servertime";

export const TimeProvider = (props: any) => {
    return (
        <ServerTimeProvider url={`/api/misc/time.json`}>
            {props.children}
        </ServerTimeProvider>
    );
};
