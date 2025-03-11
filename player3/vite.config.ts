import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import eslint from "vite-plugin-eslint";

// https://vite.dev/config/
export default defineConfig({
    build: {
        target: ["es2015", "ios11"],
    },
    plugins: [react(), eslint()],
});
