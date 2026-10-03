# News Intelligence

An automated news intelligence system designed to collect, organize, connect, and assess information across multiple sources while preserving provenance and historical assessments.

## Project Status

**Current stage:** Foundation and data-model validation

The database model has been designed and manually tested in PostgreSQL.

The project is now being converted from a validated database design into a reproducible software project.

## Purpose

The system is intended to help transform a stream of news articles into structured, traceable information:

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
* which claims are extracted from stories;
* what evidence is associated with each claim;
* who produced or published that evidence;
* whether multiple reports depend on the same underlying evidence;
* how claims were assessed;
* and how assessments changed over time.

## Core Principles

### 1. Provenance matters

A statement should be traceable to the articles and evidence supporting it.

### 2. Repetition is not independence

Several news articles repeating the same underlying statement do not automatically constitute several independent confirmations.

### 3. AI is a processing layer

AI may extract, classify, match, summarize, or propose an assessment.

AI output is not automatically treated as authoritative.

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

The schema is currently validated in PostgreSQL and is being transferred into the repository as the canonical project schema.

## Repository Structure

```text
news-intelligence/
│
├── README.md
├── AGENTS.md
├── pyproject.toml
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
│
├── tests/
├── scripts/
└── config/
```

## Development Philosophy

The project should progress in small, verifiable stages.

Each stage should answer:

1. What problem are we solving?
2. Can the existing architecture represent it?
3. What is the smallest change required?
4. How will the change be tested?
5. What documentation must be updated?

Production code, tests, prototypes, and documentation should remain clearly distinguishable.

## Current Direction

The immediate objective is to establish the project foundation:

1. repository structure;
2. project documentation;
3. canonical database schema;
4. reproducible database tests;
5. deterministic processing baseline;
6. ingestion pipeline;
7. story matching;
8. claim and evidence processing;
9. assessment workflow;
10. later AI-assisted processing.

The system should evolve from validated foundations rather than from a large amount of speculative code.
