"""Explicit local quote checks, separate from source authenticity or scholarly review."""

import hashlib
import json
import unicodedata

METHOD = "nfc-whitespace-v1"
LIMIT = 5_000_000


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def selector_digest(quote):
    return digest(json.dumps(quote, ensure_ascii=False, sort_keys=True))


def normalize(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def check_anchor(evidence, text=None):
    """Return a reproducible report; no network, map mutation, or review promotion."""
    quote = evidence.get("quote")
    if (
        not quote
        or not isinstance(quote.get("exact"), str)
        or not quote["exact"].strip()
    ):
        raise ValueError("Evidence needs a quote selector before checking local text.")
    report = {
        "work_id": evidence["work_id"],
        "version_id": evidence["version_id"],
        "url": evidence["url"],
        "selector_sha256": selector_digest(quote),
        "text_sha256": None,
        "method": METHOD,
        "outcome": "unchecked",
    }
    if text is None:
        return report
    if not isinstance(text, str):
        raise ValueError("Local source text must be a string.")
    if len(text.encode("utf-8")) > LIMIT:
        raise ValueError("Source text exceeds the 5 MB local-check limit.")
    report["text_sha256"] = digest(text)
    source, exact = normalize(text), normalize(quote["exact"])
    prefix, suffix = normalize(quote["prefix"]), normalize(quote["suffix"])
    matches, start = 0, 0
    while (position := source.find(exact, start)) >= 0:
        before_end, after_start = position, position + len(exact)
        if before_end and source[before_end - 1] == " ":
            before_end -= 1
        if after_start < len(source) and source[after_start] == " ":
            after_start += 1
        if (not prefix or source.endswith(prefix, 0, before_end)) and (
            not suffix or source.startswith(suffix, after_start)
        ):
            matches += 1
            if matches == 2:
                break
        start = position + 1
    report["outcome"] = (
        "missing" if not matches else "matched" if matches == 1 else "ambiguous"
    )
    return report


def anchor_report_errors(evidence):
    """Check a stored report's binding, without pretending to reproduce its text check."""
    report = evidence.get("anchor_check")
    if not report:
        return []
    quote = evidence.get("quote")
    if not quote:
        return ["An anchor check requires its quote selector."]
    expected = {key: evidence[key] for key in ("work_id", "version_id", "url")}
    expected["selector_sha256"] = selector_digest(quote)
    errors = []
    if any(report[key] != value for key, value in expected.items()):
        errors.append(
            "Stored anchor check does not match this source version/selector."
        )
    if (report["outcome"] == "unchecked") != (report["text_sha256"] is None):
        errors.append(
            "Checked anchors need a text digest; unchecked anchors must not claim one."
        )
    return errors
