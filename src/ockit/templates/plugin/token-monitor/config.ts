export interface TokenMonitorOptions {
	pollIntervalMs?: number;
}

export const DEFAULT_POLL_INTERVAL_MS = 30000;
export const MIN_POLL_INTERVAL_MS = 5000;
export const MAX_POLL_INTERVAL_MS = 300000;

export function parsePollInterval(options?: TokenMonitorOptions): number {
	const raw = options?.pollIntervalMs ?? DEFAULT_POLL_INTERVAL_MS;
	if (typeof raw !== "number" || !Number.isFinite(raw)) {
		return DEFAULT_POLL_INTERVAL_MS;
	}
	return Math.min(MAX_POLL_INTERVAL_MS, Math.max(MIN_POLL_INTERVAL_MS, raw));
}
