# Project Roadmap

This is the authoritative source for current project state, stage status,
priority, and acceptance criteria. Pipeline behavior belongs in
[`pipeline.md`](pipeline.md), schema details in
[`database-schema.md`](database-schema.md), and test commands/results in
[`testing.md`](testing.md). Do not copy those details here.

## 1. Current Project State

The project is still in development and is not a production news-processing
system. The active stage is the single stage marked **In progress** below.
Verified test state is maintained in [`testing.md`](testing.md).

---

## 2. Completed

The database model and reproducible SQL foundation, provenance validation,
synthetic test data, and baseline RSS ingestion are established. Their
authoritative details are maintained in
[`database-schema.md`](database-schema.md), [`pipeline.md`](pipeline.md),
[`decisions.md`](decisions.md), and [`testing.md`](testing.md).

---

## 3. Delivery Stages

### Stage 1 — Baseline Ingestion

**Status: Complete at current scope**

Its behavior and limitations are defined in [`pipeline.md`](pipeline.md);
test procedures and observed outcomes are in [`testing.md`](testing.md).
Reopen this stage only for a demonstrated requirement, not as a prerequisite
to the active stage.

---

### Stage 2 — Deduplication

**Status: In progress**

Goal:

Identify when incoming articles are duplicates or near-duplicates of previously stored material.

The current `(source_id, url)` uniqueness constraint remains the baseline
duplicate-insertion safeguard.

Existing signals, integration status, and behavior are documented in
[`pipeline.md`](pipeline.md); test coverage/results are recorded in
[`testing.md`](testing.md).

### Next task

Define and implement the first deterministic duplicate-classification
behavior using the existing normalization utilities. Keep this task separate
from story matching, and do not merge or discard article records as a side
effect.

Before changing implementation, specify through tests which URL variants are
treated as equivalent, which title/content matches remain distinct, and how
source boundaries affect a match. Preserve original article data and current
`(source_id, url)` insertion behavior unless a demonstrated requirement and
documented decision justify changing them.

### Acceptance criteria

* Positive and negative duplicate scenarios have explicit test cases.
* Normalized title or URL equality does not silently delete or overwrite
  article records.
* Ingestion uses the comparison only after its duplicate semantics are
  explicit.
* Implementation behavior and limitations are documented in
  [`pipeline.md`](pipeline.md), and observed results are recorded in
  [`testing.md`](testing.md).

---

### Stage 3 — Story Matching

**Status: Complete at current scope**

The deterministic baseline and its three outcomes are documented in
[`pipeline.md`](pipeline.md). The exit criterion is met by reproducible
matching, non-matching, and uncertain cases; the focused test result is
recorded in [`testing.md`](testing.md).

The matcher is a standalone utility: it does not create or persist stories or
run as part of article ingestion. This limitation does not prevent completion
of the current baseline scope. Any later integration should be specified as a
separate task without changing this completed status retroactively.

---

### Stage 4 — Claim and Evidence Pipeline

**Status: Complete at current scope**

The current trace behavior, roles, and limits are documented in
[`pipeline.md`](pipeline.md); the focused test outcome is recorded in
[`testing.md`](testing.md). Supporting, contradicting, and contextual
relationships retain their provenance roles in the trace.

This scope provides a standalone trace over already-linked input records. It
does not create or persist claim/evidence relationships or discover
provenance; those remain separate integration work if required.

---

### Stage 5 — Assessment Workflow

**Status: Standalone baseline implemented; persistence/integration pending**

The standalone assessment constructor and its limits are documented in
[`pipeline.md`](pipeline.md); its focused test result is in
[`testing.md`](testing.md). It creates an in-memory assessment record and
appends it to the supplied history without mutating the prior entries.

This does not persist records to `claim_assessments` or implement a connected
proposal/review/decision workflow. Those integration steps remain outstanding
before the assessment workflow can be considered complete.

---

### Stage 6 — AI-Assisted Processing

**Status: Not started**

AI should be introduced only after deterministic baselines exist.

Potential uses:

* claim extraction;
* article/story matching;
* evidence identification;
* summarization;
* classification;
* assessment proposals.

AI output must remain distinguishable from verified source material.

AI must not become the source of truth merely because it produces a confident-looking answer.

Exit criteria:

AI-assisted processing can be compared with deterministic and/or human-reviewed results.

---

### Stage 7 — Automation

**Status: Not started**

Goal:

Connect the pipeline into a repeatable processing system.

Potential flow:

```text
Feeds
  ↓
Ingestion
  ↓
Deduplication
  ↓
Story Matching
  ↓
Claim Extraction
  ↓
Evidence Identification
  ↓
Provenance
  ↓
Assessment
  ↓
Stored Intelligence
```

Automation should be introduced gradually rather than building the entire pipeline as one opaque process.

---

### Stage 8 — User Interface

**Status: Not started**

A UI will be developed only after the underlying data and processing model are sufficiently stable.

The UI should expose the evidence trail rather than hide it.

Potential views include:

* stories;
* articles;
* claims;
* evidence;
* provenance;
* conflicting evidence;
* assessment history;
* source information.

The UI should not imply certainty that the underlying data does not support.

---
