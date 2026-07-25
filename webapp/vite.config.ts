import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 10701,
    proxy: {
      "/api": "http://127.0.0.1:10700",
      "/mcp": "http://127.0.0.1:10700",
    },
  },
});
