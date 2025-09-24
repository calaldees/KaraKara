import { useContext, useRef } from "react";
import { useParams } from "react-router-dom";
import { QRCodeSVG } from "qrcode.react";
import { useReactToPrint } from "react-to-print";

import { BackToExplore, Screen } from "../_common";
import { ClientContext } from "@/providers/client";

import "./printable.scss";

///////////////////////////////////////////////////////////////////////
// Views

const PrintButtons = ({
    callback,
}: {
    callback: () => void;
}): React.ReactElement => (
    <footer>
        <div className={"buttons"}>
            <button type="button" onClick={callback}>
                Print
            </button>
        </div>
    </footer>
);

export function Printable(): React.ReactElement {
    const { roomName } = useParams();
    const { root } = useContext(ClientContext);

    const contentRef = useRef<HTMLDivElement>(null);
    const reactToPrintFn = useReactToPrint({ contentRef });

    return (
        <Screen
            className={"printable"}
            navLeft={<BackToExplore />}
            title={"Track List"}
            //navRight={}
            footer={<PrintButtons callback={reactToPrintFn} />}
        >
            <div ref={contentRef} className="printableContent">
                <p>
                    To get an interactive track list on your phone, scan this QR
                    code or visit {root} and use room name "{roomName}".
                </p>
                <div className={"qr_container"}>
                    <QRCodeSVG
                        value={`${root}/browser3/${roomName}`}
                        className={"qr_code"}
                    />
                </div>
            </div>
        </Screen>
    );
}
