# CloakCLI — 设计规格

## Context

CloakBrowser Manager 是一个自托管的浏览器指纹配置文件管理器（FastAPI + React + SQLite + noVNC）。目前用户通过 Web UI 或 HTTP/WebSocket API 与它交互。需要一套 CLI 客户端工具，让运维/脚本用户可以：

1. 在命令行管理 profile（CRUD）
2. 控制浏览器生命周期（launch / stop / status）
3. 通过 CDP 连接执行浏览器自动化操作（导航、点击、输入、截图、快照等），自动集成 humanize 人类化行为

CLI 基于方案 B（SDK 核心 + CLI 薄壳）构建，同时提供 `from cloakcli import CloakBrowserManagerClient` 的 Python SDK。

## 命名约定

| 层级 | 名称 |
|------|------|
| GitHub 仓库 | `CloakCLI` |
| PyPI 包 | `cloak-cli` |
| CLI 命令 | `cloak-cli` |
| Python 包/导入 | `cloakcli` |
| 入口点 | `cloakcli.cmd.main:main` |

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
dependencies = [
    "cloakbrowser>=0.3.31",   # connect_and_humanize(), humanize_browser(), humanize_context()
    "playwright",             # connect_over_cdp()
    "httpx",                  # Manager REST API 调用
    "typer[all]>=0.12",      # CLI 框架
    "rich",                   # 表格输出、彩色终端
    "pydantic>=2.0",          # 数据模型验证
    "pyyaml>=6.0",            # 配置文件解析
]
```

## SDK 核心设计

### `CloakBrowserManagerClient`

```python
from cloakcli import CloakBrowserManagerClient

client = CloakBrowserManagerClient(
    host="http://localhost:8080",
    token="optional-token",
    timeout=30,
)

# === Profile CRUD ===
client.profiles.list()                    # -> list[Profile]
client.profiles.get("id")                 # -> Profile
client.profiles.create(name="...", **kw)  # -> Profile
client.profiles.update("id", **kw)        # -> Profile
client.profiles.delete("id")             # -> bool

# === Browser Lifecycle ===
client.launch("id")            # -> LaunchResult
client.stop("id")              # -> bool
client.status("id")            # -> ProfileStatus (per-profile)
client.status()                # -> SystemStatus (overall)

# === CDP + Humanize ===
browser = await client.connect("id")  # connect_over_cdp + humanize
# 返回：已 patch 的 Playwright Browser（所有操作自动 humanize）

# === Browser Actions (per-operation) ===
await client.run.open("id", "https://example.com")
await client.run.click("id", "#btn")
await client.run.type("id", "#input", "text")
await client.run.fill("id", "#input", "text")
await client.run.snapshot("id", interactive_only=True)
await client.run.screenshot("id", "shot.png")
await client.run.batch("id", [["open", "url"], ["click", "#btn"], ["snapshot", "-i"]])
# 所有 run 方法支持 fast=True 跳过 humanize

# === Tab & Window ===
await client.run.tab_list("id")          # -> list[TabInfo]
await client.run.tab_new("id")           # 打开空白标签页
await client.run.tab_new("id", "url")    # 打开 URL 标签页
await client.run.tab_switch("id", "t1")  # 切换到第 1 个标签页
await client.run.tab_close("id")         # 关闭当前标签页
await client.run.tab_close("id", "t1")   # 关闭指定标签页
await client.run.window_new("id")        # 新建窗口

# === Clipboard ===
client.clipboard.read("id")    # -> str
client.clipboard.write("id", "text")
```

### 关键设计点

**`client.connect()` vs `client.run.xxx()`**:
- `connect()` — 建立长连接，返回 raw Playwright Browser（已 humanize），SDK 用户自行操作
- `run.xxx()` — 每操作独立 CDP 连接（打开→执行→关闭），CLI 底层实现。1-2秒/命令的握手开销可接受。Browser 进程持续运行，页面状态（URL、DOM、cookies）在多次命令间保持

**Humanize 自动配置**: `connect()` 和 `run.xxx()` 都先从 Manager `GET /api/profiles/{id}` 读取该 profile 的 `humanize`/`human_preset` 配置，再调用 `cloakbrowser.connect_and_humanize()` 自动应用。用户无需手动指定

**`--fast` 标志**: `run.xxx()` 支持 `fast=True`，跳过 humanize patch，直接原生 Playwright 操作。用于测试或不需要人类化行为的场景

**`run.batch()`**: 共享一次 CDP 连接 + humanize 上下文，在单个连接内顺序执行多条命令。解决链式操作的低延迟需求，无需引入后台 daemon

### 配置加载（`config.py`）

优先级（高→低）：
```
CLI --host / --token  >  CLOAKBROWSER_HOST / CLOAKBROWSER_TOKEN  >  ~/.cloakcli/config.yaml  >  http://localhost:8080（无鉴权）
```

配置文件格式 `~/.cloakcli/config.yaml`：
```yaml
default:
  host: http://localhost:8080
  token: my-secret

staging:
  host: https://cloak-staging.example.com
  token: staging-token
