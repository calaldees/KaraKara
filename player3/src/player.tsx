/// <reference types='./player.d.ts'/>

import React from "react";
import ReactDOM from "react-dom/client";
import "./static/style.scss";
import "./static/metalghosts.scss";
import { ClientProvider } from "./providers/client";
import { ServerProvider } from "./providers/server";
import { Root } from "./screens/root";

const root = ReactDOM.createRoot(
    document.getElementById("root") as HTMLElement,
);
root.render(
    <React.StrictMode>
        <ClientProvider>
            <ServerProvider>
                <Root />
            </ServerProvider>
        </ClientProvider>
    </React.StrictMode>,
);
