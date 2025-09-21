import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import Sonda from "sonda/vite";
// import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
    build: {
        target: ["es2015", "ios11"],
        sourcemap: true,
    },
    plugins: [
        react({
            babel: {
                plugins: ["babel-plugin-react-compiler"],
            },
        }),
        svgr(),
        Sonda(),
        /*
        VitePWA({
            injectRegister: null,
            manifest: {
                name: "KaraKara",
                short_name: "KaraKara",
                description: "KaraKara Song Browser",
                theme_color: "#e9e9e9",
                icons: [
                    {
                        src: "favicon.svg",
                        sizes: "any",
                        type: "image/svg",
                        purpose: "maskable any",
                    },
                ],
            },
        }),
        */
    ],
});
