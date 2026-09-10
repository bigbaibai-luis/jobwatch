"""Command-line interface."""
from __future__ import annotations

import argparse

from .core import run


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="jobwatch",
        description="Monitor job boards and get notified about new postings.",
    )
    p.add_argument("--source", choices=["remoteok", "html", "rss"], default="remoteok",
                   help="Job source (default: remoteok)")
    p.add_argument("--keywords", help="Comma-separated keywords (match title/company/tags)")
    p.add_argument("--limit", type=int, default=0, help="Max jobs to consider (0 = no limit)")
    p.add_argument("--state", default="jobwatch.state.json", help="State file path")
    p.add_argument("--notify", choices=["console", "webhook", "serverchan"], default="console",
                   help="Notification channel (default: console)")
    p.add_argument("--webhook-url", help="Webhook URL for --notify webhook")
    p.add_argument("--sendkey", help="ServerChan SendKey for --notify serverchan")
    p.add_argument("--dry-run", action="store_true", help="Do not save state")
    p.add_argument("--test-notify", action="store_true",
                   help="Send a test notification via the configured channel and exit")
    p.add_argument("--no-verify-ssl", action="store_true",
                   help="Skip SSL cert verification (insecure; workaround for expired/misconfigured certs)")

    # html source options
    p.add_argument("--url", help="(html) job board page URL")
    p.add_argument("--item-selector", help="(html) CSS selector for a job item")
    p.add_argument("--title-selector", help="(html) CSS selector for the job title")
    p.add_argument("--link-selector", default="a::attr(href)", help="(html) CSS selector for the job link")
    p.add_argument("--id-selector", help="(html) CSS selector for a stable job id (optional)")
    p.add_argument("--base-url", help="(html) base URL for relative links")

    args = p.parse_args(argv)

    if args.source == "html" and not (args.url and args.item_selector and args.title_selector):
        p.error("--source html requires --url, --item-selector, and --title-selector")
    if args.source == "rss" and not args.url:
        p.error("--source rss requires --url")

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
