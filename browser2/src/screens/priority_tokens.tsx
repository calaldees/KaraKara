import h from "hyperapp-jsx-pragma";
import { Screen } from "./base";

export const PriorityTokens = ({ state }: { state: State }) => (
    <Screen
        state={state}
        className={"priority_tokens"}
        navLeft={
            <a onclick={(state) => [{...state, screen: "explore"}]}>
                <i class={"fas fa-2x fa-chevron-circle-left"} />
            </a>
        }
        title={"Priority Tokens"}
        //navRight={}
        //footer={}
    >
        <table>
            <thead>
                <th>ID</th>
                <th>Issued</th>
                <th>Used</th>
                <th>Owner</th>
                <th>Start</th>
                <th>End</th>
            </thead>
            <tbody>
                {state.priority_tokens.map((t: PriorityToken) => <tr>
                    <td>{t.id}</td>
                    <td>{t.issued}</td>
                    <td>{t.used}</td>
                    <td>{t.session_owner}</td>
                    <td>{t.valid_start}</td>
                    <td>{t.valid_end}</td>
                </tr>)}
            </tbody>
        </table>
    </Screen>
);
