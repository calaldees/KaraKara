/// <reference types='./browser.d.ts'/>

// polyfills
import "@ungap/global-this"; // iOS up to 14
import "abortcontroller-polyfill/dist/polyfill-patch-fetch"; // iOS up to 12

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ClientProvider } from "./providers/client";
import { TimeProvider } from "./providers/time";
import { ServerProvider } from "./providers/server";
import { Root } from "./screens/root";

import "./static/forms.scss";
import "./static/vars.scss";
import "./static/layout.scss";

const root = createRoot(document.getElementById("root")!);
root.render(
    <StrictMode>
        <ClientProvider>
            <TimeProvider>
                <ServerProvider>
                    <Root />
                </ServerProvider>
            </TimeProvider>
        </ClientProvider>
    </StrictMode>,
);
