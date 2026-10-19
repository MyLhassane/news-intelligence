# Processing Pipeline

This document defines pipeline stage contracts and explains implemented
behavior. The active stage and its acceptance criteria are maintained in
[`roadmap.md`](roadmap.md); database structure is specified in
[`database-schema.md`](database-schema.md), and validation results are in
[`testing.md`](testing.md).

## 1. Purpose

The processing pipeline defines how information moves through the News Intelligence system.

The pipeline is intentionally divided into stages so that each stage can be:

* understood independently;
* tested independently;
* replaced or improved independently;
* inspected when something goes wrong.

The current conceptual pipeline is:

```text
Article
   ↓
Deduplication
   ↓
Story Matching
   ↓
Claim Extraction
   ↓
Evidence Identification
   ↓
Provenance Linking
   ↓
Assessment
```

Not every stage must be fully automated.

## 2. Stage 1 — Ingestion

### Input

Information discovered through a configured source feed.

Examples:

* RSS feed;
* API;
* website;
* other supported mechanism.

### Output

An `article` record containing normalized metadata and, where available, article content.

At ingestion time the system should preserve:

* original URL;
* source;
* feed;
* title;
* author;
* publication time;
* discovery time;
* language;
* content;
* content hash.

### Principle

Ingestion should preserve the original information before attempting interpretation.

---

## 3. Stage 2 — Deduplication

The purpose of deduplication is to identify articles that represent the same published item or substantially duplicate content.

Possible signals include:

* normalized URL;
* canonical URL;
* content hash;
* title similarity;
* publisher metadata;
* publication metadata.

The initial implementation should prefer deterministic signals.

### Current implementation status

Title normalization is implemented as a separate deterministic utility.

It applies Unicode case folding, trims surrounding whitespace, and collapses
consecutive whitespace. Punctuation is preserved, and empty titles are rejected.

The normalized title is actively used by `classify_duplicate` to identify `NEAR_DUPLICATE` relationships when an incoming article shares a normalized title with an existing article from the same source under a different URL. Title equality alone (when URLs differ) does not merge or delete articles, but classifies them as near-duplicates.

URL normalization is implemented as a separate deterministic utility.

It lowercases the URL scheme and hostname, removes default HTTP/HTTPS ports,
removes known tracking parameters, sorts distinct query keys deterministically (casefolded), preserves the relative order of repeated query values for the same key, preserves the original encoding representation of parameter values without double encoding, and removes fragments and empty query segments.

URLs containing credentials and URLs that do not use HTTP or HTTPS are rejected.

### Deterministic Duplicate Classification

A deterministic duplicate classification utility (`classify_duplicate`) is implemented using existing URL and title normalization utilities. It classifies relationships between an existing article and an incoming article into three categories:

1. **`EXACT_DUPLICATE`**: Same `source_id` and normalized URL (ignoring default ports, tracking parameters, and case differences in scheme/host).
2. **`NEAR_DUPLICATE`**: Same `source_id`, different URL, but matching normalized title (Unicode case-folded, whitespace-collapsed).
3. **`DISTINCT`**: Different source or distinct URLs and titles.

This classification does not delete, merge, or overwrite existing article records. Article records remain immutable in the database, preserving individual discovery time, source attribution, and raw URLs.

### Important distinction

Deduplication is not the same as story matching.

Two articles may be different articles while covering the same story.

Therefore:

```text
Duplicate articles
       ≠
Same story
```

---

## 4. Stage 3 — Story Matching

Story matching determines whether an article belongs to an existing story or represents a new story.

The system should not force uncertain matches.

The conceptual result should be one of:

```text
MATCH
NEW_STORY
REVIEW
```

### MATCH

The article is sufficiently related to an existing story according to the current matching rules.

### NEW_STORY

The article does not appear to belong to an existing story.

### REVIEW

There is insufficient evidence for an automatic decision.

This state is important because uncertainty should be represented rather than hidden.

### Initial Baseline

A standalone deterministic token-overlap (Jaccard similarity over normalized titles) utility (`match_story`) has been implemented as an initial baseline. It supports three outcomes:

1. **`MATCH`**: The article sufficiently overlaps with an existing story above the confidence threshold, with clear separation from alternatives.
2. **`NEW_STORY`**: The article has low similarity to all existing stories and represents a new event or topic.
3. **`REVIEW`**: There is insufficient or ambiguous evidence for an automatic decision (e.g. partial title overlap below confidence threshold, or ambiguous close scores between top matching stories, or missing titles).

The utility is not integrated into article ingestion or a persisted story workflow. It does not create or modify stories; uncertainty is represented in its result rather than forced into a match.

Semantic embeddings and LLM-based matching may be introduced later and evaluated against this deterministic baseline.

---

## 5. Stage 4 — Claim Extraction

Once an article has been associated with a story, relevant claims can be identified.

A claim should represent a meaningful statement rather than an arbitrary sentence fragment.

Claims should retain their type.

Current claim types include:

```text
factual
quote
attribution
prediction
opinion
statistical
other
```

