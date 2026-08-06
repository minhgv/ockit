/**
 * ockit-quality-gate.js — OpenCode Native Quality Gate Plugin
 * Enforces Path Boundary Security, Path Traversal Prevention, and Secret Scans.
 */
const path = require('path');
const fs = require('fs');

const SENSITIVE_PATTERNS = ['.env', '.ssh', '.aws', '.gnupg', 'id_rsa', 'credentials'];

module.exports = {
  name: 'ockit-quality-gate',
  version: '1.0.0',
  hooks: {
    'before-tool-call': function (toolName, toolArgs) {
      if (toolArgs && toolArgs.file_path) {
        const filePath = toolArgs.file_path;
        for (const pattern of SENSITIVE_PATTERNS) {
          if (filePath.includes(pattern)) {
            throw new Error(`[ockit-quality-gate] Access denied: Sensitive file pattern '${pattern}' detected in path '${filePath}'`);
          }
        }
        if (filePath.includes('..') || filePath.startsWith('-')) {
          throw new Error(`[ockit-quality-gate] Access denied: Directory traversal or unsafe flag detected in '${filePath}'`);
        }
      }
    }
  }
};
