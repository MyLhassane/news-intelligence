# Project Roadmap

## 1. Current Project State

The project has completed its initial architecture and data-model validation phase.

The PostgreSQL model has been created and manually tested against:

* real-world news and research material,
* provenance relationships,
* claim/evidence relationships,
* conflicting evidence,
* shared underlying sources,
* independent evidence,
* historical assessments,
* and analytical database views.

The repository has now been created with documentation intended to preserve the project's architecture, decisions, testing history, and operating principles.

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

---

## 3. Current Work

The immediate objective is to turn the manually validated design into a reproducible project.

### Current tasks

1. Extract the actual tested PostgreSQL schema into:

   * `database/schema.sql`

2. Extract the actual tested PostgreSQL views into:

   * `database/views.sql`

3. Preserve the tested database model exactly rather than reconstructing it manually.

4. Create reproducible test/seed data where appropriate.

5. Establish a repeatable way to initialize and validate the database.

6. Review repository documentation for consistency before the first meaningful Git commit.

---

## 4. Next Development Stages

### Stage 1 — Database Canonicalization

Goal:

Make the PostgreSQL schema represented in the repository the canonical reproducible definition of the tested database structure.

Exit criteria:

* schema can be recreated from repository SQL,
* views can be recreated from repository SQL,
* documented model matches actual database structure,
* no undocumented tables or columns are introduced.

---

### Stage 2 — Reproducible Test Data

Goal:

Create controlled test cases representing important system situations.

Initial cases should include:

* one article and one story,
* multiple articles covering one story,
* duplicate or near-duplicate articles,
* multiple articles based on the same evidence,
* genuinely different evidence,
* supporting evidence,
* contradicting evidence,
* insufficient evidence,
* historical assessment changes.

Synthetic data must remain clearly identified as synthetic.

Exit criteria:

The important provenance and assessment rules can be tested repeatedly without manually reconstructing the database state.

---

### Stage 3 — Baseline Ingestion

Goal:

Create the first deterministic article-ingestion pipeline.

Initial responsibilities:

* read configured feeds,
* retrieve article metadata,
* normalize article data,
* store articles,
* prevent duplicate insertion,
* record discovery information.

The first implementation should prioritize correctness and traceability over scale.

Exit criteria:

A configured feed can be processed repeatedly without creating uncontrolled duplicate articles.

---

### Stage 4 — Deduplication

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

### Stage 5 — Story Matching

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

### Stage 6 — Claim and Evidence Pipeline

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

### Stage 7 — Assessment Workflow

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

### Stage 8 — AI-Assisted Processing

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

### Stage 9 — Automation

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

### Stage 10 — User Interface

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
Ingestion
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

**Canonicalize the validated database model inside the repository and make its recreation reproducible.**

No AI integration, embeddings, autonomous agents, or UI work is required at this stage.
