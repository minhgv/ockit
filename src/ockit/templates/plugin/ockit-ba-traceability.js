/**
 * ockit-ba-traceability.js — OpenCode Native BA Traceability & RTM Plugin
 * Ensures RTM Traceability Matrix and 12D Edge Case Matrix are verified
 * in specification documents after they are written or edited.
 */
import fs from "node:fs";

const SPEC_FILE_PATTERNS = [
	/(^|[\\/._-])spec([\\/._-]|$)/i,
	/(^|[\\/._-])prd([\\/._-]|$)/i,
	/(^|[\\/._-])solution([\\/._-]|$)/i,
	/(^|[\\/._-])requirement([\\/._-]|$)/i,
	/(^|[\\/._-])rtm([\\/._-]|$)/i,
	/(^|[\\/._-])edge[-_ ]?case([\\/._-]|$)/i,
	/(^|[\\/._-])tlgp([\\/._-]|$)/i,
	/(^|[\\/._-])tài[ -]?liệu[ -]?giải[ -]?pháp/i,
];

function isSpecDoc(filePath) {
	return SPEC_FILE_PATTERNS.some((pattern) => pattern.test(filePath));
}

export const OckitBaTraceability = async ({ client }) => {
	return {
		"tool.execute.after": async (input) => {
			if (input.tool !== "edit" && input.tool !== "write") {
				return;
			}
			const args = input.args ?? {};
			const filePath = args.filePath ?? args.file_path ?? args.path;
			if (typeof filePath !== "string" || !isSpecDoc(filePath)) {
				return;
			}
			let content;
			try {
				content = fs.readFileSync(filePath, "utf-8");
			} catch {
				return;
			}
			if (!content.includes("RTM") || !content.includes("Edge Case")) {
				await client.app.log({
					body: {
						service: "ockit-ba-traceability",
						level: "warn",
						message:
							"Specification document is missing explicit RTM or Edge Case Matrix section",
						extra: { filePath },
					},
				});
			}
		},
	};
};
