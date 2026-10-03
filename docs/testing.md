# Testing and Validation

## 1. Purpose

This document records the validation performed on the News Intelligence data model and its current analytical views.

The purpose is to preserve:

* what was tested;
* why it was tested;
* what the test demonstrated;
* what conclusions are justified;
* and what conclusions are not justified.

A successful test demonstrates a specific behavior.

It does not automatically validate the entire architecture.

---

# 2. Testing Principles

## Reproducibility

Important tests should eventually be reproducible from the repository.

## Separation of Real and Synthetic Data

Real-world examples and synthetic test records must remain clearly distinguishable.

Synthetic records exist to test system behavior.

They are not evidence about the real world.

## Test the Model, Not Just the SQL

A query returning rows is not sufficient.

Tests should verify that the returned relationships represent the intended domain meaning.

## Preserve Historical Behavior

When testing assessment changes, the previous assessment must remain available.

## Do Not Infer More Than the Test Demonstrates

For example:

```text
2 evidence records
    ≠
2 independent confirmations
```

unless provenance independently establishes that distinction.

---

# 3. Database Schema Validation

The database tables were created and tested in PostgreSQL.

The model was validated incrementally rather than creating the complete schema without testing.

The validated domain includes:

```text
sources
source_policies
source_feeds
articles
stories
article_stories
claims
claim_sources
evidence
claim_evidence
evidence_sources
article_evidence
claim_assessments
```

The foreign-key relationships and relevant constraints were tested through actual inserts and queries.

---

# 4. Real-World Validation: LZ Dark Matter Story

A real-world news example was used to test the relationship between:

* a news article;
* a story;
* a claim;
* underlying research evidence;
* evidence provenance;
* assessment.

## 4.1 Reuters Article

Source:

```text
Reuters
```

Article:

```text
Scientists make potential breakthrough in search for dark matter
```

Published:

```text
2026-09-01
```

The article was associated with the dark matter story.

## 4.2 Story

Story:

```text
Potential signal in the search for dark matter
```

The story was classified as:

```text
developing_story
```

## 4.3 Claim

Claim:

```text
Researchers reported a potential signal consistent with dark matter in the experiment.
```

Claim type:

```text
factual
```

The wording intentionally describes a potential signal rather than treating it as a confirmed discovery.

## 4.4 Evidence

The claim was linked to a Berkeley Lab research report describing the LZ result.

Evidence type:

```text
research_report
```

The evidence provenance records:

```text
LUX-ZEPLIN → producer
Lawrence Berkeley National Laboratory → publisher
```

This demonstrated the distinction between producer and publisher.

## 4.5 Research Paper

A separate research paper was subsequently recorded:

```text
Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment
```

The paper was recorded as:

```text
research_paper
```

Its provenance identifies:

```text
LUX-ZEPLIN → producer
```

The claim was associated with this evidence as supporting evidence.

## 4.6 Assessment

The claim received a human decision assessment:

```text
supported
```

The reasoning recorded that the evidence supports the cautious wording of the claim while the result remains below the threshold for a confirmed discovery.

## 4.7 What This Test Demonstrated

This test demonstrated that the schema can represent:

* an article reporting a story;
* a story containing a claim;
* multiple evidence records associated with the claim;
* evidence with multiple provenance roles;
* an article directly related to evidence;
* historical assessment metadata.

It also demonstrated that:

```text
article source
    ≠
evidence producer
```

---

# 5. Multiple Articles and Shared Evidence

A second real-world article from Imperial College London was associated with the same dark matter story.

The article was linked to the Berkeley Lab research report through:

```text
article_evidence.relationship = based_on
```

This represents that the article was based on that evidence.

The article was also associated with the same story and claim.

## What This Demonstrated

The model can represent multiple articles covering the same story while retaining their individual evidence relationships.

It also demonstrated why article count alone cannot be used as a measure of independent confirmation.

---

# 6. Important Provenance Correction

The research paper and the Berkeley Lab announcement were deliberately kept as separate evidence records.

The current model does **not** assume an evidence-to-evidence relationship between them.

The reason is temporal and evidentiary:

* the Berkeley Lab announcement was published on September 1, 2026;
* the recorded research paper was submitted on September 2, 2026.

Therefore the current data does not establish that the September 1 announcement was derived from the September 2 paper.

Both may represent the same underlying research result, but that relationship has not been established in the current model.

This is an example of a rule used throughout the project:

> Do not create a provenance relationship merely because two records appear related.

---

# 7. Synthetic Conflict Test

Synthetic records were created to test conflicting evidence.

These records are explicitly test data.

## Claim

Synthetic claim:

```text
The test subject completed the experiment successfully.
```

## Initial Evidence

Two evidence records were created:

```text
Evidence A → supports
Evidence B → contradicts
```

The claim was initially assessed as:

```text
unclear
```

with reasoning that the available evidence directly conflicted.

## Later Evidence

