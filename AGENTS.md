# Agent Instructions

This file defines the operating rules and autonomous execution workflow for AI agents working on the News Intelligence project.

The repository is the primary source of project direction and persistent memory. Agents are expected to move the project forward independently within documented constraints, complete one task per execution cycle, and stop for user review before starting another task.

## 1. Read Before Changing

Before substantive work, read:

- `README.md`
- `docs/vision.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/decisions.md`
- `docs/testing.md`
- The relevant documentation under `docs/`
- The relevant source code, tests, and database schema

At the beginning of each execution cycle, inspect the actual repository state, including the current Git branch, working tree, recent commit, and any existing user changes.

Do not assume that the implementation, documentation, or conversation history is fully up to date. Identify relevant discrepancies before proceeding.

The repository is the persistent project memory. Conversation history is supplementary and must not replace repository inspection.

Never overwrite, discard, or incorporate unrelated user changes without authorization.

## 2. Preserve the Architecture

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

Prefer completing and validating existing pipeline stages before introducing new subsystems.

Do not confuse:

- Article deduplication with story matching.
- Repeated reporting with independent corroboration.
- Evidence collection with claim assessment.
- AI-generated proposals with final decisions.

If a change affects a fundamental architectural decision, update `docs/decisions.md` and the relevant architecture documentation.

## 3. Autonomous Execution

The agent is responsible for completing the user's requested task within its stated scope. Do not replace a specific request with a different roadmap task, expand a review or explanation request into implementation, or start follow-up work that was not requested.

When the user explicitly delegates task selection or asks the agent to advance the project without specifying a task, select the next appropriate task from the roadmap. At the beginning of such an execution cycle:

1. Inspect the current repository and Git state.
2. Review the project goals, roadmap, relevant decisions, and existing implementation.
3. Identify incomplete work, demonstrated limitations, and missing validation.
4. Select the highest-priority task that can be completed safely within the existing project direction.
5. Define the task scope and measurable acceptance criteria.

Prioritize work that advances the documented project goals, resolves demonstrated problems, improves correctness, or completes an existing pipeline stage.

Do not invent work merely to increase code, test, or documentation counts.

Do not ask the user to select routine implementation details that can be resolved from the repository, established requirements, and existing architectural decisions.

### Routine Decisions

The agent may independently make routine, reversible implementation decisions within the selected task when they are consistent with documented requirements and architecture.

The agent may independently:

- Choose an appropriate implementation approach.
- Add or modify tests.
- Refactor a small area when necessary for the task.
- Update affected documentation.
- Correct directly related defects.
- Determine whether acceptance criteria have been satisfied.

Do not expand the task into unrelated cleanup or additional roadmap items.

### Restricted Decisions

The agent must not independently make major architectural changes, introduce significant dependencies or external services, perform destructive operations, or modify production data.

When a project-level decision is genuinely necessary, explain the specific issue, available evidence, alternatives, consequences, and recommended option.

Do not stop the entire task because of an uncertainty that does not materially affect its correctness or safety. Continue with independent work where practical.

## 4. One Task Per Execution Cycle

**Complete one independently scoped task per execution cycle, then stop for user review.**

An execution cycle consists of:

1. Selecting one task and defining its acceptance criteria.
2. Inspecting the relevant implementation and tests.
3. Implementing the task.
4. Running the relevant tests and inspecting the results.
5. Updating the affected documentation and roadmap.
6. Reviewing the complete diff and checking the repository state.
7. Delivering the completion report.
8. Stopping and waiting for explicit user authorization before beginning another task.

Do not automatically start the next roadmap item, even when the current task is complete and the next task is obvious.

Do not continue with a second independent task in the same cycle merely because time or context remains.

Implementation, tests, and documentation that are necessary parts of the same coherent task belong to the same execution cycle. Do not artificially split them into separate tasks.

If the task cannot be completed, report the exact stopping point, verified progress, blocker, remaining work, and recommended next action. Update the relevant project documentation when appropriate.

### User Review and Continuation

After completing a task, wait for the user to review the report and authorize continuation.

A request to review, explain, or discuss the completed work does not automatically authorize another implementation task.

After continuation is authorized, inspect the current repository state again. Account for the user's feedback and any intervening changes before selecting or resuming work.

Do not interpret silence, an unfinished report, or the existence of a roadmap item as authorization to continue.

## 5. Task Completion and Reporting

A task is complete only when its acceptance criteria have been evaluated and the required implementation, validation, and documentation work has been performed.

At the end of each execution cycle, provide one concise, factual report containing:

