/** @jsxImportSource @opentui/solid */

import { TextAttributes } from "@opentui/core";
import type { Accessor, JSX } from "./solid-runtime.js";
import { createMemo, For } from "./solid-runtime.js";
import type { PerModelTotals } from "./token-state.js";
import { totalTokens } from "./token-state.js";

export function formatToken(value: number): string {
	if (value >= 999_950) {
		return `${(value / 1_000_000).toFixed(1)}M`;
	}
	if (value >= 1_000) {
		return `${(value / 1_000).toFixed(1)}K`;
	}
	return String(value);
}

export function formatCost(value: number): string {
	if (value <= 0) return "-";
	return `$${value.toFixed(2)}`;
}

export function formatPercent(part: number, total: number): string {
	if (total <= 0) return "0%";
	return `${Math.round((part / total) * 100)}%`;
}

function panelTotals(models: PerModelTotals[]): {
	messageCount: number;
	tokens: number;
	cost: number;
} {
	let messageCount = 0;
	let tokens = 0;
	let cost = 0;
	for (const m of models) {
		messageCount += m.messageCount;
		tokens += totalTokens(m);
		cost += m.cost;
	}
	return { messageCount, tokens, cost };
}

export function TokenPanel(props: {
	getModels: () => PerModelTotals[];
	tick?: Accessor<number>;
}): JSX.Element {
	// SolidJS runs component functions once in untracked scope. Reading props
	// inside createMemo makes the JSX reactive: the OpenTUI reconciler will
	// repaint the affected text nodes whenever the tick signal or store changes.
	const models = createMemo(() => {
		props.tick?.();
		return props.getModels();
	});
	const now = createMemo(() => {
		props.tick?.();
		return new Date().toLocaleTimeString();
	});
	const totals = createMemo(() => panelTotals(models()));
	// No padding on the root box: the host sidebar already applies paddingLeft
	// (routes/session/sidebar.tsx) and the built-in sidebar panels (Context, MCP,
	// Todo, Files, LSP) render flush, so an extra padding={1} here would shift the
	// panel's left edge 1 column right of the other panels.
	return (
		<box flexDirection="column">
			<text attributes={TextAttributes.BOLD} fg="cyan">
				Model Requests
			</text>
			{models().length === 0 ? (
				<text attributes={TextAttributes.DIM} fg="gray">
					No model activity yet {now()}
				</text>
			) : (
				<>
					<text attributes={TextAttributes.DIM}>
						{totals().messageCount} msgs · {formatToken(totals().tokens)} tok ·{" "}
						{formatCost(totals().cost)}
					</text>
					<box flexDirection="column" marginTop={1}>
						<For each={models()}>
							{(m) => {
								const total = totalTokens(m);
								return (
									<box flexDirection="column" marginBottom={1}>
										<box flexDirection="row">
											<text attributes={TextAttributes.BOLD}>{m.modelID}</text>
											<text attributes={TextAttributes.DIM} fg="gray">
												{" "}
												({m.messageCount} msgs)
											</text>
										</box>
										<text attributes={TextAttributes.DIM}>
											In {formatToken(m.inputTokens)} · CacheR{" "}
											{formatToken(m.cacheReadTokens)} (
											{formatPercent(m.cacheReadTokens, total)})
										</text>
										<text attributes={TextAttributes.DIM}>
											Out {formatToken(m.outputTokens)} · CacheW{" "}
											{formatToken(m.cacheWriteTokens)} (
											{formatPercent(m.cacheWriteTokens, total)})
										</text>
										<text attributes={TextAttributes.DIM}>
											Reasoning {formatToken(m.reasoningTokens)} · Cost{" "}
											{formatCost(m.cost)}
										</text>
									</box>
								);
							}}
						</For>
					</box>
				</>
			)}
		</box>
	);
}
