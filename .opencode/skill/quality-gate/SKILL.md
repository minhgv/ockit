# Quality Gate Skill — Lint, Typecheck, Security Audit

## Trigger
- Before committing or merging new code.

## Procedure

### 1. Lint & Type Check
- **JavaScript/TypeScript:** `npm run lint && npx tsc --noEmit`
- **Python:** `ruff check . && mypy .`
- **PHP:** `./vendor/bin/pint --test && ./vendor/bin/phpstan analyse`
- **Fix:** Auto-fix all warnings/errors. Zero tolerance.

### 2. Secret Leak Scan
```bash
# Check for hardcoded secrets in git diff
git diff --cached | grep -iE "(api_key|password|secret|token|private_key)" || echo "CLEAN"
```
- If detected → remove, move to env var, patch immediately.

### 3. OWASP Security Audit
- **SQL Injection:** Search for query string concatenation, raw SQL.
- **XSS:** Search for `innerHTML`, unescaped output, `dangerouslySetInnerHTML`.
- **CSRF:** Verify token middleware on POST/PUT/DELETE.
- **Access Control:** Check authorization on every endpoint.

### 4. Test Coverage
- Run coverage report: `npm run test:coverage` / `pytest --cov`.
- Threshold: ≥80% for new code.

## Verification
- Lint: 0 error, 0 warning.
- Security: 0 hardcode secret, 0 OWASP vulnerability.
- Coverage: ≥80%.
