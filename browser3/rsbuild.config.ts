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
            index: "./src/browser.tsx",
        },
    },
    output: {
        target: "web",
        distPath: {
            root: "dist",
        },
        assetPrefix: "/browser3/",
        sourceMap: isDev,
        polyfill: "usage",
        overrideBrowserslist: [
            // stats from minami 2024
            "ios_saf >= 15",
            "FirefoxAndroid >= 122",
            "ChromeAndroid >= 111",
            "Firefox >= 122",
            "Chrome >= 121",
            // recommended for mobile apps
            "ios >= 9",
            "android >= 4.4",
            "last 2 versions",
            "> 0.2%",
            "not dead",
        ],
    },
    server: {
        host: "127.0.0.1",
        port: 1236,
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
