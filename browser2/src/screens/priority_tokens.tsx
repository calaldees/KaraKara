import h from "hyperapp-jsx-pragma";
import { BackToExplore, Screen } from "./_common";
import { short_date } from "../utils";

export const PriorityTokens = ({ state }: { state: State }): VNode => (
    <Screen
        state={state}
        className={"priority_tokens"}
        navLeft={<BackToExplore />}
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
                {state.priority_tokens.map((t: PriorityToken) => (
                    <tr>
                        <td>{t.id}</td>
                        <td>{short_date(t.issued)}</td>
                        <td>{t.used ? "yes" : "no"}</td>
                        <td>{t.session_id}</td>
                        <td>{short_date(t.valid_start)}</td>
                        <td>{short_date(t.valid_end)}</td>
                    </tr>
                ))}
            </tbody>
        </table>
    </Screen>
);
