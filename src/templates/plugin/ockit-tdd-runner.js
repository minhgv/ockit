/**
 * ockit-tdd-runner.js — OpenCode Native TDD Execution Plugin
 * Routes multi-language TDD test runners (Python, TS, Go, Rust, PHP).
 */
const { execSync } = require('child_process');

module.exports = {
  name: 'ockit-tdd-runner',
  version: '1.0.0',
  runTdd: function (lang) {
    switch (lang) {
      case 'python':
        return execSync('pytest', { encoding: 'utf-8' });
      case 'typescript':
      case 'javascript':
        return execSync('npx vitest run', { encoding: 'utf-8' });
      case 'go':
        return execSync('go test ./...', { encoding: 'utf-8' });
      case 'rust':
        return execSync('cargo test', { encoding: 'utf-8' });
      case 'php':
        return execSync('vendor/bin/phpunit', { encoding: 'utf-8' });
      default:
        throw new Error(`Unsupported language for ockit-tdd-runner: ${lang}`);
    }
  }
};
