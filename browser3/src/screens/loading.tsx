import { useContext } from "react";
import { Screen } from "./_common";
import { percent } from "../utils";
import * as icons from "../static/icons";
import { ServerContext } from "../providers/server";
import { useParams } from "react-router-dom";

export function Loading(): React.ReactElement {
    const { downloadDone, downloadSize } = useContext(ServerContext);
    const { roomName } = useParams();

    return (
        <Screen className={"loadingPage"} title={"Loading..."}>
            <div className={"flex-center"}>
                <input type="text" value={roomName} disabled={true} />
                <button type="button" disabled={true}>
                    Loading Tracks{" "}
                    {downloadSize ? (
                        percent(downloadDone, downloadSize)
                    ) : (
                        <icons.Rotate className={"loading"} />
                    )}
                </button>
            </div>
        </Screen>
    );
}
