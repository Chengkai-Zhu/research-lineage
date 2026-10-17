"""Conservative bibliographic identity: identifiers group; titles never merge."""

import re
from urllib.parse import unquote, urlsplit

from .core import MapError


def identifiers(value):
    value = unquote(value.strip())
    doi = re.fullmatch(
        r"(?:https?://(?:dx\.)?doi\.org/|doi:\s*)?(10\.\d{4,9}/\S+)", value, re.I
    )
    arxiv = re.fullmatch(
        r"(?:https?://(?:www\.)?arxiv\.org/(?:abs|pdf)/|arxiv:\s*)?"
        r"((?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7}))(v[1-9]\d*)?(?:\.pdf)?",
        value,
        re.I,
    )
    if doi:
        return {"doi": doi[1].lower()}
    if arxiv:
        return {"arxiv": arxiv[1].lower(), "version": arxiv[2] or None}
    return {}


def record_ids(record):
    found = {}
    for key in ("doi", "arxiv"):
        value = record.get(key)
        if value:
            parsed = identifiers(str(value))
            if key not in parsed:
                raise MapError(
                    f"Invalid {key} identifier in record {record.get('id')!r}."
                )
            found.update(parsed)
    version = record.get("version")
    if version is not None:
        if (
            "arxiv" not in found
            or not isinstance(version, str)
            or not re.fullmatch(r"v[1-9]\d*", version)
        ):
            raise MapError(
                "A separate version needs an arXiv identity and a vN revision."
            )
        if found.get("version") not in (None, version):
            raise MapError("Embedded and separate arXiv revisions disagree.")
        found["version"] = version
    return found


def reconcile(records):
    if not isinstance(records, list) or len(records) > 250:
        raise MapError("Identity input must be a list of at most 250 records.")
    groups, conflicts, seen = [], [], set()
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise MapError("Each identity record needs a string id.")
        if record["id"] in seen:
            raise MapError("Identity record IDs must be unique.")
        seen.add(record["id"])
        ids = record_ids(record)
        candidates = []
        for group in groups:
            shared = any(
                ids.get(k) and ids[k] == old.get(k)
                for old in group["identifiers"]
                for k in ("doi", "arxiv")
            )
            if not shared:
                continue
            conflict = any(
                ids.get(k) and old.get(k) and ids[k] != old[k]
                for old in group["identifiers"]
                for k in ("doi", "arxiv")
            )
            if conflict:
                conflicts.append(
                    {
                        "record": record["id"],
                        "with": group["records"],
                        "reason": "Shared identifier with contradictory DOI/arXiv identity.",
                    }
                )
            else:
                candidates.append(group)
        if len(candidates) == 1 and not any(
            c["record"] == record["id"] for c in conflicts
        ):
            group = candidates[0]
            group["records"].append(record["id"])
            group["identifiers"].append(ids)
        else:
            if len(candidates) > 1:
                conflicts.append(
                    {
                        "record": record["id"],
                        "with": [g["records"] for g in candidates],
                        "reason": "Identifier bridge requires manual reconciliation.",
                    }
                )
            groups.append({"records": [record["id"]], "identifiers": [ids]})
    return {
        "groups": groups,
        "conflicts": conflicts,
        "input_records": records,
        "policy": "Grouping proposal only. Titles do not establish identity; versions are retained.",
    }


def seed_kind(value):
    if identifiers(value):
        return "paper"
    parsed = urlsplit(value)
    return (
        "paper"
        if parsed.scheme in ("http", "https") or value.lower().endswith(".pdf")
        else "topic"
    )
