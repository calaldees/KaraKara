import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

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
    },
    plugins: [react()],
});
