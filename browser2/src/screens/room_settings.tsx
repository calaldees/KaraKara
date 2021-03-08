import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./base";

export const RoomSettings = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"room_settings"}
        navLeft={<BackToExplore />}
        title={"Room Settings"}
        //navRight={}
        //footer={}
    >
        {Object.entries(state.settings).map(([key, value]) => (
            <p>
                {key}:
                <br />
                <input value={value} />
            </p>
        ))}
    </Screen>
);