1. **Task:** What was selected and why.
2. **Changes:** Which files changed and the purpose of each change.
3. **Validation:** Commands actually executed and their observed results.
4. **Documentation:** Which documents were updated.
5. **Acceptance criteria:** Which criteria passed, failed, or remain unverified.
6. **Risks and blockers:** Any unresolved issues or limitations.
7. **Next task:** The recommended next task and its acceptance criteria.

Clearly distinguish verified facts from assumptions and recommendations.

Never claim that a test, command, database operation, commit, or push succeeded unless its result was actually observed.

Do not report a task as complete merely because the code was written or the documentation was updated.

## 6. Database Changes

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

Never use the production `news` database for integration tests. Use `news_test` only.

Verify the actual connected database before performing test operations. Do not rely solely on a configured connection string when a connection can be inspected.

Database migrations must be deliberate, reproducible, and appropriate to the current project stage.

Do not modify production data or perform production-impacting operations without explicit authorization and an appropriate safety procedure.

## 7. Provenance

Preserve the information's origin and distinguish article, evidence, and
source roles. Never infer independence from article, source, or evidence
counts, or infer that an article's publisher produced all evidence it reports.
Follow the provenance model in `docs/architecture.md`, the implemented
relationships in `docs/database-schema.md`, and the rationale in ADR-001 and
ADR-002 of `docs/decisions.md`. Do not discard provenance merely to simplify
a pipeline stage.

## 8. Claims

Preserve a claim's type, source wording, and uncertainty. Do not treat a quote
or attribution as proof that the quoted or attributed statement is true, or
apply factual verification indiscriminately. See the domain contract in
`docs/architecture.md` and current supported types in
`docs/database-schema.md`.

## 9. Evidence

Record how evidence relates to a claim; do not derive a final claim status
from supporting or contradicting links alone. Distinguish direct evidence from
context, and preserve uncertainty. Follow the rationale in ADR-004 and ADR-015
of `docs/decisions.md` and the relationship contract in `docs/pipeline.md`.

## 10. Assessments

Preserve assessment history: append a new evaluation rather than silently
overwriting an earlier one. Keep current claim status distinct from historical
assessments, and do not treat an AI proposal as a human decision. The
authoritative fields and roles are in `docs/database-schema.md`; rationale is
in ADR-005 and ADR-006 of `docs/decisions.md`.

## 11. AI Usage

Treat AI as a processing mechanism, not a source of truth. Keep its outputs
distinguishable from source material, deterministic results, and human
decisions. Use it only for a demonstrated need and compare it with an
appropriate baseline. Follow ADR-006 and ADR-007 in `docs/decisions.md`.

## 12. Prototypes vs Production

Clearly distinguish:

- Production
- Test
- Prototype
- Documentation

Prototype code must not silently become production code.

A prototype may demonstrate an idea without being integrated into the system.

When promoting a prototype into production, review its design against the current architecture rather than copying it blindly.

Document the status and limitations of experimental components where future agents or developers could otherwise mistake them for implemented production behavior.

## 13. Testing

A change is not complete merely because the code runs.

Tests should demonstrate the behavior that matters and cover relevant failure conditions where practical.

Database behavior that has previously been validated should remain reproducible where practical.

Synthetic test data must be clearly identified as synthetic and must never be presented as real-world evidence.

Use the existing test framework and project conventions unless a demonstrated limitation justifies a change.

Run the tests relevant to the task. Run broader suites when the scope or risk warrants it.

Report the exact commands executed and observed results. Clearly identify tests that were not run, could not run, or remain unverified.

Never use production `news` for integration testing.

## 14. Documentation

When a change affects any of the following, update the corresponding documentation:

- Architecture.
- Database structure.
- Pipeline behavior.
- Testing methodology.
- Project direction.
- Implementation status.
- Significant technical decisions.

### Documentation Ownership

Each document has one authoritative subject. Treat the implementation and canonical SQL as the facts about what exists; use the document below as the maintained explanation for its subject. Other documents should link to that authority instead of copying its status, lists, commands, results, or detailed content.

| Subject | Authoritative file | Keep here |
|---|---|---|
| Project purpose, long-term goals, and non-goals | `docs/vision.md` | Why the project exists and what success means |
| Conceptual architecture and domain boundaries | `docs/architecture.md` | Core concepts, invariants, and relationships |
| Actual database structure and constraints | `database/schema.sql`, `database/views.sql`; explained in `docs/database-schema.md` | Canonical SQL is structural truth; the document explains its meaning and change policy |
| Rationale and history of technical choices | `docs/decisions.md` | Accepted, superseded, or reconsidered decisions and why |
| Pipeline stage contracts and implemented behavior | `docs/pipeline.md` | Inputs, outputs, rules, failure behavior, and what is or is not integrated |
| Current project state, active stage, priorities, and acceptance criteria | `docs/roadmap.md` | The single source for what work is current, next, complete, or blocked |
| Test commands, scope, safeguards, and observed results | `docs/testing.md` | Reproducible test procedures and results actually observed |
| Project entry point and navigation | `README.md` | Brief introduction and links; no second copy of current status or test results |
| Agent operating rules and this ownership policy | `AGENTS.md` | How to work and keep the repository documentation coherent |

