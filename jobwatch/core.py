"""Pipeline: fetch -> filter -> diff -> notify."""
from __future__ import annotations

import json

from . import notify, sources, state


def _match(job: dict, keywords: list[str]) -> bool:
    if not keywords:
        return True
    haystack = " ".join(
        [job.get("title", ""), job.get("company", ""), " ".join(job.get("tags") or [])]
    ).lower()
    return any(k.lower() in haystack for k in keywords)


def _format(job: dict) -> str:
    title = job.get("title") or "(no title)"
    company = job.get("company") or "(no company)"
    line = f"{title} — {company}"
    if job.get("location"):
        line += f" [{job['location']}]"
    if job.get("salary"):
        line += f" ({job['salary']})"
    if job.get("url"):
        line += f" | {job['url']}"
    return line


def load_config(path: str) -> list[dict]:
    """Load a monitor config: {"monitors": [...]} or a bare JSON array."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "monitors" in data:
        data = data["monitors"]
    if isinstance(data, list):
        return data
    raise ValueError('config must be {"monitors": [...]} or a JSON array')


def run_monitor(spec: dict) -> None:
    src = spec.get("source", "remoteok")
    verify = not spec.get("no_verify_ssl", False)
    label = spec.get("label") or spec.get("url") or src

    # 1. fetch
    if src == "remoteok":
        jobs = sources.fetch_remoteok(verify=verify)
    elif src == "html":
        jobs = sources.fetch_scrapling_html(
            url=spec["url"],
            item_selector=spec["item_selector"],
            title_selector=spec["title_selector"],
            link_selector=spec.get("link_selector", "a::attr(href)"),
            id_selector=spec.get("id_selector"),
            base_url=spec.get("base_url") or spec["url"],
        )
    elif src == "rss":
        jobs = sources.fetch_rss(spec["url"], verify=verify)
    else:
        raise ValueError(f"unknown source: {src}")

    # 2. filter by keywords
    keywords = [k.strip() for k in spec["keywords"].split(",") if k.strip()] if spec.get("keywords") else []
    matched = [j for j in jobs if _match(j, keywords)]
    if spec.get("limit"):
        matched = matched[: spec["limit"]]

    # 3. diff against seen state
    st = state.State(spec.get("state", "jobwatch.state.json"))
    new = st.new_jobs(matched)

    # 4. report / notify
    if not st.seen:
        print(f"[{label}] first run: {len(matched)} matching job(s) saved as baseline.")
        for j in matched:
            print("  " + _format(j))
    elif new:
        title = f"[{label}] {len(new)} new job(s)"
        notify.send(
            spec.get("notify", "console"),
            title,
            [_format(j) for j in new],
            spec.get("webhook_url", ""),
            spec.get("sendkey", ""),
            verify=verify,
        )
    else:
        print(f"[{label}] no new jobs.")

    # 5. persist state
    if not spec.get("dry_run", False):
        st.mark_seen(matched)
        st.save()


def run(args) -> int:
    if args.test_notify:
        notify.send(
            args.notify,
            "jobwatch test",
            ["This is a test notification from jobwatch."],
            args.webhook_url,
            args.sendkey,
            verify=not args.no_verify_ssl,
        )
        print("Test notification sent.")
        return 0

    if args.config:
        for spec in load_config(args.config):
            try:
                run_monitor(spec)
            except Exception as exc:
                label = spec.get("label") or spec.get("url") or spec.get("source")
                print(f"[{label}] ERROR: {exc}")
        return 0

    spec = {
        "source": args.source,
        "url": args.url,
        "item_selector": args.item_selector,
        "title_selector": args.title_selector,
        "link_selector": args.link_selector,
        "id_selector": args.id_selector,
        "base_url": args.base_url,
        "keywords": args.keywords,
        "limit": args.limit,
        "state": args.state,
        "notify": args.notify,
        "webhook_url": args.webhook_url,
        "sendkey": args.sendkey,
        "no_verify_ssl": args.no_verify_ssl,
        "dry_run": args.dry_run,
    }
    run_monitor(spec)
    return 0
