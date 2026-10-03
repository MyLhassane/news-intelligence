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

The completed reproducibility and provenance milestone was committed as:

```text
7c8883f Document database reproducibility and provenance tests
```

The local `main` branch and `origin/main` are synchronized after this milestone.

---

## 3. Current Work

The current implementation stage is:

**Baseline Ingestion**

The objective is to turn the validated data model into the smallest deterministic article-ingestion pipeline.

The first implementation should establish a controlled and reproducible path from an input feed to stored `articles`.

### Current responsibilities

The baseline ingestion stage should:

* read a configured feed,
* parse feed items,
* normalize basic article fields,
* validate required fields,
* associate articles with `source_id` and `feed_id`,
* store valid articles,
* prevent duplicate insertion,
* preserve discovery information,
* produce clear and testable results.

The initial implementation should use a controlled local feed fixture before depending on external feeds.

### Initial article fields

Required:

* `source_id`
* `feed_id`
* `title`
* `url`

Optional:

* `author`
* `published_at`
* `language`
* `content`

Database-generated fields such as `discovered_at`, `created_at`, and `updated_at` remain under database control.

### Baseline ingestion flow

```text
Feed
  ↓
Parse
  ↓
Normalize basic fields
  ↓
Validate required fields
  ↓
Insert article
```

The ingestion stage does not perform story matching, claim extraction, evidence extraction, or assessment.

### Baseline ingestion tests

The initial test suite should cover at least:

1. Valid feed → articles inserted.
2. Re-running the same feed → no duplicate articles.
3. Missing title → item rejected.
4. Missing URL → item rejected.
5. Missing optional fields → article can still be inserted.
6. Malformed feed → ingestion fails clearly.

The existing `(source_id, url)` uniqueness constraint should be used as the initial duplicate-insertion safeguard.

The behavior of updating already stored article fields is intentionally outside the initial baseline until a demonstrated requirement exists.

---

## 4. Next Development Stages

### Stage 1 — Baseline Ingestion

Goal:

Create the first deterministic article-ingestion pipeline.

Initial responsibilities:

* read configured feeds,
* parse feed items,
* normalize article data,
* validate required fields,
* store articles,
* prevent duplicate insertion,
* record discovery information.

The first implementation should prioritize correctness and traceability over scale.

Exit criteria:

* a controlled feed can be processed successfully,
* valid articles are stored correctly,
* invalid required fields are handled predictably,
* the same feed can be processed repeatedly without creating uncontrolled duplicate articles,
* the behavior is covered by automated tests,
* the implementation and limitations are documented.

---

### Stage 2 — Deduplication

Goal:

Identify when incoming articles are duplicates or near-duplicates of previously stored material.

Initial approach:

Use deterministic signals before introducing embeddings or LLM-based matching.

Possible signals include:

* canonical URL,
* normalized title,
* content hash,
* publication metadata,
* textual similarity.

The exact algorithm should be documented and tested before becoming production logic.

Exit criteria:

Known duplicate scenarios are handled predictably and can be tested automatically.

---

### Stage 3 — Story Matching

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

* what an article reports,
* what evidence exists,
* what evidence supports or contradicts a claim,
* and what an assessment concludes.

Exit criteria:

A claim can be traced through its supporting and contradicting evidence back to the relevant provenance.

---

### Stage 5 — Assessment Workflow

Goal:

Implement a reviewable assessment process.

The system should support:

* human assessment,
* rule-based assessment,
* AI proposals,
* human review,
* historical assessment records.

AI-generated assessments must not silently replace historical decisions.

Exit criteria:

Every assessment can be identified by:

* actor type,
* actor name when applicable,
* assessment role,
* status,
* reasoning,
* creation time.

---

### Stage 6 — AI-Assisted Processing

AI should be introduced only after deterministic baselines exist.

Potential uses:

* claim extraction,
* article/story matching,
* evidence identification,
* summarization,
* classification,
* assessment proposals.

AI output must remain distinguishable from verified source material.

AI must not become the source of truth merely because it produces a confident-looking answer.

Exit criteria:

AI-assisted processing can be compared with deterministic and/or human-reviewed results.

---

### Stage 7 — Automation

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

A UI will be developed only after the underlying data and processing model are sufficiently stable.

The UI should expose the evidence trail rather than hide it.

Potential views include:

* stories,
* articles,
* claims,
* evidence,
* provenance,
* conflicting evidence,
* assessment history,
* source information.

The UI should not imply certainty that the underlying data does not support.

---

## 5. Not Yet Started

The following are intentionally not considered implemented:

* production feed ingestion,
* production deduplication,
* production story matching,
* production claim extraction,
* production evidence extraction,
* automated assessment,
* LLM integration,
* embeddings,
* vector search,
* autonomous agents,
* scheduled processing,
* production web interface,
* large-scale deployment.

These may be developed later.

The current Baseline Ingestion stage is an implementation milestone, not yet a production ingestion system.

---

## 6. Development Order

The project should generally progress in this order:

```text
Validated Database Model
        ↓
Canonical SQL
        ↓
Reproducible Tests
        ↓
Baseline Ingestion
        ↓
Deduplication
        ↓
Story Matching
        ↓
Claims
        ↓
Evidence
        ↓
Provenance
        ↓
Assessment
        ↓
AI Assistance
        ↓
Automation
        ↓
Interface
```

This order is not absolute, but changes to it should be justified and documented.

---

## 7. Milestone Principle

A stage is considered complete only when its behavior can be demonstrated and tested.

A feature is not considered complete merely because:

* code exists,
* an AI agent generated it,
* a database column was added,
* or a prototype appeared to work once.

The project should prefer:

```text
small implementation
        ↓
test
        ↓
observe failure
        ↓
adjust
        ↓
document
        ↓
commit
```

over large speculative implementations.

---

## 8. Architectural Stability Rule

The roadmap does not authorize future stages to redesign the architecture automatically.

If implementation reveals that the current model cannot represent a real requirement:

1. document the limitation,
2. demonstrate the requirement,
3. determine whether the existing model can represent it,
4. consider the smallest appropriate change,
5. record the architectural decision,
6. update the affected documentation,
7. then implement the change.

Database expansion should therefore be driven by demonstrated requirements rather than anticipated possibilities.

---

## 9. Current Priority

The immediate priority is:

**Baseline Ingestion**

The next concrete milestone is to establish a deterministic, reproducible article-ingestion path using a controlled feed fixture and automated tests.

No AI integration, embeddings, autonomous agents, or UI work is required at this stage.

The database schema is not expected to change unless implementation demonstrates a requirement that the current model cannot represent.
