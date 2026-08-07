# Reference: SPEC Master Template (Annotated Guide)

> **Role:** Annotated reference explaining every section of a SPEC document.
> **Companion form:** `plans/SPEC_TEMPLATE.md` (blank fillable copy with identical structure).
> **Conformance:** `tests/unit/test_spec_template_structure.py` enforces that section headers + table column headers in the form are a subset of this guide.

---

## Decision Rule: 1-File vs 5-File Pattern

| Feature scope | Pattern | Files |
|---|---|---|
| <3 files changed, no architecture change | **1-file** | `plans/SPEC_<feature>.md` only (inline all sections) |
| >3 files OR architecture change | **5-file** | `SPEC_<feature>.md` (master + summaries) + `RTM_`, `ACM_`, `NFR_`, `DFD_` companions |

When 5-file: SPEC master contains a *summary* row/table per section + pointer `(\`plans/RTM_<feature>.md\`)` to the companion holding full detail.

---

## Annotated Section Outline

Below mirrors the exact structure of `plans/SPEC_TEMPLATE.md`. Every header + table column name matches the form. Annotations explain purpose and rules.

### ## 1. Executive Summary & Business Analysis

#### ### 1.1 Primary Goals & Non-Goals
- **Goals:** Primary objective of the feature.
- **Non-Goals:** Scope boundary — what is explicitly excluded. Critical for preventing scope creep.

#### ### 1.2 Requirement Traceability Matrix (RTM) (`plans/RTM_[FEATURE].md`)

Pointer to companion file (5-file) or inline table (1-file). See `rtm-template.md` for full schema.

Table column headers (ALL mandatory — verified by structural conformance test):

| Req ID | Business Requirement Description | Source | Priority | Target Component / File | Unit Test Reference | E2E QA Verification | Status |
|---|---|---|---|---|---|---|---|

- **Req ID** MUST be `R-<number>`. `ockit verify` checks for `| Req ID |` header.
- **Unit Test Reference** empty → WARN from verify. Must trace `tests/<file>::test_r<NNN>_<name>`.

#### ### 1.3 Domain Modeling & Ubiquitous Language Glossary
- Domain Entities with fields.
- Ubiquitous Language terms mapped 1:1 to implementation.
- User Journey: Actor → Action → System Response.

#### ### 1.4 User Stories & Behavioral Acceptance Criteria (BDD / Gherkin Matrix)
See `gherkin-bdd-template.md`. Each story: Happy Path + >=3 Fail Paths (Given-When-Then).

---

### ## 2. Architecture & Data Flow Diagram (DFD) (`plans/DFD_[FEATURE].md`)

Pointer to companion file (5-file) or inline Mermaid (1-file). See `dfd-template.md` for full schema (Context L0, Command Flow L1, Sequence, Trust Boundary table, Threat→Control trace).

---

### ## 3. Interface & Schema Specification (Zod & Pydantic)

#### ### API Endpoints

| Method | Path | Request Body | Response Schema | Status Codes |
|---|---|---|---|---|

Document every endpoint/CLI surface. Method = HTTP verb or `CLI`. Status Codes = all possible responses.

#### ### Zod / Pydantic Data Validation Schemas

TypeScript Zod + Python Pydantic schemas for every input/output payload. See SKILL.md §4 for examples.

---

### ## 4. Non-Functional Requirements (NFR) (`plans/NFR_[FEATURE].md`)

Pointer to companion file (5-file) or inline table (1-file). See `nfr-template.md` for full schema.

| Category | Target Metric / Floor Threshold | Verification Method |
|---|---|---|

Categories: Latency, Throughput, Error Rate, MTTR, Coverage, Security, Portability. Every NFR traces to RTM requirement.

---

### ## 5. File Mutation Manifest

| Action | File Path | Rationale & Responsibility |
|---|---|---|

- **Action:** `Create` / `Modify` / `Delete`.
- **Constraint:** Subagents MUST NOT create or modify files outside this manifest.

---

### ## 6. Test Plan & 12-Dimensional Edge Case Matrix (ACM) (`plans/ACM_[FEATURE].md`)

#### ### 6.1 Unit / Integration Tests (Given-When-Then)
Given-When-Then statements tracing to RTM requirements.

#### ### 6.2 12-Dimensional Business Edge Case Matrix (ACM)

Pointer to companion file (5-file) or inline table (1-file). See `acm-template.md` for full schema.

| Edge ID | Risk Dimension | Test Scenario | Expected Result & Code | Test ID |
|---|---|---|---|---|

- **Edge ID** MUST be `E-<number>`. `ockit verify` checks for `Edge Case` keyword in SPEC.
- Minimum 12 edges (1 per dimension). `ockit verify` distinguishes `E-<n>` rows from `R-<n>` rows.

---

### ## 7. Backward Compatibility & Security Audit

Checklist:
- [ ] OWASP-AI-01 Slopsquatting scanned (no hallucinated packages)
- [ ] OWASP-AI-02 IDOR authorization checks verified
- [ ] OWASP-AI-03 Input sanitization & parameterized queries enforced
- [ ] OWASP-AI-04 Hardcoded secrets scan clean
- [ ] OWASP-AI-05 Excessive agency & path sandboxing verified

---

### ## 8. Definition of Done & 3-State Verification

Checklist — the "3-State Verification" string is REQUIRED by `ockit verify`:
- [ ] All RTM requirements mapped 1:1 to passing unit/integration tests
- [ ] 12-Dimensional Edge Case Matrix 100% covered in test suite
- [ ] NFR validated against quality floors
- [ ] DFD trust boundaries verified
- [ ] 3-State Verification audit completed
- [ ] `ockit verify` passed cleanly

---

## Verify Contract (what `ockit verify` checks)

Before writing a SPEC, READ `references/verify-contract.md` to know the exact pass criteria. Key hard requirements:

1. RTM table must have header row containing `| Req ID |`
2. Document must contain the string `Edge Case`
3. Document must contain the string `3-State Verification`
4. RTM rows must start with `R-<number>`
5. ACM rows must start with `E-<number>`

Failure on any → `ockit verify` exits 1 → `/plan` gate fails.
