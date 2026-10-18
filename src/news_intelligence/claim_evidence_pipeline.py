def trace_claim_provenance(claim: dict, supporting_evidence: list[dict], provenance_links: list[dict]) -> dict:
    """
    Trace a claim through its supporting/contradicting evidence and provenance links
    to ensure provenance separation and traceability.

    Args:
        claim: dict containing claim details (id, text, type, status, story_id).
        supporting_evidence: list of dicts representing evidence items linked to the claim.
        provenance_links: list of dicts representing evidence_sources mapping evidence to sources with roles (producer, publisher, etc.).

    Returns:
        A structured traceability trace dict preserving provenance roles.
    """
    claim_id = claim.get("id")
    claim_text = claim.get("claim_text")

    if claim_id is None or not claim_text:
        raise ValueError("Claim must have an id and claim_text")

    traced_evidence = []

    # Map provenance by evidence_id
    prov_map = {}
    for link in provenance_links:
        ev_id = link.get("evidence_id")
        if ev_id not in prov_map:
            prov_map[ev_id] = []
        prov_map[ev_id].append({
            "source_id": link.get("source_id"),
            "source_name": link.get("source_name"),
            "relationship": link.get("relationship"),  # e.g., 'producer', 'publisher', 'issuer'
        })

    for ev in supporting_evidence:
        ev_id = ev.get("id")
        ev_sources = prov_map.get(ev_id, [])

        # Separate producers/issuers from mere publishers
        producers = [s for s in ev_sources if s["relationship"] in {"producer", "issuer"}]
        publishers = [s for s in ev_sources if s["relationship"] == "publisher"]
        observers = [s for s in ev_sources if s["relationship"] in {"participant", "author", "other"}]

        traced_evidence.append({
            "evidence_id": ev_id,
            "evidence_title": ev.get("title"),
            "evidence_type": ev.get("type"),
            "relationship": ev.get("relationship", "supports"),  # supports/contradicts/context
            "producers_or_issuers": producers,
            "publishers": publishers,
            "other_roles": observers,
            "has_producer_or_issuer": bool(producers),
        })

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "claim_type": claim.get("claim_type", "factual"),
        "claim_status": claim.get("status", "unverified"),
        "evidence_chain": traced_evidence,
        "traceable": bool(traced_evidence) and all(
            item["producers_or_issuers"] or item["publishers"] or item["other_roles"]
            for item in traced_evidence
        ),
    }
