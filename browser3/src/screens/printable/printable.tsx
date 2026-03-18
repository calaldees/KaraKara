import { QRCodeSVG } from "qrcode.react";
import { useRef } from "react";
import { useParams } from "react-router-dom";
import { useReactToPrint } from "react-to-print";

import { BackToExplore, ButtonRow, Screen } from "@/components";

import "./printable.scss";

export function Printable(): React.ReactElement {
    const { roomName } = useParams();

    const contentRef = useRef<HTMLDivElement>(null);
    const reactToPrintFn = useReactToPrint({ contentRef });

    const root = window.location.protocol + "//" + window.location.host;
    const buttons = (
        <ButtonRow>
            <button type="button" onClick={reactToPrintFn}>
                Print
            </button>
        </ButtonRow>
    );

    return (
        <Screen
            className={"printable"}
            navLeft={<BackToExplore />}
            title={"Track List"}
            //navRight={}
            footer={buttons}
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
