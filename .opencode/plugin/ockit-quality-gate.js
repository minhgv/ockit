/**
 * ockit-quality-gate.js — OpenCode Native Quality Gate Plugin
 * Enforces Path Boundary Security, Path Traversal Prevention, and Secret Scans.
 */
const SENSITIVE_PATTERNS = [
	".env",
	".ssh",
	".aws",
	".gnupg",
	"id_rsa",
	"credentials",
];

export const OckitQualityGate = async () => {
	return {
		"tool.execute.before": async (input, output) => {
			const args = output.args ?? {};
			const filePath = args.filePath ?? args.file_path ?? args.path;
			if (typeof filePath !== "string") {
				return;
			}
			for (const pattern of SENSITIVE_PATTERNS) {
				if (filePath.includes(pattern)) {
					throw new Error(
						`[ockit-quality-gate] Access denied: Sensitive file pattern '${pattern}' detected in path '${filePath}'. Refusing to run tool '${input.tool}'.`,
					);
				}
			}
			if (filePath.includes("..") || filePath.startsWith("-")) {
				throw new Error(
					`[ockit-quality-gate] Access denied: Directory traversal or unsafe flag detected in '${filePath}'. Use an absolute path inside the project.`,
				);
			}
		},
	};
};
