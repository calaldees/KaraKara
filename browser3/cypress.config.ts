import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    specPattern: "**/*.cye.{js,jsx,ts,tsx}",
    baseUrl: "http://localhost:1234",
  },

  component: {
    specPattern: "**/*.cyc.{js,jsx,ts,tsx}",
    devServer: {
      framework: "react",
      bundler: "vite",
    },
  },
});
