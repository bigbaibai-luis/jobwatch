# 💼 jobwatch

[![CI](https://github.com/bigbaibai-luis/jobwatch/actions/workflows/ci.yml/badge.svg)](https://github.com/bigbaibai-luis/jobwatch/actions/workflows/ci.yml)

Monitor job boards and get notified about **new** postings — remote jobs from [RemoteOK](https://remoteok.com) out of the box, or any job board you're authorized to scrape via [Scrapling](https://github.com/D4Vinci/Scrapling).

> [简体中文](README.zh-CN.md)

## How it works

1. **Fetch** jobs from a source (RemoteOK JSON API, or a custom HTML page via Scrapling).
2. **Filter** by comma-separated keywords (matches title, company, and tags).
3. **Diff** against a state file — remember which job ids you've already seen.
4. **Notify** you about new jobs only (console, webhook, or ServerChan/WeChat push).

The **first run saves a baseline** (no alerts); every run after that alerts you only on new postings.

## Install

Core is **stdlib-only** (no dependencies). Python 3.9+.

```bash
git clone https://github.com/bigbaibai-luis/jobwatch.git
cd jobwatch
pip install -e .              # installs the `jobwatch` command
```

Optional: Scrapling (only for `--source html`):

```bash
pip install "scrapling[fetchers]"
```

## Quickstart

```bash
# First run: save a baseline of all "python" remote jobs (no alerts)
jobwatch --source remoteok --keywords "python"

# Later runs: prints only NEW python jobs
jobwatch --source remoteok --keywords "python"

# Multiple keywords, limit, and custom state file
jobwatch --keywords "python,backend,data" --limit 50 --state my.state.json

# Dry run (don't save state)
jobwatch --keywords "ai" --dry-run
```

## Notifications

```bash
# Console (default)
jobwatch --keywords "python" --notify console

# Generic webhook (钉钉/飞书/企业微信/custom — any endpoint that accepts JSON)
jobwatch --keywords "python" --notify webhook --webhook-url "https://your-webhook.example/hook"

# ServerChan (WeChat push, China-friendly)
jobwatch --keywords "python" --notify serverchan --sendkey "SCTxxxxx"
```

## WeChat push (ServerChan) setup

`jobwatch` ships with **ServerChan (Server酱)** support to push alerts straight to WeChat.

1. Open [sct.ftqq.com](https://sct.ftqq.com) and log in with **GitHub**.
2. Scan the QR code to follow the **方糖 (FTQQ)** official account — messages arrive through it.
3. Copy your **SendKey** from the SendKey page (looks like `SCT123456...`).
4. Send a test message to verify:
   ```bash
   jobwatch --notify serverchan --sendkey "SCT123456..." --test-notify
   ```
   You should see "jobwatch test" in WeChat.
5. Then use it normally:
   ```bash
   jobwatch --keywords "python" --notify serverchan --sendkey "SCT123456..."
   ```

> Tip: `--test-notify` also works with `webhook` to verify any channel.

## Custom job board (HTML via Scrapling)

For sites you are **authorized** to scrape, provide CSS selectors:

```bash
jobwatch --source html \
  --url "https://example.com/jobs" \
  --item-selector ".job-listing" \
  --title-selector "h2" \
  --link-selector "a::attr(href)" \
  --id-selector "::attr(data-id)" \
  --base-url "https://example.com"
```

> **Important:** without `--id-selector`, the job id falls back to the item's
> position, which is **not stable** across runs. Provide a stable `--id-selector`
> for reliable change detection. And always respect the target's `robots.txt` and ToS.

## RSS / Atom source (compliant job feeds)

Any job board or community that publishes an RSS/Atom feed can be monitored — this is the cleanest way to watch sources whose ToS prohibit HTML scraping.

```bash
jobwatch --source rss --url "https://example.com/jobs/rss.xml" --keywords "python"
```

> Example: communities like V2EX publish job feeds (`/feed/tab/jobs.xml`). Use the official feed URL and respect the site's rate limits.

## Run it on a schedule

**Linux/macOS (cron)** — every 30 minutes:

```
*/30 * * * * cd /path/to/jobwatch && jobwatch --keywords "python" --notify serverchan --sendkey SCTxxxxx >> jobwatch.log 2>&1
```

**Windows (Task Scheduler)** — create a task that runs:

```
powershell -Command "cd D:\renwu\jobwatch; jobwatch --keywords 'python' --notify serverchan --sendkey SCTxxxxx"
```

**GitHub Actions** — add a scheduled workflow using a repository secret for the sendkey.

## Compliance

- RemoteOK's API ToS asks that you **link back to RemoteOK** and mention it as a source if you build on it.
- The HTML source is for **authorized targets only** — respect `robots.txt`, the site's ToS, and applicable law (GDPR/PIPL/CCPA). Never scrape data you have no right to collect.

## Project structure

```
jobwatch/
├── jobwatch/
│   ├── cli.py        # command-line interface
│   ├── core.py       # fetch -> filter -> diff -> notify pipeline
│   ├── sources.py    # RemoteOK + Scrapling HTML sources
│   ├── state.py      # seen-job-ids persistence
│   └── notify.py     # console / webhook / ServerChan
├── tests/
├── pyproject.toml
├── .github/workflows/ci.yml
├── README.md / README.zh-CN.md
└── LICENSE
```

## License

MIT — see [LICENSE](LICENSE).
