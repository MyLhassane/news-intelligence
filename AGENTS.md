# Agent Instructions

This file defines the operating rules for AI agents working on the News Intelligence project.

## 1. Read Before Changing

Before making a substantive change, read:

* `README.md`
* the relevant document under `docs/`
* the relevant database schema or source code

Do not assume the architecture from conversation history alone.

The repository documentation is part of the project's persistent memory.

## 2. Preserve the Architecture

Do not redesign the system casually.

The core conceptual pipeline is:

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

Changes to this architecture must have a documented reason.

If a change affects a fundamental architectural decision, update `docs/decisions.md`.

## 3. Database Changes

Do not add a table or column simply because it may be useful in the future.

Before changing the schema:

1. Identify the requirement.
2. Inspect the existing schema.
3. Determine whether the requirement can already be represented.
4. Demonstrate the limitation if it cannot.
5. Make the smallest necessary change.
6. Update the schema documentation.
7. Add or update tests.

Database structure is part of the architecture, not an implementation detail.

## 4. Provenance

Preserve the chain between information and its origin.

Do not assume:

* multiple articles = multiple independent sources;
* multiple sources = multiple independent evidence items;
* a publisher = the producer of the underlying evidence;
* an article's source = the source of every claim mentioned in the article.

When information originates from another source, represent that relationship explicitly when possible.

## 5. Claims

Claims must not automatically be treated as facts.

The database distinguishes claim types such as:

* factual
* quote
* attribution
* prediction
* opinion
* statistical
* other

Do not apply factual verification logic indiscriminately to opinions or predictions.

## 6. Evidence

Evidence relationships describe how evidence relates to a claim.

The presence of supporting and contradicting evidence does not automatically determine the final claim status.

In particular:

* absence of evidence is not automatically contradiction;
* conflicting evidence requires evaluation;
* repeated reporting does not automatically strengthen independence;
* provenance must be considered before counting confirmations.

## 7. Assessments

`claim_assessments` is historical.

Never silently overwrite historical assessments.

A new evaluation should normally be recorded as a new assessment.

The distinction between these concepts must be preserved:

```text
claim.status
    = current quick status

claim_assessments
    = historical assessment record
```

Assessment roles currently include:

* `proposal`
* `review`
* `decision`

AI may produce a proposal.

A human may review or make a decision.

The system must not assume that AI output is a final decision.

## 8. AI Usage

AI is a processing mechanism, not the source of truth.

AI may be used for:

* extraction;
* classification;
* summarization;
* story matching;
* claim identification;
* evidence identification;
* assessment proposals.

AI output must remain distinguishable from human decisions and deterministic rules.

Do not introduce AI merely because it is available.

Prefer a deterministic baseline when one can reasonably be established.

## 9. Prototypes vs Production

Clearly distinguish:

* Production
* Test
* Prototype
* Documentation

Prototype code must not silently become production code.

A prototype may demonstrate an idea without being integrated into the system.

When promoting a prototype into production, review its design against the current architecture rather than copying it blindly.

## 10. Testing

A change is not complete merely because the code runs.

Tests should demonstrate the behavior that matters.

Database behavior that has previously been validated should remain reproducible where practical.

Synthetic test data must be clearly identified as synthetic and must never be presented as real-world evidence.

## 11. Documentation

When a change affects:

* architecture;
* database structure;
* pipeline behavior;
* testing methodology;
* project direction;

update the corresponding documentation.

Do not allow the implementation to become more current than the project documentation.

## 12. Small Changes

Prefer small, understandable changes.

For each meaningful change, be able to explain:

* what changed;
* why it changed;
* what was tested;
* what remains unresolved.

Avoid unrelated cleanup during feature work unless explicitly requested.

## 13. Data Safety

Do not delete, overwrite, or transform user data or database records without an explicit reason and a safe procedure.

Database migrations must be deliberate and reproducible.

Never place passwords, API keys, tokens, or other secrets in the repository.

## 14. Source Classification

Source types describe institutional or functional roles.

They must not be interpreted as automatic trust scores.

Do not introduce simplistic source-ranking logic unless explicitly designed, documented, and justified.

## 15. Decision Authority

The agent may:

* inspect;
* analyze;
* propose;
* implement an agreed change;
* run tests;
* document results.

The agent must not silently make major architectural decisions on behalf of the project.

When a change requires a project-level decision, document the issue and the reasoning.

## 16. Repository Memory

The repository is the persistent project memory.

Important knowledge should not exist only in an AI conversation.

When a decision becomes important enough that a future developer or agent needs to know it, record it in the appropriate documentation.
