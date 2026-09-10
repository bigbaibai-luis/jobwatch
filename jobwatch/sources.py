"""Job sources. Each source returns a list of job dicts.

Job dict keys: id, title, company, location, url, salary, tags, posted
"""
from __future__ import annotations

import json
import urllib.request

USER_AGENT = "jobwatch/0.1 (+https://github.com/bigbaibai-luis/jobwatch)"


def _get(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _salary(min_v, max_v) -> str:
    if min_v and max_v:
        return f"${min_v} - ${max_v}"
    if min_v:
        return f"${min_v}+"
    if max_v:
        return f"up to ${max_v}"
    return ""


def fetch_remoteok() -> list[dict]:
    """Fetch remote jobs from the RemoteOK public JSON API.

    RemoteOK's API ToS asks that you link back to RemoteOK and mention it
    as a source if you build on top of it.
    """
    data = json.loads(_get("https://remoteok.com/api").decode("utf-8"))
    jobs = []
    for item in data:
        if not isinstance(item, dict) or "id" not in item:
            continue  # skip the legal notice and any malformed entries
        jobs.append(
            {
                "id": str(item["id"]),
                "title": item.get("position", ""),
                "company": item.get("company", ""),
                "location": (item.get("location") or "").strip(),
                "url": item.get("url") or item.get("apply_url") or "",
                "salary": _salary(item.get("salary_min"), item.get("salary_max")),
                "tags": item.get("tags") or [],
                "posted": item.get("date", ""),
            }
        )
    return jobs


def fetch_scrapling_html(
    url,
    item_selector,
    title_selector,
    link_selector="a::attr(href)",
    id_selector=None,
    base_url="",
) -> list[dict]:
    """Fetch a job board page and extract jobs via CSS selectors (Scrapling).

    For authorized targets only — respect robots.txt and the site's ToS.

    NOTE: without `id_selector`, the job id falls back to the item's position,
    which is not stable across runs (new items shift positions). Provide a
    stable `id_selector` for reliable change detection.
    """
    try:
        from scrapling.fetchers import Fetcher
    except ImportError as exc:
        raise RuntimeError(
            "Scrapling is not installed. Install it with: pip install 'scrapling[fetchers]'"
        ) from exc

    page = Fetcher.get(url)
    jobs = []
    for i, item in enumerate(page.css(item_selector)):
        title = (item.css(title_selector).get() or "").strip()
        if not title:
            continue
        link = (item.css(link_selector).get() or "").strip()
        if link and base_url and link.startswith("/"):
            link = base_url.rstrip("/") + link
        jid = (item.css(id_selector).get() or "").strip() if id_selector else ""
        jobs.append(
            {
                "id": jid or f"{url}#{i}",
                "title": title,
                "company": "",
                "location": "",
                "url": link,
                "salary": "",
                "tags": [],
                "posted": "",
            }
        )
    return jobs
