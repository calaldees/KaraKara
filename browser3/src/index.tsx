/// <reference types='./index.d.ts'/>

import { Component, StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";

import { ClientProvider } from "./providers/client";
import { ServerProvider } from "./providers/server";
import { TimeProvider } from "./providers/time";
import { Root } from "./screens/root";

import "./static/forms.scss";
import "./static/layout.scss";
import "./static/vars.scss";

// Reload the page if a chunk fails to load, which can happen when
// a new version is deployed while the user has the app open
class ChunkErrorBoundary extends Component<{ children: React.ReactNode }> {
    componentDidCatch(error: Error) {
        if (
            error?.name === "ChunkLoadError" ||
            /Loading chunk \d+ failed/i.test(error?.message)
        ) {
            window.location.reload();
        } else {
            throw error;
        }
    }

    render() {
        return this.props.children;
    }
}

const root = createRoot(document.getElementById("root")!);
root.render(
    <StrictMode>
        <Suspense fallback={<div>Loading...</div>}>
            <ChunkErrorBoundary>
                <ClientProvider>
                    <TimeProvider>
                        <ServerProvider>
                            <Root />
                        </ServerProvider>
                    </TimeProvider>
                </ClientProvider>
            </ChunkErrorBoundary>
        </Suspense>
    </StrictMode>,
);
