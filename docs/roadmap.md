# Project Roadmap

## 1. Current Project State

The project has completed its initial architecture, data-model validation, database canonicalization, and reproducibility/provenance testing phases.

The PostgreSQL model has been created and manually tested against:

* real-world news and research material,
* provenance relationships,
* claim/evidence relationships,
* conflicting evidence,
* shared underlying sources,
* independent evidence,
* historical assessments,
* and analytical database views.

The repository now contains the canonical SQL representation of the validated database structure, reproducible synthetic test data, and documentation intended to preserve the project's architecture, decisions, testing history, and operating principles.

The system is **not yet a production news-processing system**.

---

## 2. Completed

### Database Model

Completed and tested:

* `sources`
* `source_policies`
* `source_feeds`
* `articles`
* `stories`
* `article_stories`
* `claims`
* `claim_sources`
* `evidence`
* `claim_evidence`
* `evidence_sources`
* `claim_assessments`
* `article_evidence`

The model supports:

* source classification,
* article provenance,
* story grouping,
* claim extraction,
* evidence tracking,
* evidence provenance,
* article-to-evidence relationships,
* claim-to-evidence relationships,
* historical assessments.

### Validation

Completed:

* real LUX-ZEPLIN dark-matter example,
* Reuters article validation,
* Imperial College article validation,
* research-paper evidence,
* provenance tracking,
* synthetic conflicting-evidence test,
* synthetic shared-primary-source test,
* synthetic independent-evidence test,
* historical assessment test.

### Database Views

Created and tested:

* `claim_intelligence`
* `claim_overview`
* `claim_evidence_conflicts`

### Database Canonicalization

Completed:

* actual tested PostgreSQL schema extracted into `database/schema.sql`,
* actual tested PostgreSQL views extracted into `database/views.sql`,
* schema reconstruction tested in a separate `news_test` database,
* all 13 expected tables recreated successfully,
* all 3 expected views recreated successfully,
* empty-database queries against the views completed without errors.

The repository SQL files are derived from the validated PostgreSQL database rather than manually reconstructed.

### Reproducible Test Data

Completed:

* synthetic test data added under `database/seeds/test_data.sql`,
* article/story relationships tested,
* claim/article relationships tested,
* claim/evidence relationships tested,
* supporting and contradicting evidence tested,
* evidence provenance tested,
* multiple articles referring to the same evidence tested,
* historical assessment changes tested.

The synthetic data is explicitly identified as synthetic and must not be treated as production or real-world evidence.

The tests demonstrated that:

* article count must not be treated as evidence count,
* repeated reporting does not automatically establish independent confirmation,
* provenance counts are descriptive and not independence or trust scores,
* historical assessments can be preserved without overwriting earlier assessments.

### Repository Foundation

Created:

* Git repository,
* project structure,
* `.gitignore`,
* `README.md`,
* `AGENTS.md`,
* architecture documentation,
* pipeline documentation,
* database documentation,
* testing documentation,
* architectural decisions documentation,
* roadmap documentation.

### Current Repository Milestone

The latest inspected commit is:

```text
f5a27cd Add deterministic URL normalization
```

Since the baseline ingestion milestone, the repository has added deterministic
title and URL normalization utilities and integration tests for duplicate
article behavior. The `main` branch was synchronized with `origin/main` before
this roadmap update. The current roadmap changes are local and uncommitted.

---

## 3. Current Work

The current implementation stage is:

**Deduplication**

Baseline Ingestion is implemented and remains the foundation for this work.
The current deduplication work adds deterministic normalization utilities and
tests while preserving the existing `(source_id, url)` insertion safeguard.

The ingestion foundation provides:

* RSS parsing;
* article normalization;
* required-field validation;
* article insertion;
* duplicate prevention through `(source_id, url)`;
* controlled local RSS fixtures;
* unit tests;
* integration tests;
* transaction-safe test execution.

The deduplication work currently provides:

* deterministic title normalization;
* deterministic URL normalization;
* tests for duplicate article behavior.

These utilities are not yet connected to ingestion or duplicate
classification. Normalized values are comparison signals, not proof that two
articles are duplicates.

### Current ingestion flow

```text
RSS Feed
   ↓
Parse
   ↓
Normalize
   ↓
Validate
   ↓
Insert Article
```

### Test inventory

The repository currently contains the following test methods, counted
statically without running the test suite:

```text
27 unit test methods
9 integration test methods
```

The original Baseline Ingestion validation recorded 9 passing unit tests and 6
passing integration tests. Those are historical results and predate the later
normalization and duplicate-behavior tests; the pass status of the current
suite has not been revalidated here.

The integration suite includes coverage for:

