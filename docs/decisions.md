# Architecture Decisions

This document records important decisions that shape the News Intelligence system.

The purpose is to preserve architectural reasoning, not merely the final implementation.

A future implementation should not reverse an established decision without explicitly revisiting the underlying reasoning.

---

# ADR-001 — Use Provenance Instead of a Universal Source Trust Score

**Status:** Accepted

## Context

News sources have different institutional roles, editorial processes, relationships to events, and relationships to underlying evidence.

Reducing these differences to a single trust score would hide important information and create a false impression of precision.

## Decision

The system will model source characteristics and provenance explicitly rather than assigning a universal trust score to each source.

The database therefore records:

* source type;
* documented source policies;
* article relationships;
* evidence relationships;
* evidence provenance;
* assessment history.

## Consequence

The system preserves more information about why a piece of information is being considered.

It also avoids treating a numeric source score as a substitute for evidence analysis.

---

# ADR-002 — Article Count Is Not Evidence Independence

**Status:** Accepted

## Context

A single statement, document, press release, or research result may be reported by many news organizations.

Counting every article as an independent confirmation would therefore overstate the amount of independent evidence.

## Decision

The system will explicitly model relationships between:

```text
Article
   ↓
Evidence
   ↓
Evidence Source
```

Articles that depend on the same underlying evidence must remain distinguishable from genuinely separate evidence.

## Consequence

The system can represent:

```text
Reuters ──┐
AP ───────┼──→ same evidence
Other ────┘
```

without treating the three articles as three independent evidence items.

---

# ADR-003 — Separate Article-to-Evidence from Claim-to-Evidence

**Status:** Accepted

## Context

An article can mention or report evidence without that evidence necessarily supporting every claim contained in the article.

A single generic relationship would make this distinction difficult to preserve.

## Decision

The system uses separate relationships:

```text
article_evidence
claim_evidence
```

`article_evidence` represents the relationship between an article and an evidence item.

`claim_evidence` represents the relationship between a claim and an evidence item.

## Consequence

The system can represent evidence at both levels without assuming that article-level evidence automatically applies to every claim.

---

# ADR-004 — Separate Evidence from Assessment

**Status:** Accepted

## Context

Evidence records information that is available.

Assessment represents an evaluation of that information.

Evidence can be:

* incomplete;
* conflicting;
* ambiguous;
* contextual;
* difficult to interpret.

Therefore evidence alone should not automatically determine the final status of a claim.

## Decision

Evidence and assessment remain separate layers.

```text
Evidence
    ↓
Assessment
```

rather than:

```text
Evidence
    ↓
automatic truth value
```

## Consequence

The system can preserve evidence even when its interpretation remains unresolved.

---

# ADR-005 — Preserve Assessment History

**Status:** Accepted

## Context

A claim may be assessed differently as new information becomes available.

Overwriting the previous assessment would destroy useful historical information.

## Decision

`claim_assessments` is an append-oriented historical record.

A new assessment should normally create a new record.

`claims.status` represents the current quick status.

## Consequence

The system can represent:

```text
unclear
   ↓
supported
   ↓
partially_supported
```

while preserving the earlier states.

---

# ADR-006 — AI Is a Processing Layer, Not the Source of Truth

**Status:** Accepted

## Context

AI can assist with extraction, classification, matching, summarization, and assessment proposals.

However, AI-generated output is itself a derived result and should not silently become the authoritative source of information.

## Decision

AI is treated as a processing layer.

AI may produce:

* proposals;
* classifications;
* extracted claims;
* matching candidates;
* evidence suggestions;
* assessment proposals.

The underlying article, evidence, provenance, and human decisions remain separately represented.

## Consequence

AI can be improved or replaced without destroying the underlying information model.

---

# ADR-007 — Deterministic Baseline Before Advanced AI

**Status:** Accepted

## Context

LLMs and semantic models may improve some processing tasks, but their behavior can be difficult to inspect and compare.

Without a baseline, it becomes difficult to determine whether a more complex method actually improves the system.

## Decision

Where practical, deterministic or explainable methods will establish the initial baseline.

Examples:

* URL normalization;
* content hashing;
* duplicate detection;
* metadata normalization;
* basic story matching.

Advanced methods may later include:

* embeddings;
* semantic similarity;
* LLM-based matching;
* LLM-based extraction.

