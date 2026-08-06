/**
 * ockit-ba-traceability.js — OpenCode Native BA Traceability & RTM Plugin
 * Ensures RTM Traceability Matrix and 12D Edge Case Matrix are verified.
 */
module.exports = {
  name: 'ockit-ba-traceability',
  version: '1.0.0',
  hooks: {
    'before-plan-commit': function (specDoc) {
      if (!specDoc || !specDoc.includes('RTM') || !specDoc.includes('Edge Case')) {
        console.warn('[ockit-ba-traceability] Warning: Specification document is missing explicit RTM or Edge Case Matrix section.');
      }
    }
  }
};
