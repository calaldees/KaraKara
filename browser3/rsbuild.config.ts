import { defineConfig } from "@rsbuild/core";
import { pluginReact } from "@rsbuild/plugin-react";
import { pluginSass } from "@rsbuild/plugin-sass";
import { execSync } from "child_process";

const isDev = process.env.NODE_ENV !== "production";

const getGitCommitHash = () => {
    try {
        return execSync("git rev-parse --short HEAD").toString().trim();
    } catch {
        return "unknown";
    }
};

const getBuildDate = () => {
    return new Date().toISOString();
};

export default defineConfig({
    plugins: [pluginReact(), pluginSass()],
    html: {
        template: "./src/static/index.html",
        title: "KaraKara",
        favicon: "./src/static/favicon.svg",
        meta: {
            description: "KaraKara Song Browser",
            viewport: [
                "width=device-width",
                "initial-scale=1",
                "interactive-widget=resizes-content",
            ].join(", "),
            themeColor: "#e9e9e9",
            appleMobileWebAppCapable: "yes",
            mobileWebAppCapable: "yes",
        },
        appIcon: {
            name: "KaraKara",
            icons: [
                // 192, 512
                {
                    src: "./src/static/apple-touch-icon.png",
                    size: 180,
                    target: "apple-touch-icon",
                },
                {
                    src: "./src/static/favicon.svg",
                    size: 512,
                },
            ],
        },
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
        define: {
            __COMMIT__: JSON.stringify(getGitCommitHash()),
            __BUILD_DATE__: JSON.stringify(getBuildDate()),
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
        inlineStyles: true,
    },
    server: {
        host: "127.0.0.1",
        port: 1236,
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
