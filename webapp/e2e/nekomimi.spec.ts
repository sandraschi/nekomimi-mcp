import { expect, test } from "@playwright/test";

test.describe("nekomimi-mcp webapp", () => {
	test("dashboard shows hero, KPIs, and intent panel", async ({ page }) => {
		await page.goto("/");
		await expect(page.getByTestId("dashboard-hero")).toBeVisible();
		await expect(page.getByTestId("kpi-backend")).toBeVisible();
		await expect(page.getByTestId("kpi-renderers")).toBeVisible();
		await expect(page.getByTestId("kpi-intents")).toBeVisible();
		await page.screenshot({ path: "../docs/screenshots/dashboard.png" });
	});

	test("tools page lists intent cards", async ({ page }) => {
		await page.goto("/tools");
		await expect(page.getByTestId("tools-page")).toBeVisible();
		await expect(page.getByTestId("tool-card-nod")).toBeVisible({
			timeout: 15000,
		});
		await page.screenshot({ path: "../docs/screenshots/tools.png" });
	});

	test("inbox page loads with recordings or empty state", async ({ page }) => {
		await page.goto("/inbox");
		await expect(page.getByTestId("inbox-page")).toBeVisible();
	});

	test("apps page discovers fleet apps", async ({ page }) => {
		await page.goto("/apps");
		await expect(page.getByTestId("apps-page")).toBeVisible();
		await expect(page.getByTestId("fleet-app-nekomimi-mcp")).toBeVisible({
			timeout: 15000,
		});
	});

	test("chat sends via offline fallback and shows provider status", async ({
		page,
	}) => {
		await page.goto("/chat");
		await expect(page.getByTestId("chat-page")).toBeVisible();
		await expect(page.getByTestId("chat-provider-status")).toBeVisible();
		await page.getByTestId("chat-input").fill("do a nod");
		await page.getByTestId("chat-send").click();
		await expect(page.getByTestId("chat-messages")).toContainText("nod", {
			timeout: 20000,
		});
	});

	test("settings shows backend, onboarding panel, and LLM section", async ({
		page,
	}) => {
		await page.goto("/settings");
		await expect(page.getByTestId("settings-page")).toBeVisible();
		await expect(page.getByTestId("onboarding-panel")).toBeVisible();
		await expect(page.getByTestId("llm-provider-select")).toBeVisible({
			timeout: 20000,
		});
	});

	test("sidebar navigates to inbox and apps", async ({ page }) => {
		await page.goto("/");
		await page.getByTestId("nav-inbox").click();
		await expect(page).toHaveURL(/\/inbox/);
		await page.getByTestId("nav-apps").click();
		await expect(page).toHaveURL(/\/apps/);
	});
});
