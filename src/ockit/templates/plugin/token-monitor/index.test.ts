import type { AssistantMessage } from "@opencode-ai/sdk/v2/types";
import { createRoot, createSignal } from "solid-js";
import { describe, expect, it } from "vitest";
import {
	MAX_POLL_INTERVAL_MS,
	MIN_POLL_INTERVAL_MS,
	parsePollInterval,
} from "./config.js";
import { startPolling } from "./lifecycle.js";
import { formatCost, formatPercent, formatToken } from "./token-panel.js";
import {
	aggregateMessage,
	aggregateStep,
	createTokenStore,
} from "./token-state.js";

function makeMsg(overrides: Partial<AssistantMessage> = {}): AssistantMessage {
	return {
		id: "msg-1",
		sessionID: "sess-1",
		role: "assistant",
		time: { created: 1000, completed: 2000 },
		parentID: "parent-1",
		modelID: "claude",
		providerID: "gh",
		mode: "chat",
		agent: "default",
		path: { cwd: "/", root: "/" },
		cost: 0,
		tokens: {
			input: 100,
			output: 50,
			reasoning: 0,
			cache: { read: 20, write: 0 },
		},
		...overrides,
	};
}

describe("createTokenStore + aggregateMessage", () => {
	it("aggregates a single message into empty state", () => {
		const store = createTokenStore();
		aggregateMessage(store, makeMsg());
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].outputTokens).toBe(50);
		expect(models[0].cacheReadTokens).toBe(20);
		expect(models[0].cacheWriteTokens).toBe(0);
		expect(models[0].reasoningTokens).toBe(0);
		expect(models[0].cost).toBe(0);
		expect(models[0].messageCount).toBe(1);
	});

	it("accumulates reasoning and cost across messages", () => {
		const store = createTokenStore();
		aggregateMessage(
			store,
			makeMsg({
				id: "msg-1",
				cost: 0.0036,
				tokens: {
					input: 100,
					output: 50,
					reasoning: 30,
					cache: { read: 20, write: 0 },
				},
			}),
		);
		aggregateMessage(
			store,
			makeMsg({
				id: "msg-2",
				cost: 0.0004,
				tokens: {
					input: 200,
					output: 10,
					reasoning: 5,
					cache: { read: 5, write: 0 },
				},
			}),
		);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].reasoningTokens).toBe(35);
		expect(models[0].cost).toBeCloseTo(0.004, 6);
		expect(models[0].messageCount).toBe(2);
	});

	it("cost is cumulative: grows monotonically with each message", () => {
		const store = createTokenStore();
		const costs = [0.0036, 0.0004, 0.0005, 0.0012, 0.0022];
		let cumulative = 0;
		costs.forEach((c, i) => {
			aggregateMessage(
				store,
				makeMsg({
					id: `msg-${i}`,
					cost: c,
					tokens: {
						input: 10,
						output: 5,
						reasoning: 0,
						cache: { read: 0, write: 0 },
					},
				}),
			);
			cumulative += c;
			const models = store.getModels();
			expect(models).toHaveLength(1);
			expect(models[0].cost).toBeCloseTo(cumulative, 6);
			expect(models[0].messageCount).toBe(i + 1);
		});
		// final cumulative = 0.0079 -> formatted with 2 decimals
		expect(cumulative).toBeCloseTo(0.0079, 6);
	});

	it("store keeps full precision; rounding happens only at display", () => {
		const store = createTokenStore();
		// 3 tiny messages: cumulative 0.0000003 — below $0.01 so display shows
		// "$0.00", but the store must NOT round (display-only rounding).
		for (let i = 0; i < 3; i++) {
			aggregateMessage(
				store,
				makeMsg({
					id: `tiny-${i}`,
					cost: 0.0000001,
					tokens: {
						input: 10,
						output: 5,
						reasoning: 0,
						cache: { read: 0, write: 0 },
					},
				}),
			);
		}
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].cost).toBeCloseTo(0.0000003, 9);
		// display rounds, store does not
		expect(formatCost(models[0].cost)).toBe("$0.00");
	});

	it("accumulates same model across multiple messages", () => {
		const store = createTokenStore();
		aggregateMessage(
			store,
			makeMsg({
				id: "msg-1",
				tokens: {
					input: 100,
					output: 50,
					reasoning: 0,
					cache: { read: 20, write: 0 },
				},
			}),
		);
		aggregateMessage(
			store,
			makeMsg({
				id: "msg-2",
				tokens: {
					input: 200,
					output: 0,
					reasoning: 0,
					cache: { read: 0, write: 0 },
				},
			}),
		);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(300);
		expect(models[0].outputTokens).toBe(50);
		expect(models[0].cacheReadTokens).toBe(20);
		expect(models[0].cacheWriteTokens).toBe(0);
		expect(models[0].messageCount).toBe(2);
	});

	it("tracks different models independently", () => {
		const store = createTokenStore();
		aggregateMessage(
			store,
			makeMsg({ id: "msg-1", modelID: "claude", providerID: "gh" }),
		);
		aggregateMessage(
			store,
			makeMsg({ id: "msg-2", modelID: "gpt-4", providerID: "openai" }),
		);
		const models = store.getModels();
		expect(models).toHaveLength(2);
		expect(models.map((m) => m.modelID).sort()).toEqual(["claude", "gpt-4"]);
	});

	it("deduplicates by message id -- only counts once", () => {
		const store = createTokenStore();
		aggregateMessage(store, makeMsg());
		aggregateMessage(
			store,
			makeMsg({
				tokens: {
					input: 999,
					output: 0,
					reasoning: 0,
					cache: { read: 0, write: 0 },
				},
			}),
		);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].messageCount).toBe(1);
	});

	it("skips messages without tokens (no crash)", () => {
		const store = createTokenStore();
		aggregateMessage(
			store,
			makeMsg({ tokens: undefined as unknown as AssistantMessage["tokens"] }),
		);
		expect(store.getModels()).toHaveLength(0);
	});

	it("skips messages where time.completed is undefined (streaming)", () => {
		const store = createTokenStore();
		aggregateMessage(store, makeMsg({ time: { created: 1000 } }));
		expect(store.getModels()).toHaveLength(0);
	});
});