### Update and Cross-Reference Rules

1. Before changing documentation, identify which authoritative subject changed using the table above.
2. Update that authoritative document when the underlying facts change. Update another document only to remove stale duplicated text or replace it with a link/reference.
3. A source utility or test alone does not make a pipeline stage complete. Confirm integration and acceptance criteria from `docs/roadmap.md` before changing stage status.
4. Record test counts and pass/fail claims only in `docs/testing.md`, together with the commands and observed result. Other files may link to that record but must not maintain separate totals.
5. Keep `README.md` as navigation. Do not copy the roadmap, pipeline specification, schema description, or test report into it.
6. If two documents disagree, inspect the implementation, tests, or canonical SQL as applicable; correct the authoritative document, then replace stale copies with references. Do not resolve a contradiction by adding another copy.
7. Before finishing a task, check the affected documents and all inbound references for stale claims, duplicated facts, and broken paths. Do not update unrelated documents merely to make them appear current.

Keep the roadmap aligned with the actual state of the implementation.

Distinguish completed, in-progress, planned, and blocked work.

Do not mark a feature as implemented merely because a utility, prototype, or test exists. Verify whether it is integrated into the intended pipeline.

When an implementation is incomplete, document what remains and the next actionable step.

Do not create duplicate documentation when an existing document can be updated clearly.

## 15. Small Changes

Prefer small, understandable, reviewable changes.

Each task should have a coherent scope and explicit acceptance criteria.

For each meaningful change, be able to explain:

- What changed.
- Why it changed.
- What was tested.
- What remains unresolved.

Avoid unrelated cleanup during feature work unless explicitly requested or essential to complete the task safely.

Do not bundle independent roadmap items into one execution cycle.

A small task is not necessarily a valuable task. Prioritize demonstrated project needs over superficial changes.

## 16. Data Safety

Do not delete, overwrite, or transform user data or database records without an explicit reason and a safe procedure.

Database migrations must be deliberate and reproducible.

Never place passwords, API keys, tokens, or other secrets in the repository.

Do not expose secrets in logs, reports, test fixtures, or documentation.

Preserve existing user changes and unrelated working-tree modifications.

Before any potentially destructive operation, identify what could be affected and obtain the required authorization.

## 17. Source Classification

Source types describe institutional or functional roles.

They must not be interpreted as automatic trust scores.

Do not introduce simplistic source-ranking logic unless explicitly designed, documented, and justified.

Source reliability, factual accuracy, neutrality, independence, and relevance are distinct properties. Do not collapse them into a single score without an explicit, defensible methodology.

Do not infer the reliability of a specific claim solely from the institutional category of its publisher.

## 18. Decision Authority

The agent is expected to exercise independent judgment within the project's documented goals and constraints.

The agent may independently:

- Inspect and analyze the repository.
- Select and prioritize a routine implementation task.
- Implement changes consistent with existing architectural decisions.
- Add and run tests.
- Update documentation and the roadmap.
- Identify risks, limitations, and follow-up work.
- Recommend the next task based on verified project state.

Routine implementation decisions within the selected task do not require separate user approval when they are reversible, adequately tested, and consistent with documented requirements.

The agent must not silently make major architectural decisions, perform restricted destructive operations, modify production data, or introduce significant external dependencies or services.

When a genuine project-level decision is necessary, explain the evidence, alternatives, trade-offs, and recommended option. Stop at that decision boundary when proceeding would require unauthorized action.

The user retains control over task-to-task continuation: complete one execution cycle, deliver the report, and wait for explicit authorization before starting another task. This limit applies even when autonomous task selection has been delegated.

## 19. Repository Memory

The repository is the persistent project memory.

Important knowledge should not exist only in an AI conversation.

When a decision becomes important enough that a future developer or agent needs to know it, record it in the appropriate documentation.

Keep the roadmap, implementation, tests, architecture documentation, and decision records consistent with the verified project state.

At the end of each execution cycle, leave the repository in a state that another agent can inspect and understand without reconstructing the entire conversation history.

Do not commit or push changes unless explicitly authorized by the user or by an established repository policy.

The final report must distinguish local changes, committed changes, and pushed changes accurately.
