"""Single source of truth for the public JSON Schema and runtime validation."""

import re
from datetime import date
from urllib.parse import urlsplit


def text(limit=4000):
    return {"type": "string", "minLength": 1, "maxLength": limit}


def choice(*values):
    return {"type": "string", "enum": list(values)}


def array(item, minimum=0, maximum=500):
    return {"type": "array", "items": item, "minItems": minimum, "maxItems": maximum}


def obj(**properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


ID = {**text(64), "pattern": r"^[a-z0-9][a-z0-9-]*$"}
DATE = {"type": "string", "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
URL = {**text(2048), "format": "uri"}
STATUS = choice("proposed", "reviewed")
REVIEWS = array(obj(name=text(100), url=URL), maximum=20)
SETTINGS = obj(
    **{
        key: {"type": ["string", "null"], "minLength": 1, "maxLength": 2000}
        for key in ("input", "assumptions", "cost", "error")
    }
)
RELATIONS = (
    "generalizes",
    "uses_result",
    "improves_bound",
    "simplifies",
    "surveys",
    "critiques",
    "refutes_claim",
    "addresses",
    "independent_parallel",
    "empirically_checks",
    "cites",
)
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/Chengkai-Zhu/research-lineage/schema/map-v1.json",
    "title": "Research Lineage map v1",
    **obj(
        schema_version=choice("1.0"),
        id=ID,
        title=text(180),
        question=text(500),
        scope=obj(
            summary=text(),
            cutoff=DATE,
            coverage=text(),
            search_strategy=text(),
            exclusions=array(text()),
            gaps=array(text(), minimum=1),
        ),
        lanes=array(
            obj(
                id=ID,
                label=text(80),
                color=choice("teal", "blue", "amber", "rose", "violet"),
            ),
            1,
            8,
        ),
        works=array(
            obj(
                id=ID,
                title=text(500),
                authors=array(text(120), 1, 100),
                first_published=DATE,
                versions=array(
                    obj(id=ID, label=text(100), published=DATE, url=URL), 1, 30
                ),
            ),
            maximum=250,
        ),
        results=array(
            obj(
                id=ID,
                work_id=ID,
                version_id=ID,
                label=text(100),
                summary=text(),
                lane=ID,
                kind=choice(
                    "foundation",
                    "framework",
                    "extension",
                    "challenge",
                    "tutorial",
                    "result",
                ),
                settings=SETTINGS,
                evidence=array(ID, 1),
                review_status=STATUS,
                reviews=REVIEWS,
            ),
            maximum=250,
        ),
        evidence=array(
            obj(
                id=ID,
                work_id=ID,
                version_id=ID,
                url=URL,
                locator=text(500),
                kind=choice("abstract", "full_text", "metadata"),
                summary=text(),
                checked=DATE,
            ),
            maximum=1000,
        ),
        relations=array(
            obj(
                id=ID,
                source=ID,
                target=ID,
                type=choice(*RELATIONS),
                summary=text(),
                evidence=array(ID, 1),
                basis=choice("author_explicit", "editorial_inference", "citation_only"),
                comparability=choice("not_assessed", "comparable", "not_comparable"),
                review_status=STATUS,
                reviews=REVIEWS,
            ),
            maximum=1000,
        ),
        reading_route=array(ID, maximum=250),
    ),
}


def safe_url(value):
    """Links are never fetched by the renderer; still reject executable schemes."""
    try:
        parts = urlsplit(value)
        return (
            parts.scheme in ("https", "http")
            and bool(parts.hostname)
            and not parts.username
            and not parts.password
            and not re.search(r"[\s\\\x00-\x1f\x7f]", value)
        )
    except ValueError:
        return False


def _structure(value, schema, path, errors):
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    actual = (
        "null"
        if value is None
        else "object"
        if isinstance(value, dict)
        else "array"
        if isinstance(value, list)
        else "string"
        if isinstance(value, str)
        else "unsupported"
    )
    if actual not in types:
        errors.append(f"{path}: expected {' or '.join(types)}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    if actual == "object":
        for key in schema["required"]:
            if key not in value:
                errors.append(f"{path}.{key}: required")
        for key, item in value.items():
            if key not in schema["properties"]:
                errors.append(f"{path}.{key}: unknown field")
            else:
                _structure(item, schema["properties"][key], f"{path}.{key}", errors)
    if actual == "array":
        if not schema["minItems"] <= len(value) <= schema["maxItems"]:
            errors.append(f"{path}: item count outside allowed range")
        for index, item in enumerate(value):
            _structure(item, schema["items"], f"{path}[{index}]", errors)
    if actual == "string":
        if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff]", value):
            errors.append(f"{path}: unsupported control character or Unicode surrogate")
        if len(value.strip()) < schema.get("minLength", 0) or len(value) > schema.get(
            "maxLength", 10000
        ):
            errors.append(f"{path}: invalid text length")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: invalid format")
        if schema.get("format") == "uri" and not safe_url(value):
            errors.append(f"{path}: expected a safe HTTP(S) URL without credentials")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{path}: invalid calendar date")


def validate(data):
    """Return actionable errors and non-fatal review warnings; never certify science."""
    errors, warnings = [], []
    _structure(data, SCHEMA, "$", errors)
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    indexes = {}
    for collection in ("lanes", "works", "results", "evidence", "relations"):
        indexes[collection] = {item["id"]: item for item in data[collection]}
        if len(indexes[collection]) != len(data[collection]):
            errors.append(f"{collection}: duplicate IDs")
    works, results, evidence = (
        indexes[key] for key in ("works", "results", "evidence")
    )
    versions = {}
    for work in data["works"]:
        if work["first_published"] > data["scope"]["cutoff"]:
            errors.append(f"{work['id']}: first publication exceeds cutoff")
        for version in work["versions"]:
            if version["id"] in versions:
                errors.append(f"{version['id']}: duplicate version ID")
            versions[version["id"]] = (work["id"], version)
            if (
                not work["first_published"]
                <= version["published"]
                <= data["scope"]["cutoff"]
            ):
                errors.append(
                    f"{version['id']}: version date outside publication/cutoff bounds"
                )

    for item in data["evidence"] + data["results"]:
        version = versions.get(item["version_id"])
        if item["work_id"] not in works or not version or version[0] != item["work_id"]:
            errors.append(f"{item['id']}: work/version reference does not resolve")
        if item in data["evidence"] and version:
            if item["url"] != version[1]["url"]:
                errors.append(
                    f"{item['id']}: evidence URL must match its pinned source version"
                )
            if item["checked"] < version[1]["published"]:
                errors.append(
                    f"{item['id']}: evidence checked before source became available"
                )

    for item in data["results"] + data["relations"]:
        refs = [evidence[eid] for eid in item["evidence"] if eid in evidence]
        if len(refs) != len(item["evidence"]) or len(set(item["evidence"])) != len(
            refs
        ):
            errors.append(f"{item['id']}: missing or duplicate evidence reference")
        if item["review_status"] == "reviewed":
            required = (
                2
                if item.get("type") in ("critiques", "refutes_claim", "improves_bound")
                else 1
            )
            if len({review["url"] for review in item["reviews"]}) < required:
                errors.append(
                    f"{item['id']}: needs {required} independent review reference(s)"
                )
            if (
                len({review["name"].strip().casefold() for review in item["reviews"]})
                < required
            ):
                errors.append(
                    f"{item['id']}: needs {required} distinct named reviewer(s)"
                )
            if not any(ref["kind"] == "full_text" for ref in refs):
                errors.append(
                    f"{item['id']}: reviewed content requires full-text evidence"
                )
        if "work_id" in item:
            if item["lane"] not in indexes["lanes"]:
                errors.append(f"{item['id']}: missing lane")
            if not any(
                ref["work_id"] == item["work_id"]
                and ref["version_id"] == item["version_id"]
                for ref in refs
            ):
                errors.append(f"{item['id']}: no evidence for its own source version")
        else:
            source, target = results.get(item["source"]), results.get(item["target"])
            if not source or not target:
                errors.append(f"{item['id']}: relation endpoint does not resolve")
                continue
            if source["id"] == target["id"]:
                errors.append(f"{item['id']}: self relationship is not allowed")
            if item["type"] != "cites" and item["basis"] == "citation_only":
                errors.append(
                    f"{item['id']}: citation alone cannot support a semantic relation"
                )
            if item["basis"] == "author_explicit" and not any(
                ref["version_id"] == target["version_id"] for ref in refs
            ):
                errors.append(
                    f"{item['id']}: author-explicit relationship needs target-version evidence"
                )
            if item["type"] == "improves_bound":
                if item["comparability"] != "comparable" or any(
                    value is None
                    for result in (source, target)
                    for value in result["settings"].values()
                ):
                    errors.append(
                        f"{item['id']}: improvement requires comparable, fully stated settings"
                    )

    # Only proof-use dependencies must be a DAG; critiques and surveys need not be.
    graph = {key: [] for key in results}
    indegree = dict.fromkeys(results, 0)
    for edge in data["relations"]:
        if (
            edge["type"] == "uses_result"
            and edge["source"] in graph
            and edge["target"] in graph
        ):
            graph[edge["source"]].append(edge["target"])
            indegree[edge["target"]] += 1
    queue = [key for key, value in indegree.items() if value == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for target in graph[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if visited != len(graph):
        errors.append("relations: cycle in uses_result dependencies")
    if any(item not in results for item in data["reading_route"]) or len(
        set(data["reading_route"])
    ) != len(data["reading_route"]):
        errors.append("reading_route: missing or duplicate result")
    if not results:
        warnings.append(
            "Empty draft: add source-grounded results before building a map."
        )
    proposed = sum(
        item["review_status"] == "proposed"
        for item in data["results"] + data["relations"]
    )
    if proposed:
        warnings.append(f"{proposed} results/relationships await scholarly review.")
    if any(item["kind"] != "full_text" for item in data["evidence"]):
        warnings.append(
            "Some evidence is abstract/metadata level; no proof verification is implied."
        )
    if any(
        item["review_status"] == "reviewed"
        for item in data["results"] + data["relations"]
    ):
        warnings.append(
            "Review references are recorded, not authenticated by this validator."
        )
    return {"valid": not errors, "errors": errors, "warnings": warnings}
