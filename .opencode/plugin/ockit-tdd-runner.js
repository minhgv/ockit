/**
 * ockit-tdd-runner.js — OpenCode Native TDD Execution Plugin
 * Exposes a custom `run_tdd` tool that routes to the correct multi-language
 * test runner (Python, TypeScript, JavaScript, Go, Rust, PHP).
 */

import { execSync } from "node:child_process";
import { tool } from "@opencode-ai/plugin";

const RUNNERS = {
	python: "pytest",
	typescript: "npx vitest run",
	javascript: "npx vitest run",
	go: "go test ./...",
	rust: "cargo test",
	php: "vendor/bin/phpunit",
};

export const OckitTddRunner = async () => {
	return {
		tool: {
			run_tdd: tool({
				description:
					"Run the test suite for the given programming language using the project's standard test runner (pytest, vitest, go test, cargo test, phpunit). Returns the runner output.",
				args: {
					lang: tool.schema.enum([
						"python",
						"typescript",
						"javascript",
						"go",
						"rust",
						"php",
					]),
				},
				async execute(args) {
					const command = RUNNERS[args.lang];
					let output;
					try {
						output = execSync(command, {
							encoding: "utf-8",
							stdio: ["ignore", "pipe", "pipe"],
						});
					} catch (error) {
						const stderr = error.stderr
							? error.stderr.toString()
							: String(error.message);
						throw new Error(
							`[ockit-tdd-runner] Test run failed for '${args.lang}' with '${command}': ${stderr.trim()}. Fix the failing test or implementation and re-run.`,
						);
					}
					return (
						output.trim() ||
						`Test runner '${command}' completed with no output.`
					);
				},
			}),
		},
	};
};
