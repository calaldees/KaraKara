import { useContext } from "react";
import { useParams } from "react-router-dom";
import { faRotate } from "@fortawesome/free-solid-svg-icons";

import { Screen, FontAwesomeIcon } from "../_common";
import { percent } from "@/utils";
import { ServerContext } from "@/providers/server";

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
                        <FontAwesomeIcon
                            icon={faRotate}
                            className={"loading"}
                        />
                    )}
                </button>
            </div>
        </Screen>
    );
}
