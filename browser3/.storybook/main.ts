import path from "node:path";
import { fileURLToPath } from "node:url";
import type { StorybookConfig } from "storybook-react-rsbuild";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const config: StorybookConfig = {
    stories: ["../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
    addons: [],
    framework: "storybook-react-rsbuild",
    staticDirs: [{ from: "../fixtures", to: "/files" }],
    rsbuildFinal: async (config) => {
        config.resolve = config.resolve || {};
        config.resolve.alias = {
            ...config.resolve.alias,
            "@": path.resolve(__dirname, "../src"),
        };
        return config;
    },
};
export default config;
