import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { pluginSass } from "@rsbuild/plugin-sass";
import { pluginSvgr } from "@rsbuild/plugin-svgr";

const isDev = process.env.NODE_ENV !== "production";

export default defineConfig({
    plugins: [pluginReact(), pluginSass(), pluginSvgr()],
    html: {
        template: "./index.html",
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
