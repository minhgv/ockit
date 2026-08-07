import type {
	Accessor,
	createComponent as createComponentT,
	createMemo as createMemoT,
	createSignal as createSignalT,
	For as ForT,
	JSX,
} from "solid-js";
// solid-js only ships types for the package root; the runtime must use the
// reactive subpath so the signal graph is actually wired.
import * as runtime from "solid-js/dist/solid.js";

export const createComponent: typeof createComponentT = runtime.createComponent;
export const createMemo: typeof createMemoT = runtime.createMemo;
export const createSignal: typeof createSignalT = runtime.createSignal;
export const For: typeof ForT = runtime.For;
export type { Accessor, JSX };
