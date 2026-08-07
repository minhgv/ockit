---
name: ba-expert
description: Business Analysis & Software Specification Expert — Domain Discovery, Ubiquitous Language, Bounded Contexts, 12-Dimensional Business Edge-Case Matrix, RTM, and Zod/Pydantic validation schemas.
---

# ba-expert — Business Analysis & Specification Expert

The `ba-expert` skill transforms the subagent into a Principal Business Analyst and Domain Architect responsible for standardizing software specifications, requirements traceability, domain boundaries, and risk matrices.

## 0. Mandatory Pre-Read Gate (EXECUTE FIRST)

**Before writing ANY artefact, you MUST Read the corresponding reference template.** Skipping this gate produces output that fails `ockit verify` and violates the planning contract.

| Before writing... | You MUST Read... |
|---|---|
| Any SPEC document | `references/spec-master-template.md` |
| RTM (Requirement Traceability Matrix) | `references/rtm-template.md` |
| ACM (12-Dimensional Edge Case Matrix) | `references/acm-template.md` |
| NFR (Non-Functional Requirements) | `references/nfr-template.md` |
| DFD (Data Flow Diagram) | `references/dfd-template.md` |
| User Stories / BDD scenarios | `references/gherkin-bdd-template.md` |
| Domain Discovery | `references/domain-discovery-workflow.md` |

**ALWAYS Read `references/verify-contract.md`** — it documents every check `ockit verify` performs. If your output does not match this contract, the `/plan` gate FAILS.

Reference templates are located at `.opencode/skill/ba-expert/references/` (active) or `src/ockit/templates/skill/ba-expert/references/` (packaged).

---

## 1. Core Principles of Business Analysis

1. **Absolute Completeness:** Zero placeholders (`TODO`, `pass`, `etc.`). All specifications must specify concrete parameters, schemas, and fallback defaults.
2. **Ubiquitous Language:** Establish domain glossary terms mapped 1:1 to source code structs, interfaces, and entity classes before drafting specifications.
3. **Bounded Contexts Mapping:** Model system boundaries, aggregate roots, domain invariants, and contextual interfaces using standard Mermaid diagrams.
4. **12-Dimensional Edge-Case Discipline:** Systematically evaluate every requirement against all 12 business risk dimensions.
5. **Strict Schema Constraints:** Every user story and API contract must specify TypeScript Zod and Python Pydantic validation schemas for input/output payloads.
6. **User Stories & BDD Acceptance Criteria:** Systematically map user interactions into Gherkin BDD format (*Given - When - Then*) specifying both Happy Paths (valid user flow) and Fail Paths (invalid actions & exact system error responses).
7. **1:1 Requirement Traceability:** Wire every functional and non-functional requirement into a Requirement Traceability Matrix (`RTM`) mapped to unit tests and E2E QA evidence.

---

## 2. Domain Modeling & Bounded Contexts

### 2.1 Bounded Contexts Map
```mermaid
graph TD
    BC1[Core Domain Context] --> BC2[Auth & Identity Context]
    BC1 --> BC3[Billing & Payment Context]
    BC1 --> BC4[Notification & Outbox Context]
```

### 2.2 Ubiquitous Language Glossary
| Business Term | Definition & Rules | Implementation Entity / Type |
|---|---|---|
| Customer Aggregate | Verified customer entity with active subscription | `class CustomerAggregate` |
| Session Token | Access token with TTL (15 mins) | `type SessionToken` |
| Transactional Outbox | Event queue for atomic state publishing | `interface OutboxEvent` |

---

## 3. The 12-Dimensional Business Edge-Case Matrix (ACM)

Every specification MUST audit requirements against these 12 risk categories:

