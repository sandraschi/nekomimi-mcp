import { defineConfig } from "@playwright/test";

export default defineConfig({
	testDir: "./e2e",
	timeout: 60000,
	retries: 1,
	use: {
		baseURL: "http://127.0.0.1:11129",
		headless: true,
		screenshot: "only-on-failure",
	},
	webServer: [
		{
			command:
				"C:\\Users\\sandr\\.local\\bin\\uv.exe run python -m nekomimi_mcp.server --http --port 11128",
			port: 11128,
			cwd: "../",
			timeout: 60000,
			reuseExistingServer: true,
		},
		{
			command:
				"C:\\Users\\sandr\\.bun\\bin\\bun.exe run build && C:\\Users\\sandr\\.bun\\bin\\bun.exe x vite preview --port 11129 --strictPort",
			port: 11129,
			cwd: ".",
			timeout: 180000,
			reuseExistingServer: true,
		},
	],
});
