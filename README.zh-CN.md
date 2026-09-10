# 💼 jobwatch

[![CI](https://github.com/bigbaibai-luis/jobwatch/actions/workflows/ci.yml/badge.svg)](https://github.com/bigbaibai-luis/jobwatch/actions/workflows/ci.yml)

监控招聘网站，**新职位**出现时通知你——开箱即用支持 [RemoteOK](https://remoteok.com) 远程职位，也可通过 [Scrapling](https://github.com/D4Vinci/Scrapling) 采集你有权访问的任意招聘网站。

> [English](README.md)

## 工作原理

1. **抓取**职位（RemoteOK JSON 接口，或自定义 HTML 页面）；
2. **按关键词过滤**（逗号分隔，匹配职位名/公司/标签）；
3. **对比**状态文件——记住已经见过的职位 id；
4. **只通知新职位**（控制台 / webhook / Server酱微信推送）。

**第一次运行保存基线（不提醒）**，之后的每次运行只提醒新出现的职位。

## 安装

核心**纯标准库、零依赖**，Python 3.9+。

```bash
git clone https://github.com/bigbaibai-luis/jobwatch.git
cd jobwatch
pip install -e .              # 安装 jobwatch 命令
```

可选：Scrapling（仅 `--source html` 需要）：

```bash
pip install "scrapling[fetchers]"
```

## 快速开始

```bash
# 第一次运行：保存所有 "python" 职位的基线（不提醒）
jobwatch --source remoteok --keywords "python"

# 之后的运行：只打印新出现的 python 职位
jobwatch --source remoteok --keywords "python"

# 多关键词、限制数量、自定义状态文件
jobwatch --keywords "python,后端,data" --limit 50 --state my.state.json

# 试运行（不保存状态）
jobwatch --keywords "ai" --dry-run
```

## 通知方式

```bash
# 控制台（默认）
jobwatch --keywords "python" --notify console

# 通用 webhook（钉钉/飞书/企业微信/自定义，任何接受 JSON 的端点）
jobwatch --keywords "python" --notify webhook --webhook-url "https://your-webhook.example/hook"

# Server酱（微信推送，国内友好）
jobwatch --keywords "python" --notify serverchan --sendkey "SCTxxxxx"
```

## 微信推送（Server酱）设置

`jobwatch` 内置了 **Server酱（ServerChan）**，可以把新职位提醒直接推到你的微信。

1. 打开 [sct.ftqq.com](https://sct.ftqq.com)，用 **GitHub 账号** 一键登录；
2. 按提示**微信扫码关注「方糖」公众号**（消息就是通过这个公众号发到微信）；
3. 在 **SendKey** 页面复制你的 key（形如 `SCT123456...`）；
4. 用 `--test-notify` 发一条测试消息验证：
   ```bash
   jobwatch --notify serverchan --sendkey "SCT123456..." --test-notify
   ```
   微信收到「jobwatch test」就说明通了；
5. 之后正常使用：
   ```bash
   jobwatch --keywords "python" --notify serverchan --sendkey "SCT123456..."
   ```

> 提示：`--test-notify` 对 webhook 同样适用，可用来验证任何通知渠道。

## 自定义招聘网站（Scrapling 抓 HTML）

对**你有权采集**的网站，提供 CSS 选择器：

```bash
jobwatch --source html \
  --url "https://example.com/jobs" \
  --item-selector ".job-listing" \
  --title-selector "h2" \
  --link-selector "a::attr(href)" \
  --id-selector "::attr(data-id)" \
  --base-url "https://example.com"
```

> **注意：** 不传 `--id-selector` 时，职位 id 退化为"列表位置"，**不稳定**（新职位会挤位置）。请提供一个稳定的 `--id-selector` 才能可靠检测变化。并且务必遵守目标网站的 `robots.txt` 和服务条款。

## RSS / Atom 源（合规的职位订阅）

任何发布 RSS/Atom feed 的招聘平台/社区都可以监控——这是监控「条款禁止爬 HTML」的网站时最干净的方式。

```bash
jobwatch --source rss --url "https://example.com/jobs/rss.xml" --keywords "python"
```

> 示例：V2EX 等社区会发布职位 feed（如 `/feed/tab/jobs.xml`）。请使用官方 feed 地址，并遵守站点的频率限制。

## 定时运行

**Linux/macOS（cron）** —— 每 30 分钟：

```
*/30 * * * * cd /path/to/jobwatch && jobwatch --keywords "python" --notify serverchan --sendkey SCTxxxxx >> jobwatch.log 2>&1
```

**Windows（任务计划程序）** —— 新建任务，运行：

```
powershell -Command "cd D:\renwu\jobwatch; jobwatch --keywords 'python' --notify serverchan --sendkey SCTxxxxx"
```

**GitHub Actions** —— 加一个定时 workflow，sendkey 存成仓库 secret。

## 合规声明

- RemoteOK 的 API 条款要求：如果你基于它构建产品，需**回链到 RemoteOK** 并注明来源。
- HTML 源仅用于**授权目标**——遵守 `robots.txt`、网站服务条款和适用法律（GDPR/PIPL/CCPA）。不要采集你无权获取的数据。

## 目录结构

```
jobwatch/
├── jobwatch/
│   ├── cli.py        # 命令行
│   ├── core.py       # 抓取→过滤→对比→通知 流水线
│   ├── sources.py    # RemoteOK + Scrapling HTML 源
│   ├── state.py      # 已见职位 id 持久化
│   └── notify.py     # console / webhook / Server酱
├── tests/
├── pyproject.toml
├── .github/workflows/ci.yml
├── README.md / README.zh-CN.md
└── LICENSE
```

## 许可证

MIT — 见 [LICENSE](LICENSE)。
