export function startPolling(
	callback: () => void,
	intervalMs: number,
	signal?: AbortSignal,
): { cleanup: () => void; promise: Promise<void> } {
	let stopped = false;
	let timer: ReturnType<typeof setInterval> | null = null;

	const cleanup = () => {
		stopped = true;
		if (timer !== null) {
			clearInterval(timer);
			timer = null;
		}
	};

	const promise = new Promise<void>((resolve) => {
		timer = setInterval(() => {
			if (stopped) return;
			callback();
		}, intervalMs);

		if (signal) {
			if (signal.aborted) {
				cleanup();
				resolve();
				return;
			}
			signal.addEventListener(
				"abort",
				() => {
					cleanup();
					resolve();
				},
				{ once: true },
			);
		}
	});

	return { cleanup, promise };
}
