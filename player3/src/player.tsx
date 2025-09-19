/// <reference types='./player.d.ts'/>

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { ClientProvider } from "./providers/client";
import { TimeProvider } from "./providers/time";
import { ServerProvider } from "./providers/server";
import { Root } from "./screens/root";

import "./static/style.scss";
import "./static/metalghosts.scss";


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