## Consequence

Future AI methods can be evaluated against an understandable baseline.

---

# ADR-008 — Story Matching Must Allow Uncertainty

**Status:** Accepted

## Context

An incoming article may clearly belong to an existing story, clearly represent a new story, or fall into an ambiguous middle ground.

Forcing every article into MATCH or NEW_STORY would create false relationships.

## Decision

Story matching conceptually produces:

```text
MATCH
NEW_STORY
REVIEW
```

`REVIEW` is a legitimate result rather than a failure.

## Consequence

The system can defer uncertain decisions instead of hiding uncertainty.

---

# ADR-009 — Do Not Add Database Structures Speculatively

**Status:** Accepted

## Context

As the project grows, new features will create pressure to add tables, columns, and relationships.

Adding structures before demonstrating that they are necessary can make the model unnecessarily complex.

## Decision

Before adding a table, column, or relationship:

1. define the requirement;
2. inspect the current model;
3. attempt to represent it using existing structures;
4. identify the limitation;
5. determine the smallest required change;
6. test it;
7. document the change.

## Consequence

Schema growth remains evidence-driven.

---

# ADR-010 — Real and Synthetic Data Must Remain Distinguishable

**Status:** Accepted

## Context

Synthetic data is useful for testing conflicts, provenance, and edge cases.

However, synthetic records must never be confused with real-world information.

## Decision

Synthetic test data must be explicitly identified and must not be presented as real evidence.

## Consequence

Database tests can be comprehensive without contaminating the project's factual dataset.

---

# ADR-011 — Source Classification Is Descriptive

**Status:** Accepted

## Context

Sources have different institutional and functional roles.

A classification such as `news_agency` or `research_institution` is useful for understanding those roles.

It should not silently become a quality ranking.

## Decision

`source_type` describes the functional or institutional role of a source.

It is not a trust score, reliability score, or political neutrality score.

## Consequence

The database retains useful source metadata without pretending that a single category determines information quality.

---

# ADR-012 — Historical Records Should Not Be Rewritten

**Status:** Accepted

## Context

The system is intended to preserve how information and assessments evolved over time.

Silently changing historical records would make it difficult to reconstruct what the system knew or concluded at an earlier point.

## Decision

Historical assessments and important provenance relationships should be preserved.

When a new understanding is reached, the preferred approach is to add a new record or explicit correction rather than silently rewriting history.

## Consequence

The system can eventually support temporal investigation and auditability.

---

# ADR-013 — Repository Documentation Is Project Memory

**Status:** Accepted

## Context

Important architectural knowledge should not depend on one conversation, one developer, or one AI model retaining the context.

## Decision

The repository documentation is part of the project's persistent memory.

Important decisions, architecture, testing methodology, and project direction must be recorded in the repository.

## Consequence

Future developers and AI agents can reconstruct the project's reasoning from the repository itself.

---

# ADR-014 — Prototype Code Is Not Production Code

**Status:** Accepted

## Context

During development, experimental code may be useful for testing an idea.

A prototype may not satisfy the project's architecture, testing, error handling, or integration requirements.

## Decision

Prototype, test, production, and documentation artifacts must remain distinguishable.

Prototype code must not silently become production code.

Before integration, the prototype must be reviewed against the current architecture.

## Consequence

Experiments can be performed quickly without weakening the production architecture.

---

# ADR-015 — Evidence Relationships Do Not Automatically Determine Claim Status

**Status:** Accepted

## Context

A claim may have both supporting and contradicting evidence.

The existence of one relationship type does not establish that the evidence is equally strong, independent, complete, or authoritative.

## Decision

Relationships such as:

```text
supports
contradicts
```

describe recorded relationships.

They do not automatically calculate the final claim status.

## Consequence

Assessment remains an explicit reasoning layer.

A conflict can be recorded without pretending that the database itself has resolved it.

---

# Reconsideration Policy

An accepted decision may be revisited when new evidence demonstrates that:

* the original assumption was incorrect;
* the requirement has materially changed;
* the current architecture cannot represent a necessary capability;
* a simpler or more reliable model has been demonstrated.

Revisiting a decision should not silently erase the previous decision.

Instead:

1. record why the decision is being reconsidered;
2. document the new evidence;
3. record the replacement decision;
4. preserve the historical record.
