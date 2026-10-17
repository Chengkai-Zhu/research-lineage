"""Gate host-authored candidates; this module does not extract or certify claims."""

from .contract import RELATIONS, safe_url
from .core import MapError


def assess(candidate):
    if not isinstance(candidate, dict) or not isinstance(candidate.get("id"), str):
        raise MapError("Each extraction candidate needs a string id.")
    kind = candidate.get("type")
    if kind not in ("result", *RELATIONS):
        raise MapError(
            "Candidate type must be result or a supported relationship type."
        )
    reasons = []
    source, evidence = candidate.get("source", {}), candidate.get("evidence", {})
    if not isinstance(source, dict) or not isinstance(evidence, dict):
        raise MapError("Candidate source and evidence must be objects.")
    access = source.get("access")
    if access not in ("full_text", "abstract"):
        reasons.append("Readable source text is unavailable; metadata is insufficient.")
    if not isinstance(candidate.get("claim"), str) or not candidate["claim"].strip():
        reasons.append("A concrete source-grounded claim is required.")
    if not isinstance(evidence.get("locator"), str) or not evidence["locator"].strip():
        reasons.append("A source locator is required.")
    for key in ("work_id", "version_id", "url"):
        if (
            not isinstance(source.get(key), str)
            or not source[key].strip()
            or source.get(key) != evidence.get(key)
        ):
            reasons.append(f"Evidence must match the exact source {key}.")
    if not isinstance(source.get("url"), str) or not safe_url(source["url"]):
        reasons.append("A safe pinned source URL is required.")
    if kind != "result":
        basis = candidate.get("basis")
        if basis not in ("citation_only", "author_explicit", "editorial_inference"):
            reasons.append("Declare how the proposed relationship is supported.")
        if basis == "citation_only" and kind != "cites":
            reasons.append("A citation cannot support a semantic relationship.")
    if kind == "improves_bound":
        comparison = candidate.get("comparison", {})
        if not isinstance(comparison, dict):
            raise MapError("Comparison must be an object.")
        left, right = comparison.get("left", {}), comparison.get("right", {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            raise MapError("Comparison sides must be objects.")
        fields = ("input", "assumptions", "cost", "error", "cost_unit")
        if comparison.get("comparability") != "comparable" or any(
            not isinstance(side.get(key), str) or not side[key].strip()
            for side in (left, right)
            for key in fields
        ):
            reasons.append(
                "A bound improvement needs explicit comparable settings and cost units."
            )
        if left.get("cost_unit") != right.get("cost_unit"):
            reasons.append(
                "Different cost units require a justified conversion before comparison."
            )
        if access != "full_text":
            reasons.append("A bound improvement requires full-text evidence.")
    return {
        "id": candidate["id"],
        "type": kind,
        "decision": "abstain" if reasons else "propose",
        "reasons": reasons,
        "review_status": "proposed",
        "source_access": access,
        "meaning": "Evidence gate only; a proposal is not an accepted scientific claim.",
    }
