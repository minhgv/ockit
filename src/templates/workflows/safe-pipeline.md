---
description: Run pipeline in an isolated Git Worktree with auto-rollback
---

# /safe-pipeline Workflow

1. Create isolated git worktree via `worktree.py`.
2. Run full 5-stage pipeline.
3. Pre-check patch apply cleanly before merging to primary branch.
4. Auto-rollback worktree on failure.
