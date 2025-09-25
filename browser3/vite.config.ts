import react from "@vitejs/plugin-react-swc";
import Sonda from "sonda/vite";
import { defineConfig } from "vite";
// import { VitePWA } from "vite-plugin-pwa";

// https://vite.dev/config/
export default defineConfig({
    resolve: {
        alias: {
            "@": "/src",
        },
    },
    build: {
        target: ["es2015", "ios11"],
        sourcemap: true,
    },
    server: {
        proxy: {
            "/api": {
                target: "https://karakara.uk",
                changeOrigin: true,
            },
            "/files": {
                target: "https://karakara.uk",
                changeOrigin: true,
            },
            "/mqtt": {
                target: "https://karakara.uk",
                changeOrigin: true,
                ws: true,
            },
        },
    },
    plugins: [
        react(),
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