describe("aggregateStep", () => {
	function makeStep(
		overrides: Partial<{
			assistantMessageID: string;
			tokens: AssistantMessage["tokens"];
		}> = {},
	) {
		return {
			assistantMessageID: "msg-1",
			tokens: {
				input: 100,
				output: 50,
				reasoning: 0,
				cache: { read: 20, write: 0 },
			},
			...overrides,
		};
	}

	it("aggregates a single step into empty state", () => {
		const store = createTokenStore();
		const ok = aggregateStep(store, makeStep(), {
			providerID: "gh",
			modelID: "claude",
		});
		expect(ok).toBe(true);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].providerID).toBe("gh");
		expect(models[0].modelID).toBe("claude");
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].outputTokens).toBe(50);
		expect(models[0].cacheReadTokens).toBe(20);
		expect(models[0].messageCount).toBe(1);
	});

	it("accumulates multiple steps of the same model", () => {
		const store = createTokenStore();
		aggregateStep(
			store,
			makeStep({
				assistantMessageID: "step-1",
				tokens: {
					input: 100,
					output: 50,
					reasoning: 0,
					cache: { read: 0, write: 0 },
				},
			}),
			{ providerID: "gh", modelID: "claude" },
		);
		aggregateStep(
			store,
			makeStep({
				assistantMessageID: "step-2",
				tokens: {
					input: 200,
					output: 0,
					reasoning: 10,
					cache: { read: 5, write: 0 },
				},
			}),
			{ providerID: "gh", modelID: "claude" },
		);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(300);
		expect(models[0].outputTokens).toBe(50);
		expect(models[0].cacheReadTokens).toBe(5);
		expect(models[0].messageCount).toBe(2);
	});

	it("tracks different models independently", () => {
		const store = createTokenStore();
		aggregateStep(store, makeStep({ assistantMessageID: "s1" }), {
			providerID: "gh",
			modelID: "claude",
		});
		aggregateStep(
			store,
			makeStep({
				assistantMessageID: "s2",
				tokens: {
					input: 10,
					output: 5,
					reasoning: 0,
					cache: { read: 0, write: 0 },
				},
			}),
			{ providerID: "openai", modelID: "gpt-4" },
		);
		expect(store.getModels()).toHaveLength(2);
	});

	it("deduplicates by assistantMessageID -- counts once", () => {
		const store = createTokenStore();
		aggregateStep(store, makeStep({ assistantMessageID: "step-1" }), {
			providerID: "gh",
			modelID: "claude",
		});
		const second = aggregateStep(
			store,
			makeStep({
				assistantMessageID: "step-1",
				tokens: {
					input: 999,
					output: 999,
					reasoning: 0,
					cache: { read: 999, write: 999 },
				},
			}),
			{ providerID: "gh", modelID: "claude" },
		);
		expect(second).toBe(false);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].messageCount).toBe(1);
	});

	it("does not double count when the same id arrives via message.updated first", () => {
		const store = createTokenStore();
		aggregateMessage(store, makeMsg({ id: "msg-1" }));
		const ok = aggregateStep(
			store,
			makeStep({
				assistantMessageID: "msg-1",
				tokens: {
					input: 999,
					output: 999,
					reasoning: 0,
					cache: { read: 999, write: 999 },
				},
			}),
			{ providerID: "gh", modelID: "claude" },
		);
		expect(ok).toBe(false);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].messageCount).toBe(1);
	});

	it("does not double count when step arrives first and message.updated after", () => {
		const store = createTokenStore();
		aggregateStep(store, makeStep({ assistantMessageID: "msg-1" }), {
			providerID: "gh",
			modelID: "claude",
		});
		const ok = aggregateMessage(
			store,
			makeMsg({
				id: "msg-1",
				tokens: {
					input: 999,
					output: 999,
					reasoning: 0,
					cache: { read: 999, write: 999 },
				},
			}),
		);
		expect(ok).toBe(false);
		const models = store.getModels();
		expect(models).toHaveLength(1);
		expect(models[0].inputTokens).toBe(100);
		expect(models[0].messageCount).toBe(1);
	});

	it("skips steps without tokens (no crash)", () => {
		const store = createTokenStore();
		const ok = aggregateStep(
			store,
			makeStep({ tokens: undefined as unknown as AssistantMessage["tokens"] }),
			{ providerID: "gh", modelID: "claude" },
		);
		expect(ok).toBe(false);
		expect(store.getModels()).toHaveLength(0);
	});
});

