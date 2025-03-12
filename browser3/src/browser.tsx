/// <reference types='./browser.d.ts'/>

// polyfills
import "@ungap/global-this"; // iOS up to 14
import "abortcontroller-polyfill/dist/polyfill-patch-fetch"; // iOS up to 12

import React from "react";
import ReactDOM from "react-dom/client";
import "./static/style.scss";
import { ClientProvider } from "./providers/client";
import { ServerProvider } from "./providers/server";
import { Root } from "./screens/root";

const root = ReactDOM.createRoot(document.getElementById("root")!);
root.render(
    <React.StrictMode>
        <ClientProvider>
            <ServerProvider>
                <Root />
            </ServerProvider>
        </ClientProvider>
    </React.StrictMode>,
);
