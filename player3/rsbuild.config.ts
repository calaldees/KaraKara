import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { pluginSass } from "@rsbuild/plugin-sass";

const isDev = process.env.NODE_ENV !== "production";

export default defineConfig({
    plugins: [pluginReact(), pluginSass()],
    html: {
        template: "./src/static/index.html",
        title: "KaraKara Player",
        favicon: "./src/static/favicon.svg",
        meta: {
            description: "KaraKara Player",
            viewport: ["width=device-width", "initial-scale=1"].join(", "),
        },
    },
    performance: {
        chunkSplit: {
            strategy: "all-in-one",
        },
    },
    source: {
        entry: {
            index: "./src/player.tsx",
        },
    },
    output: {
        target: "web",
        distPath: {
            root: "dist",
        },
        assetPrefix: "/player3/",
        sourceMap: isDev,
        polyfill: "usage",
        overrideBrowserslist: [
            // Only chrome supports styled subs
            "Chrome >= 121",
        ],
    },
    server: {
        host: "127.0.0.1",
        port: 1237,
        proxy: {
            "/api": "https://karakara.uk",
            "/files": "https://karakara.uk",
            "/mqtt": {
                target: "https://karakara.uk",
                ws: true,
            },
        },
    },
    dev: {
        assetPrefix: "/",
    },
    tools: {
        rspack: {
            experiments: {
                css: true,
            },
        },
    },
});
