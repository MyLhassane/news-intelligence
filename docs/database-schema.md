# Database Schema

## 1. Purpose

The database is the structural foundation of the News Intelligence system.

It does more than store records.

It represents relationships between:

* sources;
* articles;
* stories;
* claims;
* evidence;
* provenance;
* assessments.

The database therefore forms part of the project's reasoning and auditability model.

## 2. Design Principles

### Explicit Relationships

Important relationships are represented explicitly rather than inferred whenever possible.

### Provenance Preservation

The system must be able to distinguish an article from the underlying evidence it reports.

### Historical Assessments

Assessment history is preserved rather than overwritten.

### No Automatic Trust Scores

The schema does not assign universal trust scores to sources.

### No Automatic Independence Assumption

The existence of multiple articles does not imply multiple independent evidence sources.

### Current State vs History

Current claim status and historical assessments are separate concepts.

---

# 3. Tables

## 3.1 `sources`

Represents organizations, institutions, publications, platforms, and other information sources.

Important fields:

* `id`
* `name`
* `country`
* `source_type`
* `website`
* `active`
* `created_at`
* `updated_at`

`source_type` classifies the functional or institutional role of a source.

It is not a trust ranking.

Current supported source types include:

* `news_agency`
* `public_broadcaster`
* `private_broadcaster`
* `newspaper`
* `digital_news`
* `financial_news`
* `specialized_media`
* `fact_checking`
* `official_government`
* `international_organization`
* `research_institution`
* `regulatory_body`
* `court_or_legal_record`
* `company_primary`
* `social_media`
* `user_generated`
* `aggregator`
* `blog`
* `other`

---

## 3.2 `source_policies`

Stores documented policies or standards associated with a source.

Examples:

* editorial standards;
* corrections;
* source transparency;
* conflicts of interest;
* fact checking;
* anonymous source policies;
* independence;
* fact/opinion separation.

A policy record describes a documented policy.

It does not automatically establish that the source is neutral or universally reliable.

Relationship:

```text
sources
   │
   └──< source_policies
```

---

## 3.3 `source_feeds`

Represents mechanisms used to discover articles from a source.

Supported feed types:

* `rss`
* `api`
* `website`
* `other`

Relationship:

```text
sources
   │
   └──< source_feeds
```

A feed belongs to one source.

---

## 3.4 `articles`

Represents an individual published or discovered article.

Important fields:

* `source_id`
* `feed_id`
* `title`
* `url`
* `author`
* `published_at`
* `discovered_at`
* `language`
* `content`
* `summary`
* `content_hash`

An article belongs to one source.

A feed relationship is optional because an article may be discovered through mechanisms other than a currently registered feed.

Relationships:

```text
sources
   │
   └──< articles

source_feeds
   │
   └──< articles
```

The current uniqueness constraint is:

```text
(source_id, url)
```

This prevents duplicate URLs within the same source.

---

## 3.5 `stories`

Represents an underlying event, development, investigation, analysis, or information thread.

Important fields:

* `title`
* `summary`
* `story_type`
* `status`
* `first_seen_at`
* `last_updated_at`

Current story types include:

* `breaking_news`
* `ongoing_event`
* `developing_story`
* `analysis`
* `investigation`
* `background`
* `other`

Current story statuses:

* `active`
* `closed`
* `archived`

A story may contain many articles.

---

## 3.6 `article_stories`

Associates articles with stories.

This is a many-to-many relationship because:

* a story may have many articles;
* an article may potentially have relationships with more than one story.

Current relationship types:

* `coverage`
* `update`
* `follow_up`
* `background`
* `analysis`
* `correction`
* `other`

The `is_primary` field identifies the primary story relationship for an article when applicable.

Relationship:

```text
articles
   │
   └──< article_stories >──┐
                           │
                           ▼
                         stories
```

---

## 3.7 `claims`

Represents identifiable statements associated with a story.

Important fields:

* `story_id`
* `claim_text`
* `claim_type`
* `status`
* `first_seen_at`
* `last_checked_at`

Current claim types:

* `factual`
* `quote`
* `attribution`
* `prediction`
* `opinion`
* `statistical`
* `other`

Current claim statuses:

* `unverified`
* `supported`
* `disputed`
* `contradicted`
* `partially_supported`
* `unclear`

The claim status is a current state representation.

It is not the complete assessment history.

Relationship:

```text
stories
   │
   └──< claims
```

---

## 3.8 `claim_sources`

Associates claims with articles that report or otherwise relate to them.

Relationship types:

* `supports`
* `contradicts`
* `reports`
* `quotes`
* `attributes`
* `questions`
* `unclear`

Source roles include:

* `primary`
* `secondary`
* `independent_observer`
* `expert`
* `eyewitness`
* `official_statement`
* `documentary`
* `aggregator`
* `other`

Two concepts are deliberately separated:

```text
relationship
    =
how the article relates to the claim

source_role
    =
the role of the article/source in relation to the underlying information
```

This prevents simplistic counting of articles as independent confirmation.

---

## 3.9 `evidence`

Represents an underlying information object relevant to a claim.

Current evidence types include:

* `official_document`
* `government_statement`
* `court_record`
* `research_paper`
* `research_report`
* `statistical_data`
* `company_statement`
* `press_release`
* `transcript`
* `image`
* `video`
* `other`

Important fields include:

* `title`
* `url`
* `description`
* `published_at`
* `accessed_at`
* `language`

The URL is currently unique.

Evidence is deliberately separate from articles.

---

## 3.10 `claim_evidence`

Associates evidence with claims.

Relationship types:

* `supports`
* `contradicts`
* `context`
* `mentions`
* `unclear`

