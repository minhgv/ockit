/**
 * ockit-linter-fixer.js — OpenCode Native Linter & Shebang Fixer Plugin
 * After a file is edited or written, makes it executable when it starts
 * with a shebang (#!) line.
 */
import fs from "node:fs";

export const OckitLinterFixer = async () => {
	return {
		"tool.execute.after": async (input) => {
			if (input.tool !== "edit" && input.tool !== "write") {
				return;
			}
			const args = input.args ?? {};
			const filePath = args.filePath ?? args.file_path ?? args.path;
			if (typeof filePath !== "string" || !fs.existsSync(filePath)) {
				return;
			}
			const content = fs.readFileSync(filePath, "utf-8");
			if (content.startsWith("#!")) {
				fs.chmodSync(filePath, 0o755);
			}
		},
	};
};
