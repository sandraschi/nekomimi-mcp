import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
	plugins: [react(), tailwindcss()],
	server: {
		host: "127.0.0.1",
		port: 11129,
		proxy: {
			"/api": "http://127.0.0.1:11128",
			"/mcp": "http://127.0.0.1:11128",
		},
	},
});
