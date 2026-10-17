"""Semantic record consistency, without inferring or certifying scientific comparisons."""


def comparison_evidence(record):
    refs = list(record["evidence"])
    for row in record["conditions"]:
        refs.extend(row["left_evidence"] + row["right_evidence"])
    if record["conversion"]:
        refs.extend(record["conversion"]["evidence"])
    return set(refs)


def comparison_errors(record, results, evidence, improvement=False):
    errors = []
    improvement = improvement or record["outcome"] == "improvement"
    left, right = results.get(record["left"]), results.get(record["right"])
    if not left or not right or record["left"] == record["right"]:
        return ["Comparison needs two distinct existing result endpoints."]
    refs = comparison_evidence(record)
    if refs - evidence.keys() or len(set(record["evidence"])) != len(
        record["evidence"]
    ):
        return ["Comparison has missing or duplicate evidence references."]
    if refs - set(record["evidence"]):
        errors.append(
            "Condition/conversion evidence must also appear in comparison evidence."
        )
    assessed = record["assessment"] != "unknown"
    if assessed and record["basis"] == "citation_only":
        errors.append("Citation alone cannot support a comparison assessment.")
    dimensions = [row["dimension"] for row in record["conditions"]]
    if len(set(dimensions)) != len(dimensions):
        errors.append("Comparison condition dimensions must be unique.")
    for side, result in (("left", left), ("right", right)):
        own = {
            eid
            for eid in refs
            if evidence[eid]["work_id"] == result["work_id"]
            and evidence[eid]["version_id"] == result["version_id"]
        }
        if assessed and not own:
            errors.append(f"Comparison needs {side}-endpoint version-bound evidence.")
        for row in record["conditions"]:
            row_refs = row[side + "_evidence"]
            if len(set(row_refs)) != len(row_refs) or any(
                eid not in own for eid in row_refs
            ):
                errors.append(
                    f"Condition {row['dimension']} has wrong {side}-version evidence."
                )
            if assessed and row[side] is not None and not row_refs:
                errors.append(
                    f"Condition {row['dimension']} needs {side}-value evidence."
                )
        if (improvement or record["review_status"] == "reviewed") and not any(
            evidence[eid]["kind"] == "full_text" for eid in own
        ):
            errors.append(
                f"Comparison requires full-text evidence for the {side} version."
            )
    if record["outcome"] == "improvement" and not record["improvement"]:
        errors.append("An improvement outcome needs a specific directional statement.")
    if record["outcome"] != "improvement" and record["improvement"] is not None:
        errors.append("Only an improvement outcome may carry an improvement statement.")
    if record["assessment"] != "comparable" and record["outcome"] != "not_assessed":
        errors.append("An unresolved/incomparable assessment cannot assert an outcome.")
    if assessed and not record["conditions"]:
        errors.append("An assessed comparison needs explicit conditions.")
    if record["review_status"] == "reviewed":
        minimum = 2 if record["outcome"] == "improvement" else 1
        if (
            len({r["url"] for r in record["reviews"]}) < minimum
            or len({r["name"].strip().casefold() for r in record["reviews"]}) < minimum
        ):
            errors.append(
                f"Comparison needs {minimum} distinct recorded review references."
            )
    if improvement:
        errors.extend(improvement_errors(record, left, right))
    return errors


def improvement_errors(record, left, right):
    errors = []
    if record["assessment"] != "comparable" or record["outcome"] != "improvement":
        errors.append(
            "Improvement requires a comparable record and an explicit improvement outcome."
        )
    if any(
        value is None
        for result in (left, right)
        for value in result["settings"].values()
    ):
        errors.append("Improvement requires fully stated result settings.")
    rows = {row["dimension"]: row for row in record["conditions"]}
    for dimension in ("input", "assumptions", "cost", "error"):
        row = rows.get(dimension)
        if not row or any(row[side] is None for side in ("left", "right")):
            errors.append(f"Improvement needs an explicit {dimension} comparison.")
    cost = rows.get("cost")
    if cost:
        if not cost["left_unit"] or not cost["right_unit"]:
            errors.append("Improvement needs explicit cost units for both sides.")
        elif cost["left_unit"] != cost["right_unit"] and not record["conversion"]:
            errors.append(
                "Different cost units require a documented conversion with evidence."
            )
    return errors
