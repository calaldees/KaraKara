import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
    build: {
        target: ["es2015", "ios11"],
        // Initial load time doesn't matter for Player, loading
        // everything up-front for stability is more important.
        chunkSizeWarningLimit: 2000,
    },
    plugins: [
        react({
            babel: {
                plugins: ["babel-plugin-react-compiler"],
            },
        }),
    ],
});
