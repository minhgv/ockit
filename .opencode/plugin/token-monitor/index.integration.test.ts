import { describe, expect, it } from "vitest";

type SlotRegistrant = {
	slots?: Record<string, unknown>;
};

// Mirrors the opencode 1.18.x TUI plugin runtime contract:
// - module must default-export { id, tui } (readV1Plugin strict)
// - file plugins must export an id (resolvePluginId)
// - api.slots.register must receive the host slot plugin shape
//   { slots: { <name>(ctx, props) => JSX } }
//
// NOTE: actually rendering the slot requires the OpenTUI native FFI, which is
// Bun-only (not available under vitest/Node). The render path is exercised by
// the Bun smoke test and, ultimately, by opencode itself at startup.
describe("Token Monitor Plugin Module", () => {
	it("default-exports an object with string id + tui function (TuiPluginModule runtime contract)", async () => {
		const mod = await import("./index.js");
		expect(mod.default).toBeTypeOf("object");
		expect(mod.default).not.toBeNull();
		expect(typeof mod.default.id).toBe("string");
		expect(mod.default.id.length).toBeGreaterThan(0);
		expect(typeof mod.default.tui).toBe("function");
	});

	it("does not export server (mutually exclusive TuiPluginModule)", async () => {
		const mod = await import("./index.js");
		expect(mod.default).not.toHaveProperty("server");
	});

	it("tui registers a sidebar_content slot using the host slot plugin shape", async () => {
		const mod = await import("./index.js");
		let registered: SlotRegistrant | undefined;
		const mockApi = {
			event: {
				on: () => () => {},
			},
			slots: {
				register: (plugin: SlotRegistrant) => {
					registered = plugin;
					return "slot-1";
				},
			},
			lifecycle: {
				signal: new AbortController().signal,
				onDispose: () => () => {},
			},
		};

		await expect(
			mod.default.tui(mockApi as never, undefined, {} as never),
		).resolves.toBeUndefined();

		expect(registered).toBeDefined();
		expect(registered?.slots).toBeTypeOf("object");
		expect(typeof registered?.slots?.sidebar_content).toBe("function");
	});

	it("tui subscribes to message.updated + session.next.step.started/ended", async () => {
		const mod = await import("./index.js");
		const subscribed: string[] = [];
		const mockApi = {
			event: {
				on: (type: string) => {
					subscribed.push(type);
					return () => {};
				},
			},
			slots: {
				register: () => "slot-1",
			},
			lifecycle: {
				signal: new AbortController().signal,
				onDispose: () => () => {},
			},
		};

		await expect(
			mod.default.tui(mockApi as never, undefined, {} as never),
		).resolves.toBeUndefined();

		expect(subscribed).toContain("message.updated");
		expect(subscribed).toContain("session.next.step.started");
		expect(subscribed).toContain("session.next.step.ended");
	});
});
