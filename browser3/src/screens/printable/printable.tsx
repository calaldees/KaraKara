import { QRCodeSVG } from "qrcode.react";
import { useContext, useRef } from "react";
import { useReactToPrint } from "react-to-print";

import { BackOr, ButtonRow, Screen } from "@/components";
import { PageContext } from "@/providers/page";

import "./printable.scss";

function Printable(): React.ReactElement {
    const { roomName } = useContext(PageContext);

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
            navLeft={<BackOr to={`/${roomName}`} />}
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

export default Printable;
