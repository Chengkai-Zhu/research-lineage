"""Non-mutating source-version availability and update proposals."""

from datetime import date

from .core import diff_maps


def update_proposal(before, after, as_of):
    as_of = date.fromisoformat(as_of).isoformat()
    changes = diff_maps(before, after)
    versions = {v["id"]: v for w in after["works"] for v in w["versions"]}
    evidence = {e["id"]: e for e in after["evidence"]}
    eligible, excluded = [], []
    for result in after["results"]:
        used = {result["version_id"]} | {
            evidence[e]["version_id"] for e in result["evidence"]
        }
        later = sorted(v for v in used if versions[v]["published"] > as_of)
        if later:
            excluded.append(
                {
                    "id": result["id"],
                    "reason": "cited_version_after_cutoff",
                    "versions": later,
                }
            )
        else:
            eligible.append(result["id"])
    relations, conflicts = [], []
    for relation in after["relations"]:
        if relation["source"] not in eligible or relation["target"] not in eligible:
            conflicts.append(
                {"id": relation["id"], "reason": "endpoint_unavailable_at_cutoff"}
            )
        elif any(
            versions[evidence[e]["version_id"]]["published"] > as_of
            for e in relation["evidence"]
        ):
            conflicts.append(
                {"id": relation["id"], "reason": "relationship_evidence_after_cutoff"}
            )
        else:
            relations.append(relation["id"])
    if as_of > after["scope"]["cutoff"]:
        conflicts.append(
            {"id": after["id"], "reason": "requested_date_exceeds_recorded_coverage"}
        )
    late_checks = [e["id"] for e in after["evidence"] if e["checked"] > as_of]
    return {
        "as_of": as_of,
        "mode": "source_version_availability",
        "proposal_only": True,
        "historical_reconstruction": "unavailable",
        "explanation": "Publication dates bound source availability, not what a researcher knew. Later checks and unresolved conflicts are retained; no historical knowledge snapshot is certified.",
        "eligible_result_ids": eligible,
        "excluded_results": excluded,
        "eligible_relation_ids": relations,
        "conflicts": conflicts,
        "evidence_checked_later": late_checks,
        "changes": changes,
        "invalidation": "No critique or changed assumption automatically invalidates descendants.",
    }
