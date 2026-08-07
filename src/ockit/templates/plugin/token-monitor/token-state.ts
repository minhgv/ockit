import type { AssistantMessage } from "@opencode-ai/sdk/v2/types";
import { createStore, produce } from "./store-runtime.js";

export interface PerModelTotals {
	providerID: string;
	modelID: string;
	inputTokens: number;
	cacheReadTokens: number;
	outputTokens: number;
	cacheWriteTokens: number;
	reasoningTokens: number;
	cost: number;
	messageCount: number;
}

export const MAX_MODEL_ENTRIES = 50;

export function modelKey(providerID: string, modelID: string): string {
	return `${providerID}/${modelID}`;
}

export function totalTokens(model: PerModelTotals): number {
	return (
		model.inputTokens +
		model.cacheReadTokens +
		model.outputTokens +
		model.cacheWriteTokens +
		model.reasoningTokens
	);
}

export type TokenStore = ReturnType<typeof createTokenStore>;

export function createTokenStore() {
	const [models, setModels] = createStore<Record<string, PerModelTotals>>({});
	const seen = new Set<string>();

	function getModels(): PerModelTotals[] {
		return Object.values(models).sort(
			(a, b) => totalTokens(b) - totalTokens(a),
		);
	}

	return { models, seen, getModels, _setModels: setModels };
}

export interface StepTokenUsage {
	assistantMessageID: string;
	tokens: AssistantMessage["tokens"];
}

function addTokensToModel(
	store: TokenStore,
	providerID: string,
	modelID: string,
	tokens: AssistantMessage["tokens"],
	cost = 0,
): void {
	const key = modelKey(providerID, modelID);
	const existing = store.models[key];

	const input = tokens.input > 0 ? tokens.input : 0;
	const output = tokens.output > 0 ? tokens.output : 0;
	const reasoning = tokens.reasoning > 0 ? tokens.reasoning : 0;
	const cacheRead =
		(tokens.cache?.read ?? 0) > 0 ? (tokens.cache?.read ?? 0) : 0;
	const cacheWrite =
		(tokens.cache?.write ?? 0) > 0 ? (tokens.cache?.write ?? 0) : 0;
	const costValue = cost > 0 ? cost : 0;

	if (!existing) {
		const entries = Object.entries(store.models);
		if (entries.length >= MAX_MODEL_ENTRIES) {
			let minKey = entries[0][0];
			let minTotal = totalTokens(entries[0][1]);
			for (const [k, v] of entries) {
				const t = totalTokens(v);
				if (t < minTotal) {
					minTotal = t;
					minKey = k;
				}
			}
			store._setModels(minKey, undefined!);
		}
		store._setModels(key, {
			providerID,
			modelID,
			inputTokens: input,
			cacheReadTokens: cacheRead,
			outputTokens: output,
			cacheWriteTokens: cacheWrite,
			reasoningTokens: reasoning,
			cost: costValue,
			messageCount: 1,
		});
	} else {
		store._setModels(
			key,
			produce((m: PerModelTotals) => {
				m.inputTokens += input;
				m.cacheReadTokens += cacheRead;
				m.outputTokens += output;
				m.cacheWriteTokens += cacheWrite;
				m.reasoningTokens += reasoning;
				m.cost += costValue;
				m.messageCount += 1;
			}),
		);
	}
}

export function aggregateMessage(
	store: TokenStore,
	msg: AssistantMessage,
): boolean {
	if (!msg.tokens) return false;
	if (!msg.time.completed) return false;
	if (store.seen.has(msg.id)) return false;
	store.seen.add(msg.id);

	addTokensToModel(store, msg.providerID, msg.modelID, msg.tokens, msg.cost);
	return true;
}

/**
 * Aggregate per-step token usage from `session.next.step.ended`.
 *
 * In opencode v2 each step creates exactly one assistant message whose id
 * equals `assistantMessageID` (see SessionMessageUpdater.step.started). The
 * dedup set is shared with `aggregateMessage` so the same assistant message
 * is never counted twice even when both `message.updated` and
 * `session.next.step.ended` arrive for it.
 */
export function aggregateStep(
	store: TokenStore,
	step: StepTokenUsage,
	model: { providerID: string; modelID: string },
): boolean {
	if (!step.tokens) return false;
	if (store.seen.has(step.assistantMessageID)) return false;
	store.seen.add(step.assistantMessageID);

	addTokensToModel(store, model.providerID, model.modelID, step.tokens);
	return true;
}
