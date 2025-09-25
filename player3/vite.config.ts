import react from "@vitejs/plugin-react-swc";
import Sonda from "sonda/vite";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
    resolve: {
        alias: {
            "@": "/src",
        },
    },
    build: {
        // Initial load time doesn't matter for Player, loading
        // everything up-front for stability is more important.
        chunkSizeWarningLimit: 2000,
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
    plugins: [react(), Sonda()],
});