```

用法：`cloak-cli --profile staging profile list`

`Config` 类公开 API：
```python
from cloakcli import Config

cfg = Config.load("staging")  # 加载指定 profile
cfg = Config.load()           # 自动解析: --profile flag > env > config default
```

### 数据模型（`models.py`）

Pydantic 模型与 Manager 的 `models.py` 保持对齐，作为 client 端的 source of truth：

- `Profile`, `ProfileCreate`, `ProfileUpdate`
- `LaunchResult`, `SystemStatus`, `ProfileStatus`
- `TagCreate`, `TagResponse`
- `ClipboardRequest`

## CLI 命令树

```
cloak-cli
│
├── profile list
│   profile get <id>
│   profile create [--name] [--proxy] [--timezone] [--locale]
│                  [--platform] [--screen-width] [--screen-height]
│                  [--humanize] [--human-preset] [--headless] [--geoip]
│                  [--auto-launch] [--seed] [--user-agent]
│                  [--tag key:color] ...
│   profile update <id> [同上选项，只更新指定的]
│   profile delete <id> [--force]
│
├── launch <id>
│   stop <id>
│   status [id]
│
├── run <id> open <url>              [--fast] [--json]
│   run <id> back                     [--fast]
│   run <id> forward                  [--fast]
│   run <id> reload                   [--fast]
│   run <id> snapshot                 [--fast] [--json] [-i] [-c] [-d N] [-s css]
│   run <id> click <sel>             [--fast]
│   run <id> dblclick <sel>          [--fast]
│   run <id> type <sel> <text>       [--fast]
│   run <id> fill <sel> <text>       [--fast]
│   run <id> press <key>             [--fast]
│   run <id> hover <sel>             [--fast]
│   run <id> focus <sel>             [--fast]
│   run <id> select <sel> <val>      [--fast]
│   run <id> check <sel>             [--fast]
│   run <id> uncheck <sel>           [--fast]
│   run <id> get text <sel>          [--json]
│   run <id> get html <sel>          [--json]
│   run <id> get value <sel>         [--json]
│   run <id> get attr <sel> <name>   [--json]
│   run <id> get title               [--json]
│   run <id> get url                 [--json]
│   run <id> get count <sel>         [--json]
│   run <id> get box <sel>           [--json]
│   run <id> screenshot [path]       [--fast] [--full]
│   run <id> pdf <path>              [--fast]
│   run <id> eval <js>               [--fast] [--json]
│   run <id> wait <ms|sel>           [--fast] [--load load|networkidle] [--state visible|hidden]
│   run <id> scroll <dir> [px]       [--fast]
│   run <id> scrollintoview <sel>    [--fast]
│   run <id> tab                      [--json]
│   run <id> tab new [url]            [--fast]
│   run <id> tab switch <tN|label>   [--fast]
│   run <id> tab close [tN|label]    [--fast]
│   run <id> window new               [--fast]
│   run <id> batch <file.json>       [--fast]
│
├── clipboard read <id>              [--json]
│   clipboard write <id> <text>
│
└── config show
    config path
```

### 全局选项

| 选项 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `--host` | `CLOAKBROWSER_HOST` | `http://localhost:8080` | Manager 地址 |
| `--token` | `CLOAKBROWSER_TOKEN` | — | 鉴权 token |
| `--profile` | — | `default` | 配置 profile（不是浏览器 profile） |

### `--fast` 标志

所有 `run` 子命令支持 `--fast`：
```bash
# 测试时跳过 humanize，瞬时执行
cloak-cli run my-profile --fast click "#btn"
cloak-cli run my-profile --fast batch test-flow.json
```

### `batch` 命令

JSON 文件格式（agent-browser 兼容）：
```json
[
  ["open", "https://example.com/login"],
  ["snapshot", "-i"],
  ["type", "#email", "user@example.com"],
  ["fill", "#password", "pass123"],
  ["click", "#login-btn"],
  ["wait", "--load", "networkidle"],
  ["screenshot", "result.png"]
]
```

```bash
cloak-cli run my-profile batch actions.json
cloak-cli run my-profile --fast batch test-flow.json
```

整个 batch 共享一次 CDP 连接和 humanize 上下文。

### `tab` 命令组

管理浏览器的标签页和窗口。每个标签页用 `tN` 引用（`t1`, `t2`, ...）：

```bash
cloak-cli run my-profile tab
# t1: "Home" [https://example.com] (active)
# t2: "Docs" [https://docs.example.com]

cloak-cli run my-profile tab new "https://news.example.com"   # 打开新标签页
cloak-cli run my-profile tab switch t2                         # 切换到 t2
cloak-cli run my-profile tab close t1                          # 关闭 t1
cloak-cli run my-profile window new                            # 新建窗口
```

`tab new` 不带 URL 则打开空白标签页。`tab close` 不带参数则关闭当前活动标签页。`tab switch` 除了 `tN` 也支持标签 label。

### `snapshot` 命令

