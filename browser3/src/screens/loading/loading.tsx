import { faRotate } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { Screen } from "@/components";
import { PageContext } from "@/providers/page";
import { ServerContext } from "@/providers/server";
import { percent } from "@/utils";

function Loading(): React.ReactElement {
    const { downloadDone, downloadSize } = useContext(ServerContext);
    const { roomName } = useContext(PageContext);

    return (
        <Screen className={"loadingPage"} title={"Loading..."}>
            <div className={"flex-center"}>
                <input type="text" value={roomName} disabled={true} />
                <button type="button" disabled={true}>
                    Loading Tracks{" "}
                    {downloadSize ? (
                        percent(downloadDone, downloadSize)
                    ) : (
                        <FAIcon icon={faRotate} className={"loading"} />
                    )}
                </button>
            </div>
        </Screen>
    );
}

export default Loading;
