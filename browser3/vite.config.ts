import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import svgr from "vite-plugin-svgr";
import { VitePWA } from "vite-plugin-pwa";
import eslint from "vite-plugin-eslint";

// https://vitejs.dev/config/
export default defineConfig({
    build: {
        target: ["es2015", "ios11"],
    },
    plugins: [
        react(),
        svgr(),
        eslint(),
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
    ],
});
