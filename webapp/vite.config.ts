import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 11129,
    proxy: {
      "/api": "http://127.0.0.1:11128",
      "/mcp": "http://127.0.0.1:11128",
    },
  },
});
