import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

// https://vite.dev/config/
export default defineConfig({
    build: {
        target: ["es2015", "ios11"],
    },
    plugins: [react()],
});
