# System Architecture

## 1. Architectural Objective

The architecture is designed around one central requirement:

> Information should remain traceable from a published article to the underlying story, claims, evidence, provenance, and assessment history.

The system therefore separates concepts that are often mixed together in ordinary news aggregation systems.

## 2. High-Level Architecture

```text
                         ┌──────────────────┐
                         │      Sources     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Ingestion    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     Articles     │
                         └────────┬─────────┘
                                  │
                         ┌────────┴─────────┐
                         ▼                  ▼
                ┌─────────────────┐  ┌─────────────────┐
                │ Deduplication   │  │ Metadata        │
                │                 │  │ Normalization   │
                └────────┬────────┘  └─────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Story Matching  │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     Stories     │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │     Claims      │
                └──────┬─────┬────┘
                       │     │
              ┌────────┘     └─────────┐
              ▼                        ▼
      ┌─────────────────┐      ┌─────────────────┐
      │    Evidence     │      │  Article/Claim  │
      │                 │      │   Relations     │
      └────────┬────────┘      └─────────────────┘
               │
               ▼
      ┌─────────────────┐
      │   Provenance    │
      └────────┬────────┘
               │
               ▼
      ┌─────────────────┐
      │   Assessment    │
      └─────────────────┘
```

## 3. Main Domain Objects

### Sources

Represent organizations, institutions, publications, platforms, or other origins of published information.

A source has a functional classification such as:

* news agency;
* broadcaster;
* newspaper;
* research institution;
* government organization;
* court or legal record;
* company;
* social media;
* aggregator;
* other.

The classification describes the source's role.

It is not a universal trust score.

### Source Policies

Record documented policies or standards associated with a source.

Examples include:

* editorial standards;
* correction policies;
* source transparency;
* conflicts of interest;
* fact-checking policies;
* independence statements.

These records describe documented policies. They do not automatically establish that a source is neutral or universally reliable.

### Source Feeds

Represent mechanisms through which articles can be discovered or ingested.

Examples include:

* RSS;
* API;
* website;
* other feed mechanisms.

### Articles

Represent individual published or discovered news items.

An article records information such as:

* source;
* feed;
* title;
* URL;
* author;
* publication time;
* discovery time;
* language;
* content;
* summary;
* content hash.

Articles are the primary input objects entering the processing pipeline.

### Stories

Represent an underlying event, development, investigation, or information thread that may be covered by multiple articles.

A story can contain many articles.

An article can also have different relationships to a story, such as:

* coverage;
* update;
* follow-up;
* background;
* analysis;
* correction.

### Claims

Represent identifiable statements associated with a story.

Claims are typed because not every statement has the same verification characteristics.

Current claim types include:

* factual;
* quote;
* attribution;
* prediction;
* opinion;
* statistical;
* other.

### Evidence

Represents a document, record, report, statement, dataset, transcript, image, video, or other information object that may be relevant to a claim.

Evidence is separate from articles because an article may report information originating elsewhere.

### Provenance

Provenance records relationships between evidence and the entities responsible for producing, publishing, issuing, or otherwise participating in that evidence.

This distinction is important because:

```text
Article publisher
        ≠
Producer of underlying evidence
```

An article may report a research paper produced by a research collaboration.

### Assessments

Represent evaluations of claims.

Assessments record:

* status;
* actor type;
* actor name;
* reasoning;
* role;
* timestamp.

The system preserves assessment history instead of treating the latest assessment as the only meaningful record.

## 4. Relationship Model

The architecture intentionally separates several relationships.

### Article → Story

Answers:

> Which story does this article belong to?

### Claim → Article

Answers:

> Which article reports, supports, contradicts, quotes, or attributes this claim?

### Claim → Evidence

Answers:

> What evidence is relevant to this claim, and how?

### Evidence → Source

Answers:

> Who produced, published, issued, or otherwise participated in this evidence?

### Article → Evidence

Answers:

> What relationship does this article have to this evidence?

These relationships should not be collapsed into a single generic relationship.

## 5. Information Flow

The conceptual processing flow is:

```text
Source
  ↓
Feed
  ↓
Article
  ↓
Deduplication
  ↓
Story Matching
  ↓
Story
  ↓
Claim Extraction
  ↓
Evidence Identification
  ↓
Provenance Linking
  ↓
Assessment
```

Each stage should produce inspectable results.

## 6. Deterministic Baseline

The first implementation should establish deterministic behavior wherever practical.

Examples include:

* URL normalization;
* content hashing;
* duplicate detection;
* basic metadata normalization;
* explicit relationship storage;
* reproducible database queries.

More advanced approaches such as:

* embeddings;
* semantic similarity;
* LLM-based story matching;
* LLM-based claim extraction;

may be introduced later.

They should be evaluated against the deterministic baseline rather than replacing it without comparison.

## 7. Assessment Architecture

Assessment is deliberately separated from evidence.

Evidence records what information is available.

Assessment records an evaluation of that information.

Therefore:

```text
Evidence
    ≠
Assessment
```

Likewise:

```text
Supporting evidence
    ≠
Automatic proof
```

and:

```text
Contradicting evidence
    ≠
Automatic resolution
```

The assessment layer exists because evidence can be incomplete, conflicting, ambiguous, or context-dependent.

## 8. Historical Model

Current state and historical state are separate concepts.

For claims:

```text
claims.status
```

represents the current quick status.

While:

```text
claim_assessments
```

preserves the assessment history.

A new assessment should normally be appended rather than replacing an earlier assessment.

## 9. AI Layer

AI is considered a processing layer over the underlying information model.

Conceptually:

```text
                    ┌──────────────────┐
                    │        AI        │
                    │ extraction       │
                    │ matching         │
                    │ classification   │
                    │ proposals        │
                    └────────┬─────────┘
                             │
                             ▼
Sources → Articles → Stories → Claims → Evidence
                                      │
                                      ▼
                                  Assessment
```

AI should not become the hidden authority behind the data model.

Important outputs should remain linked to the underlying records that support them.

## 10. Architectural Constraint

The system should favor explicit relationships over implicit assumptions.

If an important relationship cannot be represented clearly, the architecture should be examined before adding automation.

The database is therefore not merely a storage layer.

It is part of the reasoning and provenance model of the system.
