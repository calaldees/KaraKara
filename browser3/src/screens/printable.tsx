import { useContext } from "react";
import { BackToExplore, Screen } from "./_common";
import { useParams } from "react-router-dom";
import { ClientContext } from "../providers/client";
import { QRCodeSVG } from "qrcode.react";

///////////////////////////////////////////////////////////////////////
// Views

const PrintButtons = (): React.ReactElement => (
    <footer>
        <div className={"buttons"}>
            <button
                onClick={function (state) {
                    window.print();
                    return state;
                }}
            >
                Print
            </button>
        </div>
    </footer>
);

export function Printable(): React.ReactElement {
    const { roomName } = useParams();
    const { root } = useContext(ClientContext);

    return (
        <Screen
            className={"track_list"}
            navLeft={<BackToExplore />}
            title={"Track List"}
            //navRight={}
            footer={<PrintButtons />}
        >
            <p>To get an interactive track list on your phone, scan this QR code or
            visit {root} and use room name "{roomName}".</p>
            <div className={"qr_container"}>
                <QRCodeSVG
                    value={`${root}/browser3/${roomName}`}
                    className={"qr_code"}
                />
            </div>
        </Screen>
    );
}
