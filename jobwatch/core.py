"""Pipeline: fetch -> filter -> diff -> notify."""
from __future__ import annotations

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


def run(args) -> int:
    # 1. fetch
    if args.source == "remoteok":
        jobs = sources.fetch_remoteok()
    elif args.source == "html":
        jobs = sources.fetch_scrapling_html(
            url=args.url,
            item_selector=args.item_selector,
            title_selector=args.title_selector,
            link_selector=args.link_selector,
            id_selector=args.id_selector,
            base_url=args.base_url or args.url,
        )
    else:
        print(f"error: unknown source {args.source}")
        return 2

    # 2. filter by keywords
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []
    matched = [j for j in jobs if _match(j, keywords)]
    if args.limit:
        matched = matched[: args.limit]

    # 3. diff against seen state
    st = state.State(args.state)
    new = st.new_jobs(matched)

    # 4. report / notify
    if not st.seen:
        print(f"First run: {len(matched)} matching job(s) saved as baseline (no alerts).")
        for j in matched:
            print("  " + _format(j))
    elif new:
        title = f"{len(new)} new job(s) matching your keywords"
        notify.send(args.notify, title, [_format(j) for j in new], args.webhook_url, args.sendkey)
    else:
        print("No new jobs.")

    # 5. persist state (skip on dry-run)
    if not args.dry_run:
        st.mark_seen(matched)
        st.save()

    return 0
