import { readFileSync } from "node:fs";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const pkg = JSON.parse(
	readFileSync(new URL("./package.json", import.meta.url), "utf-8"),
) as {
	version: string;
};

export default defineConfig({
	plugins: [react(), tailwindcss()],
	define: {
		__APP_VERSION__: JSON.stringify(pkg.version),
	},
	server: {
		host: "127.0.0.1",
		port: 11129,
		proxy: {
			"/api": "http://127.0.0.1:11128",
			"/mcp": "http://127.0.0.1:11128",
		},
	},
});