输出与 agent-browser 兼容的 accessibility tree：
```
- document [@e1]
  - navigation [@e2]
    - link "Home" [@e3] -> /home
  - main [@e4]
    - heading "Login" [@e5]
    - textbox "Email" [@e6]
    - textbox "Password" [@e7]
    - button "Sign In" [@e8]
  - contentinfo [@e9]
```

选项：`-i` 仅可交互元素、`-c` 紧凑模式、`-d N` 限制深度、`-s css` 限定范围。

## 数据流

### Profile CRUD

```
cloak-cli profile list
  → ConfigLoader.load() 解析 host/token
  → CloakBrowserManagerClient.profiles.list()
    → httpx GET {host}/api/profiles (Authorization: Bearer {token})
    → parse JSON → list[Profile]
  → utils.format_table() 表格输出
```

### 浏览器操作（run click 为例）

```
cloak-cli run my-profile click "#login-btn"
  → ConfigLoader.load() 解析 host/token
  → CloakBrowserManagerClient.run.click("my-profile", "#login-btn")
    ┌─────────────────────────────────────────────┐
    │ 1. httpx GET /api/profiles/my-profile       │
    │    → 读取 humanize / human_preset / headless │
    ├─────────────────────────────────────────────┤
    │ 2. httpx GET /api/profiles/my-profile/cdp   │
    │    → 获取 cdp_url（经过 Manager 代理）      │
    ├─────────────────────────────────────────────┤
    │ 3. pw.chromium.connect_over_cdp(cdp_url)    │
    │    → Playwright Browser 对象                │
    ├─────────────────────────────────────────────┤
    │ 4. cloakbrowser.connect_and_humanize(url,   │
    │       human_preset=..., human_config=...)    │
    │    （--fast 模式跳过此步）                   │
    │    → Browser/Context/Page 全部 monkey-patch  │
    │    → click() → Bézier 轨迹 + aim delay       │
    │    → type() → 随机延迟 + 误触                │
    │    → scroll() → 加速/减速曲线                │
    ├─────────────────────────────────────────────┤
    │ 5. page = browser.contexts[0].pages[0]      │
    │    page.click("#login-btn")                  │
    │    （若未指定 selector: 获取活动元素后点击）  │
    ├─────────────────────────────────────────────┤
    │ 6. browser.close() 释放 CDP 连接            │
    └─────────────────────────────────────────────┘
```

## 与现有代码的关系

### 依赖但无需修改

| 包 | 使用的功能 | 说明 |
|----|-----------|------|
| `cloakbrowser >= 0.3.31` | `connect_and_humanize()`, `humanize_browser()`, `humanize_context()` | Plan B 实现的函数，在 cloabrowser SDK 侧 |
| `cloakbrowser` | `HumanConfig`, `resolve_human_config` | humanize 配置类型 |
| Manager API | 全部 REST 和 CDP WebSocket 端点 | 无需修改 |

### 前置依赖：Plan B 需先落地

`CloakCLI` 的 `client.connect()` 和 `client.run.xxx()` 依赖 `cloakbrowser` 包中的以下 3 个公开函数：

| 函数 | 位置 | 用途 |
|------|------|------|
| `humanize_context(ctx, preset, config)` | `cloakbrowser/browser.py` | 对已有 BrowserContext 应用 humanize |
| `humanize_browser(browser, preset, config)` | `cloakbrowser/browser.py` | 对已有 Browser 应用 humanize（覆盖所有 contexts） |
| `connect_and_humanize(url, preset, config, **kwargs)` | `cloakbrowser/browser.py` | `connect_over_cdp()` + `humanize_browser()` 一行搞定 |

以及一个内部 helper `_humanize(obj, preset, config)` 消除 `launch*()` 四处的重复代码。

## 验证计划

### 单元测试

1. **ConfigLoader**: 测试 YAML 文件加载、环境变量覆盖、CLI 参数覆盖、不存在的 profile 报错
2. **Client**: Mock httpx 测试所有 API 方法（profiles CRUD, launch, stop, status, clipboard）
3. **Models**: 验证 Manager 返回的 JSON → Pydantic 模型反序列化正确
4. **Utils**: format_table、print_json 输出格式验证

### 集成测试（需要 Manager + CloakBrowser 运行）

1. 创建 profile → launch → status → stop → delete 完整流程
2. `run click` / `run type` / `run fill` 验证操作成功执行
3. `run --fast click` 验证瞬时执行（无 humanize 延迟）
4. `run snapshot -i` 验证输出格式与 agent-browser 兼容
5. `run batch` 验证多命令共享连接
6. clipboard read/write 验证数据正确传输
7. 鉴权模式（AUTH_TOKEN 设置时）验证 401 → 200 正确切换

### CLI 冒烟测试

```bash
# 无鉴权模式
cloak-cli profile list
cloak-cli profile create --name "test" --humanize
cloak-cli launch <id>
cloak-cli run <id> open "https://example.com"
cloak-cli run <id> snapshot -i
cloak-cli run <id> screenshot
cloak-cli run <id> --fast click "body"
cloak-cli stop <id>
cloak-cli profile delete <id> --force
```
