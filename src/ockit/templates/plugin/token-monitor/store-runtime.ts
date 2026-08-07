import type {
	createStore as createStoreT,
	produce as produceT,
	Store,
} from "solid-js/store";
// solid-js/store only ships types for the package root; the runtime must use
// the reactive subpath so store updates are tracked.
import * as runtime from "solid-js/store/dist/store.js";

export const createStore: typeof createStoreT = runtime.createStore;
export const produce: typeof produceT = runtime.produce;
export type { Store };
