# Reference: Gherkin BDD User Story Matrix Template

> SPEC §1.4 MUST contain User Stories with Happy Path + Fail Path scenarios in Given-When-Then format.

---

## User Story Skeleton

```markdown
#### Story US-<NN>: <Feature User Story Title>
- **As a** `<Role / User Type>`
- **I want to** `<Perform Action / Feature Goal>`
- **So that** `<Achieve Business Value / Outcome>`
```

---

## Happy Path Scenario (Success Flow)

Every story MUST have exactly 1 Happy Path:

```markdown
##### Happy Path Scenario (Success Flow)
- **Given** `<Pre-condition, e.g. Valid session & correct input payload>`
- **When** `<User performs action, e.g. Submits valid form>`
- **Then** `<System responds with success: HTTP 201 / exit 0 / state change>`
```

---

## Fail Path Scenarios (Invalid Actions & Error Responses)

Every story MUST have at least 3 Fail Paths covering the most common failure archetypes:

### Fail Path Archetype 1: Missing / Invalid Input

```markdown
- **Scenario FP-01 (Missing Field)**: **Given** `<Missing required field in request>` **When** `<User submits form>` **Then** `<System responds with HTTP 400 Bad Request & error message '<exact message>'`
```

### Fail Path Archetype 2: Unauthorized / Forbidden

```markdown
- **Scenario FP-02 (Unauthorized Action)**: **Given** `<Expired or invalid auth token>` **When** `<User calls endpoint>` **Then** `<System responds with HTTP 401 Unauthorized & error message '<exact message>'`
```

### Fail Path Archetype 3: Conflict / Duplicate / State Violation

```markdown
- **Scenario FP-03 (Duplicate Resource)**: **Given** `<Resource already exists in database>` **When** `<User submits creation>` **Then** `<System responds with HTTP 409 Conflict & error message '<exact message>'`
```

### Optional Fail Path Archetypes (add as relevant)

```markdown
- **Scenario FP-04 (Rate Limited)**: **Given** `<Burst requests exceed limit>` **When** `<User calls endpoint N+1 times>` **Then** `<System responds with HTTP 429 Too Many Requests>`
- **Scenario FP-05 (Idempotency Replay)**: **Given** `<Duplicate X-Idempotency-Key>` **When** `<User retries request>` **Then** `<System returns cached original response, no duplicate mutation>`
- **Scenario FP-06 (Partial Failure)**: **Given** `<Primary mutation succeeds but side-effect fails>` **When** `<Outbox retries side-effect>` **Then** `<System eventually consistent; no data loss>`
```

---

## Full Story Example

```markdown
#### Story US-01: User Registration
- **As a** `Unauthenticated User`
- **I want to** `register an account with email and password`
- **So that** `I can authenticate and access protected resources`

##### Happy Path Scenario (Success Flow)
- **Given** `Valid email and strong password (>= 12 chars)`
- **When** `User submits POST /api/v1/auth/register`
- **Then** `System responds with HTTP 201 Created & returns {user_id, token}`

##### Fail Path Scenarios
- **Scenario FP-01 (Missing Field)**: **Given** `Missing password field` **When** `User submits form` **Then** `HTTP 400 & error 'Password is required'`
- **Scenario FP-02 (Unauthorized Action)**: **Given** `Expired session token` **When** `User calls protected endpoint` **Then** `HTTP 401 & error 'Invalid session'`
- **Scenario FP-03 (Duplicate Resource)**: **Given** `Email already registered` **When** `User submits registration` **Then** `HTTP 409 & error 'Email already exists'`
```

---

## Verify Contract Notes

- `ockit verify` does NOT directly check Gherkin syntax, but User Stories feed RTM requirements (each US maps to R-<NNN>).
- Each Fail Path should trace to an ACM edge case (E-<NNN>).
- Error messages in `Then` clauses should be EXACT (quoted) — they become test assertions.
