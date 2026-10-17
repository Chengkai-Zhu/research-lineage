"""Render the actual research-run records as a self-contained evidence notebook."""

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from research_lineage.core import MapError, same_file
from research_lineage.research_scope import audit_run


def esc(value):
    return html.escape(str(value))


def url_list(urls):
    return "".join(
        '<li><a href="' + esc(url) + '">' + esc(url) + "</a></li>" for url in urls
    )


def write(folder):
    folder = Path(folder)
    manifest_path = folder / "manifest.json"
    audit = audit_run(manifest_path)
    if audit["status"] == "FAIL":
        raise MapError("Refusing to render inconsistent research evidence.")
    cached = json.loads((folder / "audit.json").read_text(encoding="utf-8-sig"))
    if cached != audit:
        raise MapError("Cached audit differs from the current evidence audit.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    paths = {
        key: folder / entry["path"] for key, entry in manifest["artifacts"].items()
    }
    destination = folder / "report.html"
    protected = list(paths.values()) + [
        manifest_path,
        folder / "audit.json",
        folder / "coverage-review.json",
    ]
    if (
        any(same_file(destination, path) for path in protected)
        or destination.is_symlink()
        or (destination.exists() and destination.stat().st_nlink > 1)
    ):
        raise MapError("Report output would overwrite or alias an evidence input.")
    log = json.loads(paths["research_log"].read_text(encoding="utf-8-sig"))
    trace = [
        json.loads(line)
        for line in paths["trace"].read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]
    review_path = folder / "coverage-review.json"
    review = (
        json.loads(review_path.read_text(encoding="utf-8"))
        if review_path.exists()
        else {
            "status": "PENDING",
            "summary": "Coverage review is not yet available.",
            "checks": [],
        }
    )
    n = audit["counts"]
    branches = "".join(
        f'<article class="branch"><span class="pill {esc(b["status"])}">{esc(b["status"])}</span><h3>{esc(b["label"])}</h3><p>{esc(b["basis"])}</p><small>{len(b["candidate_ids"])} considered candidates · {len(b["search_ids"])} research operations</small>{"<p>" + esc(b["gap"]) + "</p>" if b["gap"] else ""}</article>'
        for b in log["branches"]
    )
    sources = "".join(
        f'<tr data-decision="{esc(c["decision"])}"><td><span class="pill {esc(c["decision"])}">{esc(c["decision"])}</span></td><td><a href="{esc(c["url"])}" target="_blank" rel="noreferrer">{esc(c["title"])}</a><small>{esc(c["id"])} · {esc(c["access"])} · {esc(c["locator"])}</small></td><td>{esc(c["reason"])}</td></tr>'
        for c in log["candidates"]
    )
    searches = "".join(
        f'<details><summary><span class="pill">{esc(s["direction"])}</span> {esc(s["id"])} · {len(s["candidate_ids"])} candidates <span class="quiet">{esc(s["status"])}</span></summary><pre>{esc(s["query"])}</pre><p>{esc(s["finding"])}</p><small>Checked {esc(s["checked"])} · trace {esc(", ".join(s["trace_ids"]))}</small></details>'
        for s in log["searches"]
    )
    operations = "".join(
        f'<details><summary><span class="pill {esc(t["status"])}">{esc(t["status"])}</span> {esc(t["id"])} · {esc(t["tool"])}</summary><small>{esc(t["at"])}</small><pre>{esc(t["query"])}</pre><p>{esc(t["observation"])}</p><ul>{url_list(t["urls"])}</ul></details>'
        for t in trace
    )
    checks = "".join(
        f'<div class="check"><span class="pill {esc(c["status"].lower())}">{esc(c["status"])}</span><div><strong>{esc(name.replace("_", " "))}</strong>{"<p>" + esc("; ".join(c["details"])) + "</p>" if c["details"] else ""}</div></div>'
        for name, c in audit["checks"].items()
    )
    coverage = "".join(
        f'<tr><td><span class="pill {esc(c["status"].lower())}">{esc(c["status"])}</span></td><td>{esc(c["criterion"])}</td><td>{esc(c["observation"])}</td></tr>'
        for c in review["checks"]
    )
    refsets = "".join(
        f'<li><a href="{esc(r["url"])}">{esc(r["id"])}</a> · {esc(r["locator"])}<p>{esc(r["purpose"])}</p></li>'
        for r in log["reference_sets"]
    )
    downloads = "".join(
        f'<a class="download" href="{esc(a["path"])}">{esc(key.replace("_", " "))} ↗</a>'
        for key, a in manifest["artifacts"].items()
    )
    page = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>Research notebook · Surface-code history</title><style>
    :root{--ink:#18332a;--muted:#627168;--line:#dce3dc;--paper:#f7f8f3;--green:#276550;--soft:#e8eee5}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:var(--green);text-underline-offset:4px}header,main,footer{max-width:1120px;margin:auto;padding:0 38px}header{padding-top:38px;display:flex;justify-content:space-between;gap:20px;font-size:13px;border-bottom:1px solid var(--line);padding-bottom:20px}.brand{font-weight:700;letter-spacing:.03em}.eyebrow{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--green);font-weight:700}h1{font-family:Georgia,"Times New Roman",serif;font-weight:400;font-size:clamp(40px,5.6vw,68px);line-height:1.08;letter-spacing:-.035em;max-width:850px;margin:18px 0 24px}h2{font-family:Georgia,"Times New Roman",serif;font-size:31px;font-weight:400;line-height:1.2;margin:10px 0 18px}h3{font-size:17px;line-height:1.45;font-weight:600;margin:14px 0 10px}.hero{padding:60px 0 35px}.lead{max-width:780px;font-size:18px;color:var(--muted)}.cta{display:inline-block;padding:11px 20px;background:var(--green);color:white;text-decoration:none;border-radius:6px;margin-top:15px}.stats{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:32px 0 0;padding:22px 0;gap:20px}.stats strong{font:36px/1.2 Georgia,serif;display:block}.stats span{font-size:12px;color:var(--muted)}section{padding:38px 0;border-bottom:1px solid var(--line)}.quiet,small{color:var(--muted);font-size:12px}small{display:block;margin:6px 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.branch{background:#fff;border:1px solid var(--line);border-radius:9px;padding:23px}.branch p{font-size:14px;color:var(--muted);margin:8px 0}.pill{display:inline-block;border:1px solid var(--line);border-radius:30px;padding:2px 9px;font-size:10px;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;background:#fff}.pass,.covered,.include,.ok{background:var(--soft);border-color:#ccdccc;color:#245b42}.fail,.failed{background:#f7e7e2;color:#873e2a;border-color:#e8c8be}.partial,.gap,.defer{background:#f3eddd;color:#7c6026;border-color:#e5d8b5}.check{display:flex;align-items:flex-start;gap:13px;margin:16px 0}.check strong{text-transform:capitalize;font-size:14px}.check p{font-size:13px;margin:5px 0}details{border-top:1px solid var(--line);padding:14px 0}summary{cursor:pointer;font-size:14px;line-height:1.7}details p{font-size:14px;color:var(--muted)}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.7 ui-monospace,Consolas,monospace;background:#eef1e9;padding:16px;border-radius:6px}table{width:100%;border-collapse:collapse;font-size:13px}th{text-align:left;color:var(--muted);font-weight:500;font-size:11px;letter-spacing:.06em;text-transform:uppercase}td,th{padding:15px 12px;border-bottom:1px solid var(--line);vertical-align:top}td:first-child{padding-left:0}td:nth-child(2){width:45%}.table-wrap{overflow-x:auto}input{background:white;border:1px solid var(--line);border-radius:6px;padding:10px 12px;width:100%;font:inherit;font-size:13px;margin-bottom:12px}button{background:white;color:var(--ink);border:1px solid var(--line);padding:6px 12px;border-radius:4px;cursor:pointer;margin:0 5px 16px 0}button[aria-pressed=true]{background:var(--green);color:white}.downloads{display:flex;flex-wrap:wrap;gap:10px}.download{font-size:12px;padding:8px 13px;background:white;border:1px solid var(--line);border-radius:5px;text-decoration:none}footer{padding-top:28px;padding-bottom:45px;color:var(--muted);font-size:12px}li{overflow-wrap:anywhere}a{overflow-wrap:anywhere}[hidden]{display:none!important}@media(max-width:650px){header,main,footer{padding-left:22px;padding-right:22px}.hero{padding-top:38px}.stats{grid-template-columns:repeat(2,1fr)}.grid{grid-template-columns:1fr}td,th{padding:12px 7px}header .quiet{display:none}}
    </style></head><body><header><span class="brand">researchlineage <span class="quiet">/ research notebook</span></span><span class="quiet">A single-paper execution · @@DATE@@</span></header><main>
    <div class="hero"><div class="eyebrow">One paper. An inspectable research history.</div><h1>From a threshold idea<br>to a working memory.</h1><p class="lead">@@SCOPE@@</p><a class="cta" href="@@MAP@@">Open the research map →</a><div class="stats"><div><strong>@@WORKS@@</strong><span>works in the map</span></div><div><strong>@@CANDIDATES@@</strong><span>candidates accounted for</span></div><div><strong>@@SEARCHES@@</strong><span>recorded research steps</span></div><div><strong>@@MOMENTS@@ / @@ROUTE@@</strong><span>overview moments / reading steps</span></div></div></div>
    <section><div class="eyebrow">01 / What ran</div><h2>A fresh context, with the input preserved.</h2><p>@@INPUT@@</p><p class="quiet">@@EXECUTION@@</p><details><summary>Execution provenance, runner interventions and limits</summary><p>@@ISOLATION@@</p><p>Inspect <a href="runner-record.json">the parent runner record</a> and <a href="runner-messages.json">technical interventions</a> alongside the agent-recorded trace. Neither is authenticated provider telemetry. Model identity: @@MODEL@@.</p><p>Actual tool failures remain in the operation log below. The optional start helper was rejected twice; the brief is explicitly marked as a manual fallback, not helper output. Source checks and software checks are separate from independent scholarly review, which remains open in issue #10.</p></details></section>
    <section><div class="eyebrow">02 / Coverage</div><h2>The research branches behind the short story.</h2><div class="grid">@@BRANCHES@@</div><details><summary>Reference sets used to establish the scope</summary><ul>@@REFSETS@@</ul></details><p class="quiet">Stopping judgment: @@STOP@@</p></section>
    <section><div class="eyebrow">03 / Evidence review</div><h2>What the records establish.</h2>@@CHECKS@@<p class="quiet">@@LIMITS@@</p><details><summary>Source-based coverage review · @@REVIEWSTATUS@@</summary><p>@@REVIEW@@</p><div class="table-wrap"><table><thead><tr><th>Result</th><th>Criterion</th><th>Observed evidence</th></tr></thead><tbody>@@COVERAGE@@</tbody></table></div><p><a href="coverage-review.json">Read the coverage assessment</a></p></details></section>
    <section><div class="eyebrow">04 / Corpus</div><h2>Every considered work has a decision.</h2><p class="quiet">@@INCLUDED@@ included · @@EXCLUDED@@ excluded · @@DEFERRED@@ deferred. A short route does not remove the remaining included works.</p><details><summary>Inspect the candidate ledger</summary><input id="query" aria-label="Search candidate works" placeholder="Search title, source or decision reason…"><div id="filters"><button data-filter="all" aria-pressed="true">All</button><button data-filter="include" aria-pressed="false">Included</button><button data-filter="exclude" aria-pressed="false">Excluded</button><button data-filter="defer" aria-pressed="false">Deferred</button></div><div class="table-wrap"><table><thead><tr><th>Decision</th><th>Work and access</th><th>Reason</th></tr></thead><tbody id="sources">@@SOURCES@@</tbody></table></div></details></section>
    <section><div class="eyebrow">05 / Actual research trail</div><h2>Queries, findings and failed attempts.</h2><p class="quiet">Research operations include queries, source opens/finds and metadata requests; these are not 95 independent search queries.</p><details><summary>Inspect @@SEARCHES@@ recorded research steps</summary>@@SEARCHLOG@@</details><details><summary>Inspect @@TRACECOUNT@@ tool-operation records</summary>@@OPERATIONS@@</details></section>
    <section><div class="eyebrow">06 / Keep and reproduce</div><h2>The files behind this result.</h2><div class="downloads">@@DOWNLOADS@@<a class="download" href="manifest.json">run manifest ↗</a><a class="download" href="audit.json">offline audit ↗</a></div><p class="quiet">Run from the repository: <code>python scripts/verify_research_run.py docs/test-reports/surface-code-rerun/manifest.json</code>. Rebuild the map with the generic Research Lineage runtime; the research log records observations, not a promise that future searches return identical results.</p></section>
    </main><footer>Research Lineage · Original annotations with primary-source links. The first screen is concise; the research record remains inspectable.</footer><script>
    let decision='all';const input=document.getElementById('query');function filter(){const query=input.value.toLowerCase();for(const row of document.querySelectorAll('#sources tr'))row.hidden=(decision!=='all'&&row.dataset.decision!==decision)||!row.textContent.toLowerCase().includes(query)}input.addEventListener('input',filter);document.getElementById('filters').addEventListener('click',event=>{const button=event.target.closest('button');if(!button)return;decision=button.dataset.filter;for(const b of document.querySelectorAll('#filters button'))b.setAttribute('aria-pressed',String(b===button));filter()});
    </script></body></html>"""
    execution = manifest["execution"]
    values = {
        "DATE": esc(log["cutoff"]),
        "SCOPE": esc(log["scope"]["summary"]),
        "MAP": esc(manifest["artifacts"]["html"]["path"]),
        "WORKS": n["map_works"],
        "CANDIDATES": n["candidates"],
        "SEARCHES": n["searches"],
        "MOMENTS": n["overview_cards"],
        "ROUTE": n["route_steps"],
        "INPUT": esc(manifest["input"]["seed"]),
        "EXECUTION": esc(
            execution["host"]
            + " · "
            + execution["agent_id"]
            + " · "
            + execution["started_at"]
            + " → "
            + execution["finished_at"]
        ),
        "ISOLATION": esc(execution["isolation"]),
        "MODEL": esc(execution["model"] or "not exposed"),
        "BRANCHES": branches,
        "REFSETS": refsets,
        "STOP": esc(log["stop"]["reason"]),
        "CHECKS": checks,
        "LIMITS": esc(audit["limits"]),
        "REVIEWSTATUS": esc(review["status"]),
        "REVIEW": esc(review["summary"]),
        "COVERAGE": coverage,
        "INCLUDED": n["include"],
        "EXCLUDED": n["exclude"],
        "DEFERRED": n["defer"],
        "SOURCES": sources,
        "SEARCHLOG": searches,
        "TRACECOUNT": len(trace),
        "OPERATIONS": operations,
        "DOWNLOADS": downloads,
    }
    import re

    page = re.sub(r"@@([A-Z]+)@@", lambda match: str(values[match[1]]), page)
    destination.write_text(page, encoding="utf-8", newline="\n")
    print(destination)


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python scripts/render_research_report.py <evidence-folder>")
        return 2
    try:
        write(args[0])
    except (MapError, OSError, ValueError) as exc:
        print(f"FAIL report: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
