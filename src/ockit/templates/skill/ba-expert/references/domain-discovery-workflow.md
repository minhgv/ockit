# Reference: Domain Discovery Workflow

> Execute this 7-step procedure BEFORE writing any SPEC content. Output feeds §1.1 Goals/Non-Goals, §1.3 Ubiquitous Language, and the 1-file vs 5-file decision.

---

## Step 1: Codebase Survey

Identify what exists relevant to the feature:

- Grep for keywords from `$ARGUMENTS` / feature description.
- List files that will be touched (creates File Mutation Manifest §5 seed).
- Identify entry points (CLI commands, HTTP endpoints, UI components).
- Note existing patterns/conventions (naming, error handling, state management).

**Output:** Bullet list of files + 1-sentence role each.

---

## Step 2: Actor Identification

List every actor that interacts with the feature:

- **Primary actors:** Who triggers the feature? (User, CI, external system, agent)
- **Secondary actors:** Who/what responds? (Database, external API, message queue)
- **Adversarial actors:** Who might misuse? (Attacker, confused deputy, tenant cross-access)

**Output:** Actor table: `Actor | Type | Motivation | Access Level`.

---

## Step 3: Ubiquitous Language Extraction

Extract domain terms BEFORE writing specifications:

- List nouns from feature description + codebase survey.
- For each term, define: business meaning + rules + implementation entity.
- Map 1:1 to source code struct/class/interface.
- Flag ambiguous terms (same word, different meaning) — resolve with explicit definition.

**Output:** Ubiquitous Language Glossary table (SKILL.md §2.2 format).

---

## Step 4: Bounded Context Mapping

Identify domain boundaries:

- Which contexts does this feature touch? (Core domain, Auth, Billing, Notification, etc.)
- Are there cross-context integrations? (events, shared DB, API calls)
- Draw Bounded Context map (Mermaid `graph TD`).

**Output:** Mermaid diagram + 1 paragraph narrative per context boundary.

---

## Step 5: Non-Goals Definition (scope boundary)

Explicitly state what is OUT of scope:

- What adjacent problems will NOT be solved?
- What is deferred to a future iteration?
- What is intentionally not supported?

**Output:** Bulleted Non-Goals list (feeds SPEC §1.1).

---

## Step 6: Risk Assessment (pre-ACM)

Identify which of the 12 dimensions are most relevant:

- Concurrency? (shared mutable state?)
- Security? (auth, path, secret handling?)
- Precision? (currency, measurements?)
- Scale? (large inputs, many records?)

**Output:** Ranked list of top 3-5 risk dimensions. These get extra edge cases in ACM.

---

## Step 7: Decision — 1-File vs 5-File

Apply the decision rule from `spec-master-template.md`:

| Criterion | 1-File | 5-File |
|---|---|---|
| Files changed | <3 | >3 |
| Architecture change | No | Yes |
| Edge cases expected | <12 | >12 |
| NFRs measurable | Simple | Complex |

**Output:** Decision + 1-sentence justification. This determines artefact pipeline.

---

## Anti-Patterns (AVOID)

- **Skipping survey:** Writing SPEC without reading code → hallucinated file paths.
- **Vague terms:** "User", "System", "Data" without domain-specific definition.
- **Missing Non-Goals:** Everything in scope → scope creep.
- **Pre-mature 5-file:** Splitting into companion files for a 1-file feature → overhead.