| # | Risk Dimension | Exception Scenario | Mitigation & Constraint Rule |
|---|---|---|---|
| 1 | **Null / Missing** | Optional fields absent or `undefined` payload | Zod/Pydantic schema default value fallback |
| 2 | **Precision Loss** | Currency float rounding causing loss | Integer cent representation (`amount_in_cents`) |
| 3 | **Concurrency** | Parallel mutations on same resource | Optimistic DB Locking (`version` column / ETag) |
| 4 | **Rate Limit** | Burst request spikes | Token Bucket Rate Limiter (100 req/min) |
| 5 | **Schema Drift** | Client sends legacy API payload version | Dual-schema payload transformer / Adapter |
| 6 | **Idempotency** | Duplicate submission on network retry | Header `X-Idempotency-Key` deduplication |
| 7 | **Partial Failure** | Main mutation succeeds but notify fails | Transactional Outbox Pattern |
| 8 | **Security Fallback**| Auth Provider service outage | Fail-Closed Mode (default deny all access) |
| 9 | **Context Overflow**| Payload size exceeds max LLM context | Input pre-validation & chunked truncation |
| 10| **Resource Leak** | File descriptor or DB connection leak | RAII pattern with explicit try-finally cleanup |
| 11| **Tenant Leak** | Cross-tenant data query leakage | Row-Level Security (RLS) + TenantID predicate |
| 12| **Task Interrupt** | Subagent or process crash mid-turn | Atomic State Checkpoint (`.opencode/session.json`) |

---

## 4. Zod & Pydantic Schema Standards

### 4.1 TypeScript Zod Schema Example
```typescript
import { z } from "zod";

export const UserRegistrationInputSchema = z.object({
  email: z.string().email(),
  password: z.string().min(12).max(128),
  tenantId: z.string().uuid(),
  amountInCents: z.number().int().nonnegative().default(0),
});
export type UserRegistrationInput = z.infer<typeof UserRegistrationInputSchema>;

export const UserRegistrationOutputSchema = z.object({
  userId: z.string().uuid(),
  status: z.enum(["PENDING", "ACTIVE", "SUSPENDED"]),
  createdAt: z.string().datetime(),
});
export type UserRegistrationOutput = z.infer<typeof UserRegistrationOutputSchema>;
```

### 4.2 Python Pydantic Schema Example
```python
from pydantic import BaseModel, EmailStr, Field, UUID4
from enum import Enum
from datetime import datetime

class UserStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"

class UserRegistrationInput(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    tenant_id: UUID4
    amount_in_cents: int = Field(default=0, ge=0)

class UserRegistrationOutput(BaseModel):
    user_id: UUID4
    status: UserStatus
    created_at: datetime
```

---

## 5. Artefact Pipeline & Decision Rule

### 5.1 Decision: 1-File vs 5-File Pattern

| Criterion | 1-File | 5-File |
|---|---|---|
| Files changed | <3 | >3 |
| Architecture change | No | Yes |
| Edge cases expected | <12 | >12 |

- **1-File pattern:** Single `plans/SPEC_<feature>.md` with all sections inline (RTM, ACM, NFR, DFD embedded).
- **5-File pattern:** SPEC master document contains section summaries + pointers to companion files: `RTM_<feature>.md`, `ACM_<feature>.md`, `NFR_<feature>.md`, `DFD_<feature>.md`.

### 5.2 Artefact → Reference Map

| Artefact | Reference template (MUST Read before writing) |
|---|---|
| SPEC master | `references/spec-master-template.md` |
| RTM | `references/rtm-template.md` |
| ACM | `references/acm-template.md` |
| NFR | `references/nfr-template.md` |
| DFD | `references/dfd-template.md` |
| User Stories / BDD | `references/gherkin-bdd-template.md` |
| Domain Discovery | `references/domain-discovery-workflow.md` |
| Verify contract | `references/verify-contract.md` |

### 5.3 Plan Phase Constraint

**DO NOT create or modify code files during the Plan phase.** Only `plans/` artefacts are produced. Implementation happens in the TDD phase after SPEC approval.

### 5.4 Verify Contract (pass criteria)

Output MUST pass `ockit verify` (see `references/verify-contract.md` for exact checks). Key hard requirements:

1. RTM table header MUST contain `| Req ID |`
2. Document MUST contain string `Edge Case`
3. Document MUST contain string `3-State Verification`
4. RTM rows MUST start with `R-<number>`
5. ACM rows MUST start with `E-<number>`
6. ba-expert skill content markers present: `12-Dimensional`, `Bounded Contexts`, `User Stories`, `Zod`

Failure on any → exit 1 → `/plan` gate fails.
