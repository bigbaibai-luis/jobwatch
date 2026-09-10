# Contributing / 贡献指南

Thanks for considering contributing! / 感谢你考虑贡献！

## How to contribute / 如何贡献

1. Fork the repo / Fork 本仓库
2. Create a branch / 新建分支
3. Make changes / 修改
4. Open a pull request / 提交 PR

## Design rules / 设计规则

- Core (`jobwatch/`) stays **stdlib-only** — no third-party runtime deps / 核心保持**纯标准库**，不引入第三方运行时依赖
- Scrapling remains an optional extra (`--source html`) / Scrapling 保持可选（仅 `--source html` 用）
- New sources must document compliance (robots.txt, ToS, privacy law) / 新数据源必须注明合规要求

## Local checks / 本地校验

```bash
python -m compileall jobwatch
python -m unittest discover -s tests -v
```

CI runs these automatically / CI 会自动执行。
