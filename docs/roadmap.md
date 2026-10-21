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

### Stage sequencing and completion

Work proceeds in roadmap order. Only one stage is active at a time; a
standalone utility or test for a later stage is preparatory work, not a reason
to mark that stage complete or advance the active stage.

A stage is complete only when its acceptance criteria below are demonstrated
in the intended application workflow, with relevant tests and documentation.
If a baseline exists without that integration, record it as a baseline and
keep the stage incomplete. Do not start implementation of the next stage
before the active stage is complete unless the user explicitly changes scope.

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

**Status: Complete at current scope**

Goal:

Identify when incoming articles are duplicates or near-duplicates of previously stored material.

The deterministic classifier (`classify_duplicate`) actively governs insertion behavior during ingestion (`EXACT_DUPLICATE` is rejected explicitly prior to insertion, while `NEAR_DUPLICATE` and `DISTINCT` preserve original article records without merging, deletion, or overwriting; database-level `(source_id, url)` unique constraint provides secondary safety).

Existing signals, integration status, and behavior are documented in
[`pipeline.md`](pipeline.md); test coverage/results are recorded in
[`testing.md`](testing.md).

### Acceptance criteria

* Positive and negative duplicate scenarios have explicit test cases.
* Ingestion uses the classifier (`classify_duplicate`) to explicitly govern insertion behavior (`EXACT_DUPLICATE` skips explicitly prior to insertion, `NEAR_DUPLICATE` and `DISTINCT` preserve original article records without merging, deletion, or overwriting).
* Existing `(source_id, url)` behavior and article data are preserved.
* Implementation behavior and limitations are documented in
  [`pipeline.md`](pipeline.md), and observed results are recorded in
  [`testing.md`](testing.md).

---

### Stage 3 — Story Matching

**Status: Complete at current scope**

The deterministic matcher (`match_story`) is integrated into article insertion
through `process_article_story_matching`. `MATCH` links the article to an
existing story; `NEW_STORY` creates and links one active story; `REVIEW`
preserves the article without creating a story association. These outcomes are
covered by the database-backed integration test in
[`../tests/integration_test_story_matching.py`](../tests/integration_test_story_matching.py).

Existing signals, integration status, and behavior are documented in
[`pipeline.md`](pipeline.md); test coverage/results are recorded in
[`testing.md`](testing.md).

### Acceptance criteria

* The matcher runs after successful article insertion against active candidate
  stories.
* `MATCH` associates the article with the selected existing story using the
  current `article_stories` model.
* `NEW_STORY` creates one active story and one article-story relationship.
* `REVIEW` leaves the association undecided rather than forcing a match.
* Integration tests cover all outcomes and their persisted relationships,
  including no new story or relationship for `REVIEW`.
* Implementation behavior and limitations are documented in
  [`pipeline.md`](pipeline.md), and observed results are recorded in
  [`testing.md`](testing.md).

---

### Stage 4 — Claim and Evidence Pipeline

**Status: Baseline implemented; incomplete and not active**

The standalone provenance-trace utility and its focused test outcome are
documented in [`pipeline.md`](pipeline.md) and [`testing.md`](testing.md).
It operates only on relationships supplied to it; this preparatory utility
does not complete the stage or change the active priority.

### Completion criteria

* Claims are connected to their stories and reporting articles using the
  existing relationship model.
* Evidence is connected to claims with explicit supporting, contradicting,
  contextual, or other applicable relationships.
* Evidence provenance distinguishes its producer or issuer from publishers
  and other roles; provenance is not inferred merely from an article mention.
* The connected records can be traced from claim through evidence to
  provenance, with tests covering relationships and missing or conflicting
  information.
* Evidence relationships do not silently determine or overwrite an
  assessment.
* The behavior and limitations are documented in [`pipeline.md`](pipeline.md),
  and observed results in [`testing.md`](testing.md).

---

### Stage 5 — Assessment Workflow

**Status: Baseline implemented; incomplete and not active**

The standalone in-memory assessment constructor and its focused test result
are documented in [`pipeline.md`](pipeline.md) and [`testing.md`](testing.md).
This preparatory utility does not persist records or complete the workflow.

### Completion criteria

* Assessments are persisted as new historical records in
  `claim_assessments`; previous assessments are never silently overwritten.
* The current `claims.status` is updated only through the documented workflow
  and remains distinct from the historical assessment records.
* Proposal, review, and decision roles have an explicit, tested workflow that
  preserves actor type, actor name, status, reasoning, and creation time.
* Tests verify persistence, append-only history, and the distinction between
  AI proposals and human decisions.
* The behavior and limitations are documented in [`pipeline.md`](pipeline.md),
  and observed results in [`testing.md`](testing.md).

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
