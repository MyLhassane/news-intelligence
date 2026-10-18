from datetime import datetime, timezone

VALID_ACTOR_TYPES = {"human", "ai", "rule", "hybrid"}
VALID_ASSESSMENT_ROLES = {"proposal", "review", "decision"}
VALID_ASSESSMENT_STATUSES = {"supported", "partially_supported", "contradicted", "unclear"}


def create_assessment(
    claim_id: int,
    assessment_status: str,
    actor_type: str,
    actor_name: str | None = None,
    reasoning: str | None = None,
    assessment_role: str = "proposal",
    existing_assessments: list[dict] | None = None,
) -> tuple[dict, list[dict]]:
    """
    Create a new reviewable assessment for a claim, ensuring append-only history
    without silently overwriting prior evaluations.

    Args:
        claim_id: int identifying the target claim.
        assessment_status: str ('supported', 'partially_supported', 'contradicted', 'unclear').
        actor_type: str ('human', 'ai', 'rule', 'hybrid').
        actor_name: optional str identifying the specific actor.
        reasoning: optional str explaining the assessment rationale.
        assessment_role: str ('proposal', 'review', 'decision').
        existing_assessments: optional list of prior assessment dicts for this claim.

    Returns:
        A tuple of (new_assessment_dict, updated_full_assessment_history_list).
    """
    if actor_type not in VALID_ACTOR_TYPES:
        raise ValueError(f"Invalid actor_type '{actor_type}'. Must be one of {VALID_ACTOR_TYPES}")

    if assessment_role not in VALID_ASSESSMENT_ROLES:
        raise ValueError(f"Invalid assessment_role '{assessment_role}'. Must be one of {VALID_ASSESSMENT_ROLES}")

    if assessment_status not in VALID_ASSESSMENT_STATUSES:
        raise ValueError(f"Invalid assessment_status '{assessment_status}'. Must be one of {VALID_ASSESSMENT_STATUSES}")

    if not claim_id:
        raise ValueError("claim_id must be provided")

    history = list(existing_assessments) if existing_assessments else []
    next_id = max((item.get("id", 0) for item in history), default=0) + 1

    new_assessment = {
        "id": next_id,
        "claim_id": claim_id,
        "assessment_status": assessment_status,
        "actor_type": actor_type,
        "actor_name": actor_name,
        "reasoning": reasoning,
        "assessment_role": assessment_role,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Append-only history rule: never overwrite prior history
    history.append(new_assessment)

    return new_assessment, history
