"""Job sources. Each source returns a list of job dicts.

Job dict keys: id, title, company, location, url, salary, tags, posted
"""
from __future__ import annotations

import json
import ssl
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "jobwatch/0.1 (+https://github.com/bigbaibai-luis/jobwatch)"


def _context(verify: bool):
    if verify:
        return None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _get(url: str, timeout: int = 30, verify: bool = True) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout, context=_context(verify)) as resp:
        return resp.read()


def _salary(min_v, max_v) -> str:
    if min_v and max_v:
        return f"${min_v} - ${max_v}"
    if min_v:
        return f"${min_v}+"
    if max_v:
        return f"up to ${max_v}"
    return ""


def fetch_remoteok(verify: bool = True) -> list[dict]:
    """Fetch remote jobs from the RemoteOK public JSON API.

    RemoteOK's API ToS asks that you link back to RemoteOK and mention it
    as a source if you build on top of it.
    """
    data = json.loads(_get("https://remoteok.com/api", verify=verify).decode("utf-8"))
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


def _text(elem, tag: str) -> str:
    for child in elem.iter():
        if child.tag == tag or child.tag.endswith("}" + tag):
            return (child.text or "").strip()
    return ""


def _link(elem) -> str:
    for child in elem.iter():
        if child.tag == "link" or child.tag.endswith("}link"):
            href = child.get("href")
            if href:
                return href
            return (child.text or "").strip()
    return ""


def parse_rss(xml_text: str) -> list[dict]:
    """Parse an RSS 2.0 or Atom feed into job dicts (pure function)."""
    root = ET.fromstring(xml_text)
    items = list(root.iter("item"))
    if not items:
        items = [e for e in root.iter() if e.tag == "entry" or e.tag.endswith("}entry")]
    jobs = []
    for it in items:
        title = _text(it, "title")
        link = _link(it)
        guid = _text(it, "guid") or _text(it, "id") or link
        if not title:
            continue
        jobs.append(
            {
                "id": guid or link or title,
                "title": title,
                "company": "",
                "location": "",
                "url": link,
                "salary": "",
                "tags": [],
                "posted": _text(it, "pubDate") or _text(it, "updated") or "",
            }
        )
    return jobs


def fetch_rss(url: str, verify: bool = True) -> list[dict]:
    """Fetch and parse an RSS/Atom feed (works with any board that publishes RSS)."""
    return parse_rss(_get(url, verify=verify).decode("utf-8", errors="replace"))


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
