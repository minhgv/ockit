---
description: Run 5-stage SDLC pipeline (Plan -> TDD -> Gate -> QA -> Review)
---

# /pipeline Workflow

1. Execute /plan to generate SPEC, RTM Matrix & 12D Edge Case Matrix.
2. Execute /build for TDD RED-GREEN-REFACTOR.
3. Execute /gate for linter, secret scan, and security audit.
4. Execute /qa for E2E dogfooding tests.
5. Execute /review for 3-State Verification and Conventional Commits.
