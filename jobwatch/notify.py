"""Notifications: console (default), generic webhook, ServerChan (WeChat push)."""
from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request


def _context(verify: bool):
    if verify:
        return None
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def console(title: str, lines: list[str]) -> None:
    print(title)
    for line in lines:
        print("  " + line)


def webhook(url: str, title: str, lines: list[str], verify: bool = True) -> None:
    payload = {"title": title, "content": "\n".join(lines)}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30, context=_context(verify)) as resp:
        resp.read()


def serverchan(sendkey: str, title: str, lines: list[str], verify: bool = True) -> None:
    url = f"https://sctapi.ftqq.com/{sendkey}.send"
    data = urllib.parse.urlencode({"title": title, "desp": "\n".join(lines)}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30, context=_context(verify)) as resp:
        resp.read()


def send(
    method: str,
    title: str,
    lines: list[str],
    webhook_url: str = "",
    sendkey: str = "",
    verify: bool = True,
) -> None:
    if method == "console":
        console(title, lines)
    elif method == "webhook":
        if not webhook_url:
            raise RuntimeError("--webhook-url is required with --notify webhook")
        webhook(webhook_url, title, lines, verify)
    elif method == "serverchan":
        if not sendkey:
            raise RuntimeError("--sendkey is required with --notify serverchan")
        serverchan(sendkey, title, lines, verify)
    else:
        raise RuntimeError(f"unknown notify method: {method}")
