import type { TuiPluginModule } from "@opencode-ai/plugin/tui";
import type { AssistantMessage } from "@opencode-ai/sdk/v2/types";
import { parsePollInterval } from "./config.js";
import { startPolling } from "./lifecycle.js";
import { createComponent, createSignal } from "./solid-runtime.js";
import { TokenPanel } from "./token-panel.js";
import {
	aggregateMessage,
	aggregateStep,
	createTokenStore,
} from "./token-state.js";

const tui: TuiPluginModule["tui"] = async (api, options) => {
	const store = createTokenStore();
	const intervalMs = parsePollInterval(options);
	const [tick, setTick] = createSignal(0);

	const unsubEvent = api.event.on("message.updated", (event) => {
		try {
			const info = event.properties?.info;
			if (info?.role !== "assistant") return;
			const msg = info as AssistantMessage;
			aggregateMessage(store, msg);
		} catch (error) {
			console.error(
				`[token-monitor] message.updated handler failed: ${
					error instanceof Error ? error.message : String(error)
				}`,
			);
		}
	});

	// session.next.step.started carries the model for the step. Remember it so
	// the matching step.ended (which carries only tokens) can be attributed to
	// the correct model. In v2 the assistantMessageID IS the assistant message
	// id, so the shared `seen` set prevents double counting with message.updated.
	const stepModels = new Map<string, { providerID: string; modelID: string }>();
	const unsubStepStarted = api.event.on(
		"session.next.step.started",
		(event) => {
			try {
				const p = event.properties;
				if (!p?.model) return;
				stepModels.set(p.assistantMessageID, {
					providerID: p.model.providerID,
					modelID: p.model.id,
				});
			} catch (error) {
				console.error(
					`[token-monitor] session.next.step.started handler failed: ${
						error instanceof Error ? error.message : String(error)
					}`,
				);
			}
		},
	);

	const unsubStepEnded = api.event.on("session.next.step.ended", (event) => {
		try {
			const p = event.properties;
			if (!p?.assistantMessageID) return;
			const model = stepModels.get(p.assistantMessageID);
			if (!model) return;
			aggregateStep(store, p, model);
			// Bounded state: the step is done, so drop its model entry. The map
			// then holds only in-flight steps, not one entry per completed step.
			stepModels.delete(p.assistantMessageID);
		} catch (error) {
			console.error(
				`[token-monitor] session.next.step.ended handler failed: ${
					error instanceof Error ? error.message : String(error)
				}`,
			);
		}
	});

	api.slots.register({
		slots: {
			sidebar_content() {
				return createComponent(TokenPanel, {
					getModels: store.getModels,
					tick,
				});
			},
		},
	});

	const { cleanup: stopPolling } = startPolling(
		() => {
			setTick((t) => t + 1);
		},
		intervalMs,
		api.lifecycle.signal,
	);

	api.lifecycle.onDispose(() => {
		unsubEvent();
		unsubStepStarted();
		unsubStepEnded();
		stepModels.clear();
		stopPolling();
	});
};

export default {
	id: "token-monitor",
	tui,
} satisfies TuiPluginModule;