Optional `excerpt` records the relevant portion of the evidence.

Relationship:

```text
claims
   │
   └──< claim_evidence >──┐
                          │
                          ▼
                       evidence
```

Important rule:

A supporting relationship does not automatically mean that the claim is proven.

A contradicting relationship does not automatically resolve the claim.

The final assessment remains a separate layer.

---

## 3.11 `evidence_sources`

Represents provenance relationships between evidence and registered sources.

Current relationships:

* `producer`
* `publisher`
* `issuer`
* `participant`
* `author`
* `other`

This table is essential for distinguishing:

```text
producer of evidence
        ≠
publisher of an article about that evidence
```

Example:

```text
LUX-ZEPLIN
     │
     │ producer
     ▼
Research result
     │
     │ reported by
     ▼
Reuters article
```

---

## 3.12 `article_evidence`

Associates articles directly with evidence.

Current relationship types:

* `based_on`
* `quotes`
* `reports`
* `links_to`
* `mentions`
* `other`

This table is intentionally separate from `claim_evidence`.

The distinction is:

```text
article_evidence
    =
article ↔ evidence

claim_evidence
    =
claim ↔ evidence
```

An article may be associated with evidence without that evidence necessarily being relevant to every claim contained in the article.

---

## 3.13 `claim_assessments`

Stores historical assessments of claims.

Important fields:

* `claim_id`
* `assessment_status`
* `actor_type`
* `actor_name`
* `reasoning`
* `assessment_role`
* `created_at`

Assessment statuses:

* `supported`
* `partially_supported`
* `contradicted`
* `unclear`

Actor types:

* `human`
* `ai`
* `rule`
* `hybrid`

Assessment roles:

* `proposal`
* `review`
* `decision`

The table is append-oriented from a historical perspective.

A later assessment should normally be inserted as a new record rather than modifying an earlier assessment.

---

# 4. Relationship Overview

The current conceptual model can be represented as:

```text
sources
   │
   ├── source_policies
   │
   ├── source_feeds
   │       │
   │       └── articles
   │
   └── articles
           │
           ├── article_stories ────── stories
           │                              │
           │                              └── claims
           │                                   │
           │                                   ├── claim_sources ── articles
           │                                   │
           │                                   ├── claim_evidence ── evidence
           │                                   │                       │
           │                                   │                       └── evidence_sources ── sources
           │                                   │
           │                                   └── claim_assessments
           │
           └── article_evidence ───── evidence
```

This diagram is conceptual rather than a substitute for the actual SQL schema.

---

# 5. Important Distinctions

## Article vs Story

An article is a published information item.

A story is the underlying event or information thread being covered.

```text
many articles
      ↓
one story
```

## Article vs Evidence

An article is a publication.

Evidence may be the underlying document, research, statement, record, or other information referenced by the article.

## Claim vs Evidence

A claim is a statement being evaluated.

Evidence is information relevant to that statement.

## Evidence vs Assessment

Evidence records what information is available.

Assessment records an evaluation of that information.

## Current Status vs Historical Assessment

`claims.status` provides a current status.

`claim_assessments` preserves historical evaluations.

---

# 6. Independence and Provenance

The schema deliberately avoids a simple:

```text
source_count = evidence_strength
```

model.

Consider:

```text
Reuters ────────┐
AP ─────────────┼──→ Same official statement
Another outlet ─┘
```

There may be three articles but only one underlying evidence source.

The provenance model allows the system to represent this without treating all three articles as independent confirmation.

At the same time, shared provenance alone does not prove that two evidence records are identical.

The system should distinguish:

1. same source;
2. same underlying evidence;
3. evidence derived from another evidence item;
4. independent evidence.

These are not interchangeable concepts.

---

# 7. Current Validation State

The schema has been manually tested in PostgreSQL using both real-world and synthetic records.

### Real-world validation

A dark matter research story was used to validate relationships involving:

* Reuters;
* LUX-ZEPLIN;
* Lawrence Berkeley National Laboratory;
* Imperial College London;
* a research paper;
* article-to-evidence relationships;
* claim-to-evidence relationships;
* provenance.

### Synthetic validation

Synthetic records were used to test:

* conflicting evidence;
* subsequent resolution;
* historical assessments;
* shared underlying evidence;
* apparent multi-source confirmation;
* independent evidence relationships.

Synthetic records must never be interpreted as real-world evidence.

---

# 8. Current Views

The database currently includes analytical views for:

## `claim_intelligence`

Provides a detailed claim/evidence/provenance/assessment representation.

It is useful for inspecting the complete evidence chain.

## `claim_overview`

Provides a compact claim-level summary including:

* evidence count;
* producer count;
* issuer count;
* publisher count;
* latest assessment.

These counts describe recorded relationships.

They are not trust or independence scores.

## `claim_evidence_conflicts`

Identifies claims for which both supporting and contradicting evidence have been recorded.

The view does not decide which side is correct.

It only identifies the existence of recorded conflict.

---

# 9. Schema Change Policy

Before adding a table, column, or relationship:

1. Define the requirement.
2. Inspect the existing model.
3. Attempt to represent the requirement using existing structures.
4. Identify the exact limitation.
5. Determine the smallest structural change required.
6. Test the change.
7. Update this document.
8. Record an architectural decision when appropriate.

This prevents schema growth based on speculation.

---

# 10. Canonical SQL

The repository will maintain canonical SQL representations of the database:

```text
database/schema.sql
database/views.sql
```

These files should eventually reproduce the validated database structure and views.

They should be treated as project artifacts, not manually maintained descriptions that can drift from the actual schema.

Before declaring them canonical, they must be compared against the currently tested PostgreSQL database.
