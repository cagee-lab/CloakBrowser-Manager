## 背景

CloakBrowser Manager 是一个自托管的浏览器指纹配置文件管理器（FastAPI + React + SQLite + noVNC）。它通过 REST API 提供 profile 管理和浏览器生命周期控制，通过 CDP WebSocket 代理提供 Chrome DevTools Protocol 访问。目前没有 CLI 客户端——用户只能通过 Web UI 或直接调用 HTTP API 操作。

本设计实现一个独立的 `cloak-cli` 工具，采用"SDK 核心 + CLI 薄壳"架构。

## 目标 / 非目标

**目标：**
- 提供 `from cloakcli import CloakBrowserManagerClient` 的 Python SDK，封装 Manager 全部 REST API
- 提供 `cloak-cli` 命令行工具，覆盖 profile 管理、浏览器生命周期、CDP 浏览器自动化三大场景
- 浏览器自动化命令自动集成 humanize（Bézier 鼠标轨迹、真实打字延迟等），并支持 `--fast` 跳过
- 支持配置文件、环境变量、CLI 参数三级配置源，优先级可覆盖
- `batch` 命令支持单次 CDP 连接内批量执行多条操作

**非目标：**
- 不修改 Manager 或 CloakBrowser 现有代码（依赖 Plan B 在 CloakBrowser 侧新增的 3 个公开函数）
- 不引入后台 daemon 长连接（每操作独立 CDP 连接 + `batch` 解决链式操作需求）
- 不提供交互式 REPL（v1 再评估）
- 不实现 GUI

## 关键决策

### 1. SDK + CLI 双层架构 而非纯 CLI

**选型：** SDK 核心类 `CloakBrowserManagerClient` 封装全部 API 调用，CLI 层只做参数解析 + 调用 SDK + 格式化输出。

**理由：** 纯 CLI 实现会导致逻辑和命令耦合，无法被其他 Python 脚本复用。双层架构让 `cloak-cli profile create` 和 `client.profiles.create()` 走同一条代码路径。

### 2. 每操作独立 CDP 连接 而非后台 daemon

**选型：** 每个 `run` 命令独立打开 CDP 连接（打开→执行→关闭），不维护后台长连接进程。

**理由：**
- daemon 方案需额外 ~500-800 行代码（进程管理、IPC 通信、健康检查、断线重连、crash 恢复）
- 每操作 1-2 秒的连接握手开销可接受（浏览器进程持续运行，页面状态自然保持）
- `batch` 命令解决链式操作的延迟问题：单次连接内顺序执行多条命令
- `client.connect()` 返回 raw Browser 对象，SDK 用户可自行实现长连接场景

### 3. snapshot 输出兼容 agent-browser 格式

**选型：** `snapshot` 输出 accessibility tree + `@ref` 标记，格式与 agent-browser 兼容。

**理由：** agent-browser 的 `snapshot` → `click @ref` 工作流已被 AI agent 生态广泛使用。格式兼容可让现有 agent 工具链直接切换。

### 4. Typer + Rich 作为 CLI 框架

**选型：** Typer 构建 CLI，Rich 做终端输出。

**理由：** Typer 原生支持 async/await、类型注解自动生成帮助信息、子命令分组清晰。Rich 提供表格（`rich.table.Table`）、JSON 语法高亮、彩色输出。

### 5. 独立仓库 而非内嵌到现有 cloakbrowser 包

**选型：** 新建 `CloakCLI` 仓库，独立于 `CloakBrowser` 和 `CloakBrowser-Manager`。

**理由：** `cloakbrowser` 是浏览器二进制/SDK，Manager 是 Web 服务，CLI 是客户端工具——三者迭代周期独立。内嵌会引入不必要的依赖膨胀。平级依赖关系清晰。

## 风险 / 权衡

- **[风险] `connect_and_humanize` 尚未实现** → 前置依赖 Plan B。v0 可手动调用 `connect_over_cdp` + `humanize_browser` 两步完成，后续切换至一行版本
- **[风险] 每操作独立连接延迟较高** → `batch` 命令覆盖链式操作场景；v1 可评估 daemon 模式
- **[权衡] CLI 不支持 `--human-config` 覆盖参数** → humanize 配置完全从 Manager profile 读取，保持 CLI 参数简洁。高级用户用 `from cloakcli import CloakBrowserManagerClient` 自行调用 `connect()`
- **[风险] Manager API 变更可能导致客户端不兼容** → SDK 的 Pydantic 模型与 Manager `models.py` 显式对齐，集成测试覆盖版本兼容性

## 项目结构

```
CloakCLI/
├── pyproject.toml
├── README.md
├── LICENSE
└── cloakcli/
    ├── __init__.py          # 导出 Client, Config, __version__
    ├── client.py            # SDK 核心: CloakBrowserManagerClient
    ├── config.py            # ConfigLoader（YAML → 环境变量 → CLI）
    ├── models.py            # Pydantic 数据模型
    ├── errors.py            # 自定义异常类
    ├── utils.py             # 纯工具函数（表格格式化、JSON 输出等）
    └── cmd/
        ├── __init__.py
        ├── main.py          # Typer 入口 + 全局选项
        ├── profile.py       # profile 子命令组
        ├── browser.py       # launch / stop / status
        ├── clipboard.py     # clipboard read / write
        ├── config_cmd.py    # config show / path
        └── run/
            ├── __init__.py  # run 命令组 + batch
            ├── nav.py       # open, back, forward, reload
            ├── interact.py  # click, dblclick, type, fill, press, hover, focus, select, check, uncheck
            ├── info.py      # get text, html, value, attr, title, url, count, box
            ├── capture.py   # snapshot, screenshot, pdf, eval
            ├── tab.py       # tab list, tab new, tab switch, tab close, window new
            └── util.py      # wait, scroll, scrollintoview
```

## 依赖

```toml
[project]
name = "cloak-cli"
dependencies = [
    "cloakbrowser>=0.3.31",   # connect_and_humanize, humanize_browser, humanize_context
    "playwright",             # connect_over_cdp
    "httpx",                  # Manager REST API
    "typer[all]>=0.12",      # CLI
    "rich",                   # 格式化输出
    "pydantic>=2.0",          # 数据模型
    "pyyaml>=6.0",            # 配置文件
]

[project.scripts]
cloak-cli = "cloakcli.cmd.main:main"
```

## 数据流

```
cloak-cli run my-profile click "#btn"
  → ConfigLoader.load() 解析 host/token
  → RunAPI.click("my-profile", "#btn")
    ┌─────────────────────────────────────────────┐
    │ 1. httpx GET /api/profiles/my-profile       │
    │    → 读取 humanize / human_preset 配置      │
    ├─────────────────────────────────────────────┤
    │ 2. httpx GET /api/profiles/my-profile/cdp   │
    │    → 获取 cdp_url                           │
    ├─────────────────────────────────────────────┤
    │ 3. pw.chromium.connect_over_cdp(cdp_url)    │
    ├─────────────────────────────────────────────┤
    │ 4. cloakbrowser.connect_and_humanize(...)    │
    │    （--fast 模式跳过）                       │
    │    → click() → Bézier 轨迹                  │
    │    → type() → 随机延迟 + 误触                │
    ├─────────────────────────────────────────────┤
    │ 5. page.click("#btn")                        │
    ├─────────────────────────────────────────────┤
    │ 6. browser.close()                           │
    └─────────────────────────────────────────────┘
```
