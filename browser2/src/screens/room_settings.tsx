import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";

export const RoomSettings = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"room_settings"}
        navLeft={
            <a onclick={(state) => [{...state, screen: "explore"}]}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={"Room Settings"}
        //navRight={}
        //footer={}
    >
        {Object.entries(state.settings).map(([key, value]) =>
            <p>{key}:
            <br/><input value={value} /></p>
        )}
    </Screen>
);
