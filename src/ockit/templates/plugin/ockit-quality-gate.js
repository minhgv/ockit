/**
 * ockit-quality-gate.js — OpenCode Native Quality Gate Plugin
 * Enforces Path Boundary Security, Path Traversal Prevention, and Secret Scans.
 *
 * Merges agy-kit's bin/check-path-boundaries.sh logic (path allow/deny lists,
 * dotfile-escape, symlink-escape detection, control-character rejection) into
 * the native OpenCode tool.execute.before hook (R-018).
 *
 * Source reference: https://github.com/giapminh79/agy-kit/tree/main/bin/check-path-boundaries.sh
 */
import { lstatSync, readlinkSync } from "node:fs";

const SENSITIVE_PATTERNS = [
	".env",
	".ssh",
	".aws",
	".gnupg",
	"id_rsa",
	"credentials",
];

// Deny-list ported from check-path-boundaries.sh FORBIDDEN_PATTERNS:
// ^\.env$ | ^\.ssh/ | ^/etc/ | ^\.git/
const FORBIDDEN_PATH_REGEX = /^(\.env$|\.ssh\/|\/etc\/|\.git\/)/;

// Control characters rejected in paths (check-path-boundaries.sh newline check).
const CONTROL_CHARS = /[\x00-\x1f\x7f]/;

export const OckitQualityGate = async () => {
	return {
		"tool.execute.before": async (input, output) => {
			const args = output.args ?? {};
			const filePath = args.filePath ?? args.file_path ?? args.path;
			if (typeof filePath !== "string") {
				return;
			}

			// 1. Control-character rejection (newlines / NUL / CR).
			if (CONTROL_CHARS.test(filePath)) {
				throw new Error(
					`[ockit-quality-gate] Access denied: Control characters detected in path '${JSON.stringify(
						filePath,
					)}'. Refusing to run tool '${input.tool}'.`,
				);
			}

			// 2. Directory traversal + unsafe leading flag.
			if (filePath.includes("..") || filePath.startsWith("-")) {
				throw new Error(
					`[ockit-quality-gate] Access denied: Directory traversal or unsafe flag detected in '${filePath}'. Use an absolute path inside the project.`,
				);
			}

			// 3. Sensitive file patterns (secrets, keys, credentials).
			for (const pattern of SENSITIVE_PATTERNS) {
				if (filePath.includes(pattern)) {
					throw new Error(
						`[ockit-quality-gate] Access denied: Sensitive file pattern '${pattern}' detected in path '${filePath}'. Refusing to run tool '${input.tool}'.`,
					);
				}
			}

			// 4. Forbidden path deny-list (dotfile-escape, absolute system paths).
			if (FORBIDDEN_PATH_REGEX.test(filePath)) {
				throw new Error(
					`[ockit-quality-gate] Access denied: Path on forbidden deny-list '${filePath}'. Refusing to run tool '${input.tool}'.`,
				);
			}

			// 5. Symlink-escape detection: a symlink whose target escapes the
			//    workspace (absolute target or containing "..") is refused.
			try {
				const stats = lstatSync(filePath);
				if (stats.isSymbolicLink()) {
					const target = readlinkSync(filePath);
					if (target.startsWith("/") || target.includes("..")) {
						throw new Error(
							`[ockit-quality-gate] Access denied: Symlink escape detected on '${filePath}' -> '${target}'. Refusing to run tool '${input.tool}'.`,
						);
					}
				}
			} catch (err) {
				if (err instanceof Error && err.message.includes("Symlink escape")) {
					throw err;
				}
				// ENOENT / EACCES etc.: path does not exist yet (create/edit) or
				// is unreadable — not a boundary violation by itself.
			}
		},
	};
};
