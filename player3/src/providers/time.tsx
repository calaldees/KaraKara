import { ServerTimeProvider } from "@shish2k/react-use-servertime";

export const TimeProvider = (props: any) => {
    return (
        <ServerTimeProvider url={`/api/time.json`}>
            {props.children}
        </ServerTimeProvider>
    );
};