A third evidence record was introduced:

```text
Evidence C → supports
```

The record represented an original experiment document.

A new assessment was recorded:

```text
supported
```

The earlier `unclear` assessment remained in the database.

## What This Demonstrated

The test validated the distinction between:

```text
current claim status
```

and:

```text
historical assessment records
```

It also demonstrated that new evidence can lead to a later assessment without deleting the earlier assessment.

---

# 8. Synthetic Shared-Source Test

Synthetic records were used to model a situation where multiple news articles report the same underlying source.

Conceptually:

```text
Reuters article ──┐
                  ├──→ same underlying evidence
AP article ───────┘
```

The articles were associated with the same evidence item.

The evidence had a registered provenance relationship representing its underlying source.

## What This Demonstrated

The model can represent:

```text
multiple articles
        ↓
one underlying evidence item
```

Therefore the system does not have to treat repeated reporting as independent confirmation.

---

# 9. Synthetic Independent Evidence Test

A separate synthetic evidence item was introduced to represent an independent record.

This allowed the system to distinguish:

```text
shared evidence
```

from:

```text
separate evidence records
```

However, the existence of different source IDs alone is not treated as proof of independence.

Independence is a provenance and relationship question, not merely a counting operation.

---

# 10. `claim_intelligence` View

The `claim_intelligence` view was created and tested.

It combines information from:

* stories;
* claims;
* evidence;
* claim-evidence relationships;
* evidence provenance;
* latest assessment.

For Claim 3, the view produced multiple rows because one evidence item had multiple provenance relationships.

This is expected behavior.

The view is therefore useful for detailed inspection, but it is not a one-row-per-claim summary.

---

# 11. `claim_overview` View

The `claim_overview` view was created and tested.

For Claim 3, the current result included:

```text
evidence_count = 2
producer_count = 1
publisher_count = 1
```

This correctly demonstrates that two evidence records do not necessarily represent two different producers.

For Claim 4, the synthetic test produced:

```text
evidence_count = 4
producer_count = 1
```

Again, these values describe recorded relationships.

They are not trust scores or automatic independence measurements.

---

# 12. `claim_evidence_conflicts` View

The conflict view was created and tested.

For the synthetic conflict claim, it returned:

```text
supporting_evidence_count = 3
contradicting_evidence_count = 1
claim_status = supported
```

The view does not determine that the claim is correct.

It only identifies that both supporting and contradicting evidence have been recorded.

The final status resulted from a separate assessment process.

---

# 13. Historical Assessment Test

The synthetic conflict claim currently has at least two historical assessment records:

```text
Assessment 1
status = unclear
actor = human
role = decision
```

followed by:

```text
Assessment 2
status = supported
actor = human
role = decision
```

The first assessment was not modified or deleted.

This validates the append-oriented historical assessment model.

---

# 14. Current Validation Conclusions

The current tests establish that the database model can represent:

1. multiple sources;
2. source policies;
3. source feeds;
4. articles;
5. stories;
6. article-story relationships;
7. claims;
8. claim-source relationships;
9. evidence;
10. claim-evidence relationships;
11. evidence provenance;
12. article-evidence relationships;
13. historical assessments;
14. conflicting evidence;
15. shared underlying evidence;
16. multiple evidence records;
17. current claim status;
18. analytical views over these relationships.

The tests do **not** establish that:

* the current model is complete;
* source reliability can be automatically determined;
* evidence independence can always be automatically determined;
* claim assessments can be fully automated;
* AI will outperform deterministic methods;
* the current story-matching approach is sufficient.

Those questions remain future engineering and validation tasks.

---

# 15. Future Testing

Future tests should cover at least:

### Ingestion

* malformed feeds;
* duplicate URLs;
* missing publication dates;
* invalid metadata;
* unavailable content.

### Deduplication

* exact duplicates;
* URL variations;
* syndicated articles;
* substantially similar articles;
* unrelated articles with similar titles.

### Story Matching

* clear match;
* clear new story;
* ambiguous match;
* related but distinct events.

Expected decision classes:

```text
MATCH
NEW_STORY
REVIEW
```

### Claims

* factual claims;
* quotations;
* attributions;
* predictions;
* opinions;
* statistical claims.

### Evidence

* supporting evidence;
* contradicting evidence;
* contextual evidence;
* incomplete evidence;
* multiple evidence records;
* shared evidence.

### Provenance

* direct producer;
* publisher;
* issuer;
* derived reporting;
* shared underlying source;
* uncertain provenance.

### Assessments

* initial assessment;
* review;
* decision;
* changed assessment;
* conflicting evidence;
* insufficient evidence.

---

# 16. Testing Policy

Every major processing capability should have:

1. a reproducible test;
2. a documented expected result;
3. a clear distinction between real and synthetic data;
4. a record of important limitations.

When a test reveals that the current model cannot represent a requirement, that limitation should be documented before changing the schema.