### Important distinction

A quote is not necessarily a factual claim.

An attribution is not necessarily evidence that the attributed statement is true.

A prediction is not a fact simply because it was published.

An opinion should not automatically enter factual verification logic.

---

## 6. Stage 5 — Evidence Identification

Evidence identification attempts to determine what underlying information is relevant to a claim.

Potential evidence includes:

* official documents;
* government statements;
* court records;
* research papers;
* research reports;
* statistical data;
* company statements;
* press releases;
* transcripts;
* images;
* videos;
* other records.

The system should distinguish between:

```text
Article reports evidence
```

and:

```text
Evidence supports a claim
```

These are different relationships.

An article may report evidence without that evidence necessarily proving every claim contained in the article.

---

## 7. Stage 6 — Provenance Linking

Provenance determines the origin and chain of an evidence item.

The system should attempt to distinguish roles such as:

* producer;
* publisher;
* issuer;
* participant;
* author;
* other.

Example:

```text
Research collaboration
       │
       │ produces
       ▼
Research paper
       │
       │ reported by
       ▼
News article
```

In this case the news organization is the publisher of the article, but it is not necessarily the producer of the research paper.

### Independence

Provenance should be used when evaluating apparent multi-source confirmation.

For example:

```text
Reuters ──────┐
              │
AP ───────────┼──→ Same official statement
              │
Other outlet ─┘
```

This may represent several articles but only one underlying information source.

Therefore:

```text
Number of articles
       ≠
Number of independent evidence items
```

The system should preserve this distinction instead of reducing it to a source count.

### Claim-to-Evidence Provenance Trace

The standalone `trace_claim_provenance` utility assembles a claim's linked
supporting, contradicting, or contextual evidence with its supplied
`evidence_sources` provenance links. It keeps producer/issuer roles distinct
from publisher and other roles. `traceable` is true only when there is at
least one evidence item and every item has at least one supplied provenance
link.

The utility reports whether a producer or issuer is present; this is not a
verification of independence. It does not query or write to the database,
discover provenance, or create claim/evidence relationships. Those inputs
must already be linked by the caller.

---

## 8. Stage 7 — Assessment

Assessment evaluates a claim in light of the available information.

Current assessment statuses include:

```text
supported
partially_supported
contradicted
unclear
```

Assessment should consider:

* associated evidence;
* relationships between evidence and claim;
* provenance;
* conflicting evidence;
* relevant context;
* limitations of the available information.

### Important rule

Evidence relationships do not automatically determine the final assessment.

For example:

```text
Supporting evidence
       +
Contradicting evidence
       ↓
Does not automatically produce a final status
```

The assessment layer exists because evidence may conflict or require interpretation.

### Standalone Assessment Baseline

`create_assessment` constructs an assessment record with status, actor type,
optional actor name and reasoning, role, and creation time. It appends the new
record to a copied in-memory history list, preserving prior entries.

This utility does not write to `claim_assessments`, update `claims.status`, or
enforce a proposal/review/decision sequence. Persistence and integration into
a reviewable workflow remain outstanding.

---

## 9. Assessment History

Assessments are historical records.

A claim may move through states such as:

```text
Unclear
   ↓
Supported
   ↓
Unclear
   ↓
Partially supported
```

Each assessment should remain available as historical information.

The current claim status provides a convenient current representation, while `claim_assessments` provides the audit history.

A new assessment should normally be appended rather than replacing the previous assessment.

---

## 10. Human and AI Roles

Different processing stages may eventually have different actors.

Possible actors include:

```text
rule
ai
human
hybrid
```

AI may produce:

* extraction results;
* matching proposals;
* evidence suggestions;
* assessment proposals.

Human review may accept, reject, or modify those proposals.

The system should preserve who performed an assessment and in what role.

---

## 11. Failure and Uncertainty

The pipeline must be able to stop or defer a decision when available information is insufficient.

Examples:

```text
Article
   ↓
Story Matching
   ↓
REVIEW
```

or:

```text
Claim
   ↓
Conflicting Evidence
   ↓
UNCLEAR
```

This is preferable to forcing a false sense of certainty.

Uncertainty is a valid system state.

---

## 12. Reprocessing

Pipeline stages should eventually be designed so that previously processed information can be re-evaluated.

For example, a future improvement to Story Matching should be able to compare its results against previous results without destroying the historical record.

This is especially important when introducing:

* new matching algorithms;
* embeddings;
* LLMs;
* improved extraction models;
* new provenance rules.

The system should favor reproducible processing and historical traceability.

---

## 13. Implementation Status

The roadmap is the single source of truth for completed, active, planned, and
blocked stages, including stage priorities and acceptance criteria. This
document describes the pipeline behavior and should not maintain a second
project schedule.

---

## 14. Pipeline Invariant

The central invariant of the system is:

> Every important derived conclusion should remain traceable to the information and relationships from which it was derived.

If a future implementation makes a result easier to produce but harder to trace, the architectural consequences must be considered before adopting it.
