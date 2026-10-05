# News Intelligence

An automated news intelligence system designed to collect, organize, connect, and assess information across multiple sources while preserving provenance and historical assessments.

## Project Status

**Current stage: Baseline Ingestion**

The database model has been designed, validated, and transferred into the repository as the canonical PostgreSQL schema.

The project has now moved from database-model validation into reproducible software development.

### Current capabilities

* Canonical PostgreSQL schema
* Reproducible database setup
* Synthetic database test data
* RSS feed parsing
* Article normalization
* Article validation
* Baseline article ingestion
* Duplicate prevention through `(source_id, url)`
* Integration tests using a controlled local RSS fixture
* Transaction-safe integration testing

### Current test status

* **9 unit tests — passing**
* **6 integration tests — passing**

The current baseline has been tested for:

* valid feed ingestion;
* repeated feed ingestion without duplicate articles;
* missing article titles;
* missing article URLs;
* missing optional fields;
* malformed RSS feeds.

## Purpose

The system is intended to transform a stream of news articles into structured, traceable information:

```text
Sources
   ↓
Ingestion
   ↓
Articles
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
```

The objective is not to determine a single "truth source" or assign simple trust scores to sources.

Instead, the system records:

* where information came from;
* how articles relate to stories;
* which claims are associated with stories;
* what evidence is associated with each claim;
* who produced or published that evidence;
* whether multiple reports depend on the same underlying evidence;
* how claims were assessed;
* and how assessments change over time.

## Core Principles

### 1. Provenance matters

Information should be traceable to the articles and evidence supporting it.

### 2. Repetition is not independence

Several news articles repeating the same underlying statement do not automatically constitute several independent confirmations.

### 3. AI is a processing layer

AI may eventually extract, classify, match, summarize, or propose an assessment.

AI output is not automatically treated as authoritative or as the source of truth.

### 4. Assessments are historical

Previous assessments must remain available.

A later assessment should be recorded as a new event rather than silently replacing the previous assessment.

### 5. Uncertainty must be representable

The system must be able to represent situations where evidence is incomplete, conflicting, ambiguous, or insufficient.

### 6. Architecture should be evidence-driven

New database structures should not be added merely because a future feature might need them.

First determine whether the existing model can represent the requirement.

### 7. Deterministic baselines come first

Where possible, deterministic methods should establish a baseline before introducing LLMs, embeddings, or other probabilistic methods.

This allows future AI-based methods to be evaluated against an understandable baseline.

### 8. Real and synthetic data remain distinguishable

Synthetic records are used to test the architecture and processing logic.

They must not be treated as real-world evidence or factual reporting.

## Current Pipeline

The current implemented baseline covers:

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

### Parsing

RSS items are parsed into an internal representation containing fields such as:

* title
* URL
* publication date
* author
* description

Malformed XML causes the parsing stage to fail rather than producing partially trusted data.

### Normalization

Feed-specific fields are converted into the canonical article representation.

For example:

```text
RSS description → article summary
RSS pubDate    → timezone-aware datetime
```

RSS `description` is not treated as full article content.

### Validation

The baseline requires:

* title
* URL

Optional fields may be absent.

Invalid articles are rejected before insertion.

### Ingestion

Validated articles are inserted into the `articles` table.

The existing database constraint:

```text
(source_id, url)
```

prevents duplicate articles from the same source.

The current ingestion behavior is intentionally conservative:

* first insertion → insert;
* repeated insertion → skip;
* existing article → do not silently update it.

Updating existing article records is outside the current baseline scope.

## Current Database Model

The current model contains entities for:

* sources
* source policies
* source feeds
* articles
* stories
* article-story relationships
* claims
* claim-source relationships
* evidence
* claim-evidence relationships
* evidence-source provenance
* article-evidence relationships
* claim assessments

The canonical schema is stored in:

```text
database/schema.sql
database/views.sql
```

Synthetic reproducibility data is stored under:

```text
database/seeds/
```

The database model and its design decisions are documented separately in `docs/`.

## Repository Structure

```text
news-intelligence/
│
├── README.md
├── AGENTS.md
├── pyproject.toml
├── .gitignore
│
├── docs/
│   ├── vision.md
│   ├── architecture.md
│   ├── pipeline.md
│   ├── database-schema.md
│   ├── decisions.md
│   ├── testing.md
│   └── roadmap.md
│
├── database/
│   ├── schema.sql
│   ├── views.sql
│   └── seeds/
│
├── src/
│   └── news_intelligence/
│       ├── rss_parser.py
│       ├── article_normalization.py
│       ├── article_validation.py
│       ├── article_ingestion.py
│       └── baseline_ingestion.py
│
├── tests/
│   ├── fixtures/
│   │   └── feeds/
│   │       ├── baseline.xml
│   │       └── invalid.xml
│   ├── unit/
│   └── integration_test_ingestion.py
│
├── scripts/
└── config/
```

## Development Environment

The Python project uses a local virtual environment and a package configuration defined in `pyproject.toml`.

The current project targets:

* Python 3.13+
* PostgreSQL 16+
* psycopg 3

The development database used by integration tests is:

```text
news_test
```

Integration tests must not use the production `news` database.

Test database changes are performed inside transactions and rolled back after the test.

## Development Philosophy

The project should progress in small, verifiable stages.

Each stage should answer:

1. What problem are we solving?
2. Can the existing architecture represent it?
3. What is the smallest change required?
4. How will the change be tested?
5. What documentation must be updated?

Production code, tests, prototypes, and documentation should remain clearly distinguishable.

The preferred development cycle is:

```text
Implement
   ↓
Test
   ↓
Observe
   ↓
Adjust
   ↓
Document
   ↓
Commit
```

The repository documentation is part of the project's memory. Architectural decisions, database behavior, testing results, and completed work should not depend solely on conversation history.

## Development Roadmap

The planned development order is:

```text
Validated Database Model
        ↓
Canonical SQL
        ↓
Reproducible Tests
        ↓
Baseline Ingestion        ← current stage
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

### Current stage: Baseline Ingestion

The current stage establishes the deterministic ingestion foundation:

```text
Feed
 → Parse
 → Normalize
 → Validate
 → Insert
```

Advanced processing is intentionally outside this stage.

### Not yet implemented

The following are future stages, not current implementation requirements:

* advanced article deduplication;
* story matching;
* claim extraction;
* evidence extraction;
* automated provenance discovery;
* automated assessment;
* LLM processing;
* embeddings;
* AI agents;
* scheduling and automation;
* user interface.

Future work should build on the tested baseline rather than bypassing it.

## Documentation

The main project documentation is organized by responsibility:

* `docs/vision.md` — project purpose and long-term direction
* `docs/architecture.md` — system architecture and boundaries
* `docs/pipeline.md` — processing pipeline
* `docs/database-schema.md` — database model
* `docs/testing.md` — reproducibility and test procedures
* `docs/decisions.md` — important architectural decisions
* `docs/roadmap.md` — current development stages and priorities

`AGENTS.md` contains instructions for AI agents and contributors working on the repository.

## Current Direction

The immediate objective is to complete and stabilize the deterministic ingestion foundation before introducing more advanced processing.

The next development stage is **Deduplication**, but it should begin only after the current baseline implementation, tests, and documentation have been reviewed and committed.

The system should evolve from validated foundations rather than from a large amount of speculative code.