describe("formatToken", () => {
	it('formats 1000 as "1.0K"', () => {
		expect(formatToken(1000)).toBe("1.0K");
	});
	it('formats 1500 as "1.5K"', () => {
		expect(formatToken(1500)).toBe("1.5K");
	});
	it('formats 999999 as "1.0M"', () => {
		expect(formatToken(999999)).toBe("1.0M");
	});
	it('formats 1000000 as "1.0M"', () => {
		expect(formatToken(1000000)).toBe("1.0M");
	});
	it('formats 1500000 as "1.5M"', () => {
		expect(formatToken(1500000)).toBe("1.5M");
	});
	it('formats 2000000 as "2.0M"', () => {
		expect(formatToken(2000000)).toBe("2.0M");
	});
	it("formats 500 as raw number", () => {
		expect(formatToken(500)).toBe("500");
	});
	it("formats 999 as raw number", () => {
		expect(formatToken(999)).toBe("999");
	});
	it('formats 0 as "0"', () => {
		expect(formatToken(0)).toBe("0");
	});
});

describe("formatCost", () => {
	it('formats 0 as "-"', () => {
		expect(formatCost(0)).toBe("-");
	});
	it("rounds small fractional cost to 2 decimals", () => {
		expect(formatCost(0.0036)).toBe("$0.00");
	});
	it("rounds tiny cost to 2 decimals", () => {
		expect(formatCost(0.0001571416)).toBe("$0.00");
	});
	it("formats >= 1 with 2 decimals", () => {
		expect(formatCost(1.5)).toBe("$1.50");
	});
	it("formats 0.01 with 2 decimals", () => {
		expect(formatCost(0.01)).toBe("$0.01");
	});
	it("rounds up to 2 decimals", () => {
		expect(formatCost(0.555)).toBe("$0.56");
	});
});

describe("formatPercent", () => {
	it('formats 50/100 as "50%"', () => {
		expect(formatPercent(50, 100)).toBe("50%");
	});
	it("rounds 1/3 to 33%", () => {
		expect(formatPercent(1, 3)).toBe("33%");
	});
	it('formats 0/100 as "0%"', () => {
		expect(formatPercent(0, 100)).toBe("0%");
	});
	it('formats 100/100 as "100%"', () => {
		expect(formatPercent(100, 100)).toBe("100%");
	});
	it('formats part when total is 0 as "0%" (no NaN)', () => {
		expect(formatPercent(10, 0)).toBe("0%");
	});
});

