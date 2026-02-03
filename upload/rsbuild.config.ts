import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";

const backend = process.env.BACKEND ?? "http://127.0.0.1:8000";

export default defineConfig({
    plugins: [pluginReact()],
    source: {
        entry: { index: "./frontend/index.tsx" },
    },
    html: {
        title: "KaraKara Uploader",
        favicon: "frontend/static/favicon.svg",
        //template: "frontend/static/index.html",
    },
    server: {
        proxy: {
            "/api": { target: backend },
        },
    },
});
