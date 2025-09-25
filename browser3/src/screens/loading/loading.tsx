import { faRotate } from "@fortawesome/free-solid-svg-icons";
import { useContext } from "react";
import { useParams } from "react-router-dom";

import { FontAwesomeIcon, Screen } from "@/components";
import { ServerContext } from "@/providers/server";
import { percent } from "@/utils";

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
