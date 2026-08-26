import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { pluginSass } from "@rsbuild/plugin-sass";

const isDev = process.env.NODE_ENV !== "production";

const getBuildDate = () => {
    return new Date().toISOString();
};

export default defineConfig({
    plugins: [pluginReact(), pluginSass()],
    html: {
        title: "KaraKara Player",
        favicon: "./src/static/favicon.svg",
        meta: {
            viewport: ["width=device-width", "initial-scale=1"].join(", "),
        },
    },
    source: {
        define: {
            __BUILD_DATE__: JSON.stringify(getBuildDate()),
        },
    },
    output: {
        sourceMap: isDev,
        overrideBrowserslist: [
            // Only chrome supports styled subs
            "Chrome >= 121",
        ],
    },
    server: {
        host: "127.0.0.1",
        port: 1237,
        proxy: {
            "/files": "https://karakara.uk",
            "/api": {
                target: "https://karakara.uk",
                ws: true,
            },
        },
    },
});