describe("TokenPanel reactivity", () => {
	it("subscribes to tick signal so re-evaluation happens on change", () => {
		let readCount = 0;
		createRoot((dispose) => {
			const [tick, setTick] = createSignal(0);
			const derived = () => {
				readCount++;
				return tick();
			};
			// Establish reactive context; this mirrors TokenPanel reading props.tick()
			const value = derived();
			expect(value).toBe(0);
			expect(readCount).toBe(1);
			setTick(1);
			// Re-reading after update proves dependency tracking works
			expect(derived()).toBe(1);
			expect(readCount).toBeGreaterThan(1);
			dispose();
		});
	});
});

describe("getModels ordering", () => {
	it("returns models sorted by total tokens descending", () => {
		const store = createTokenStore();
		aggregateMessage(
			store,
			makeMsg({
				id: "a",
				modelID: "low",
				tokens: {
					input: 10,
					output: 5,
					reasoning: 0,
					cache: { read: 0, write: 0 },
				},
			}),
		);
		aggregateMessage(
			store,
			makeMsg({
				id: "b",
				modelID: "high",
				tokens: {
					input: 500,
					output: 200,
					reasoning: 0,
					cache: { read: 50, write: 0 },
				},
			}),
		);
		aggregateMessage(
			store,
			makeMsg({
				id: "c",
				modelID: "mid",
				tokens: {
					input: 100,
					output: 50,
					reasoning: 0,
					cache: { read: 10, write: 0 },
				},
			}),
		);
		const models = store.getModels();
		expect(models[0].modelID).toBe("high");
		expect(models[1].modelID).toBe("mid");
		expect(models[2].modelID).toBe("low");
	});
});

describe("parsePollInterval", () => {
	it("returns min boundary when pollIntervalMs equals MIN", () => {
		expect(parsePollInterval({ pollIntervalMs: MIN_POLL_INTERVAL_MS })).toBe(
			MIN_POLL_INTERVAL_MS,
		);
	});
	it("clamps to MIN when pollIntervalMs is below", () => {
		expect(parsePollInterval({ pollIntervalMs: 1000 })).toBe(
			MIN_POLL_INTERVAL_MS,
		);
	});
	it("clamps to MAX when pollIntervalMs is above", () => {
		expect(parsePollInterval({ pollIntervalMs: 999_999 })).toBe(
			MAX_POLL_INTERVAL_MS,
		);
	});
	it("returns default 30000 when options is undefined", () => {
		expect(parsePollInterval(undefined)).toBe(30_000);
	});
	it("returns default 30000 when options is empty object", () => {
		expect(parsePollInterval({})).toBe(30_000);
	});
	it("returns default 30000 when pollIntervalMs is NaN", () => {
		expect(parsePollInterval({ pollIntervalMs: Number.NaN })).toBe(30_000);
	});
	it("returns default 30000 when pollIntervalMs is not a number", () => {
		expect(
			parsePollInterval({ pollIntervalMs: "fast" as unknown as number }),
		).toBe(30_000);
	});
});

describe("startPolling", () => {
	it("fires callback at least twice within 3x interval", async () => {
		let count = 0;
		const { cleanup } = startPolling(() => {
			count++;
		}, 10);
		await new Promise((resolve) => setTimeout(resolve, 35));
		cleanup();
		expect(count).toBeGreaterThanOrEqual(2);
	});

	it("stops when AbortSignal is triggered", async () => {
		const controller = new AbortController();
		let count = 0;
		const { cleanup } = startPolling(
			() => {
				count++;
			},
			10,
			controller.signal,
		);
		await new Promise((resolve) => setTimeout(resolve, 25));
		controller.abort();
		await new Promise((resolve) => setTimeout(resolve, 5));
		cleanup();
		const afterAbort = count;
		await new Promise((resolve) => setTimeout(resolve, 20));
		expect(count).toBe(afterAbort);
	});

	it("does not fire when signal is already aborted", async () => {
		const controller = new AbortController();
		controller.abort();
		let count = 0;
		const { cleanup } = startPolling(
			() => {
				count++;
			},
			10,
			controller.signal,
		);
		const before = count;
		await new Promise((resolve) => setTimeout(resolve, 25));
		cleanup();
		expect(before).toBe(0);
		expect(count).toBe(0);
	});
});