1. valid article insertion;
2. duplicate article handling;
3. valid feed ingestion;
4. repeated feed ingestion without duplicates;
5. rejection of missing required fields;
6. failure on malformed feeds.

The integration tests use the separate `news_test` database and roll back their database changes after each test.

### Current limitations

The baseline ingestion implementation does not yet provide:

* production feed discovery;
* feed scheduling;
* retry and network-failure handling;
* advanced deduplication;
* article content extraction;
* story matching;
* claim extraction;
* evidence extraction;
* provenance discovery;
* assessment automation;
* LLM or embedding processing.

These remain future stages.

---

## 4. Next Development Stages

### Stage 1 — Baseline Ingestion

**Status: Implemented and validated**

Goal:

Create the first deterministic article-ingestion pipeline.

Implemented responsibilities:

* parse RSS feed items;
* normalize basic article data;
* validate required fields;
* associate articles with `source_id` and `feed_id`;
* store valid articles;
* prevent duplicate insertion;
* preserve database-generated discovery and creation information;
* return clear ingestion results;
* test the behavior using controlled local fixtures.

The current implementation uses a controlled local RSS fixture rather than depending on external feeds.

### Historical validation result

When Baseline Ingestion was validated, the recorded result was:

```text
9 unit tests passed
6 integration tests passed
```

These historical counts predate subsequent tests added for title and URL
normalization and duplicate article behavior.

The stage should remain considered complete at the current scope.

Future requirements discovered during production-oriented work may require revisiting this stage, but such changes should be driven by demonstrated requirements rather than speculation.

---

### Stage 2 — Deduplication

**Status: In progress**

Goal:

Identify when incoming articles are duplicates or near-duplicates of previously stored material.

The current `(source_id, url)` uniqueness constraint remains the baseline duplicate-insertion safeguard.

The current work has added deterministic title and URL normalization utilities
and tests for duplicate article behavior. The normalization utilities are not
yet used by ingestion or duplicate classification. This stage concerns broader
duplicate detection beyond the existing database constraint.

Initial approach:

Use deterministic signals before introducing embeddings or LLM-based matching.

Possible signals include:

* canonical URL;
* normalized title;
* content hash;
* publication metadata;
* textual similarity.

The exact algorithm should be documented and tested before becoming production logic.

Exit criteria:

Known duplicate scenarios are handled predictably and can be tested automatically.

---

### Stage 3 — Story Matching

**Status: Not started**

Goal:

Determine whether an article belongs to an existing story.

The baseline matcher must allow three outcomes:

* `MATCH`
* `NEW_STORY`
* `REVIEW`

The system must not force an uncertain article into an existing story.

Initial implementation should be deterministic.

AI/LLM-assisted matching may be introduced later and compared against the deterministic baseline.

Exit criteria:

Known matching and non-matching cases produce reproducible results, including explicit handling of uncertainty.

---

### Stage 4 — Claim and Evidence Pipeline

**Status: Not started**

Goal:

Connect articles to claims and evidence while preserving provenance.

The intended flow is:

```text
Article
   ↓
Story
   ↓
Claim
   ↓
Evidence
   ↓
Evidence provenance
   ↓
Assessment
```

The implementation must preserve the distinction between:

* what an article reports;
* what evidence exists;
* what evidence supports or contradicts a claim;
* and what an assessment concludes.

Exit criteria:

A claim can be traced through its supporting and contradicting evidence back to the relevant provenance.

---

### Stage 5 — Assessment Workflow

**Status: Not started**

Goal:

Implement a reviewable assessment process.

The system should support:

* human assessment;
* rule-based assessment;
* AI proposals;
* human review;
* historical assessment records.

AI-generated assessments must not silently replace historical decisions.

Exit criteria:

Every assessment can be identified by:

* actor type;
* actor name when applicable;
* assessment role;
* status;
* reasoning;
* creation time.

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

## 5. Not Yet Started

The following are intentionally not considered implemented:

* production feed ingestion;
* production deduplication;
* production story matching;
* production claim extraction;
* production evidence extraction;
* automated assessment;
* LLM integration;
* embeddings;
* vector search;
* autonomous agents;
* scheduled processing;
* production web interface;
* large-scale deployment.

The current Baseline Ingestion implementation is a tested development milestone, not yet a production ingestion system.

---

## 9. Current Priority

The immediate priority is now:

**Deduplication**

Baseline Ingestion has reached its current implementation and validation milestone.

The next work should therefore investigate deterministic duplicate detection beyond the existing `(source_id, url)` database constraint.

No AI integration, embeddings, autonomous agents, or UI work is required at this stage.

The database schema is not expected to change unless implementation demonstrates a requirement that the current model cannot represent.
