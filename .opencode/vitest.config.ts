import { defineConfig } from "vitest/config";

// Vitest harness for the token-monitor TUI plugin (and any future TS plugins).
// Config lives in `.opencode/` so root stays Python-only; run via
// `npm --prefix .opencode test` (R-006, R-018).
export default defineConfig({
	test: {
		include: ["plugin/**/*.test.ts"],
	},
});
