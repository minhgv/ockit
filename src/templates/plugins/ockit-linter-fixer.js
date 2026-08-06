/**
 * ockit-linter-fixer.js — OpenCode Native Linter & Shebang Fixer Plugin
 * Fixes shebang executable permissions and formats python annotations.
 */
const fs = require('fs');

module.exports = {
  name: 'ockit-linter-fixer',
  version: '1.0.0',
  fixPermissions: function (filePath) {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf-8');
      if (content.startsWith('#!')) {
        fs.chmodSync(filePath, 0o755);
        return true;
      }
    }
    return false;
  }
};
