## 动机

CloakBrowser Manager 目前没有 CLI 客户端——用户只能通过 React Web UI 或原始 HTTP/WebSocket 调用来交互。运维团队和脚本开发者需要一个命令行工具来完成 profile 管理、浏览器生命周期控制以及自动化的浏览器交互（集成 humanize 人类化行为）。一套 CLI + Python SDK 能支撑 Shell 脚本、CI 自动化以及基于 Manager 的编程工具链。

## 变更内容

- **新建 Python 包** `cloak-cli`，包含 SDK 核心（`CloakBrowserManagerClient`）和 Typer CLI（`cloak-cli` 命令）
- **Profile CRUD**：通过 CLI 和 SDK 进行 list、get、create、update、delete
- **浏览器生命周期**：launch、stop、status 命令
- **浏览器自动化**：通过 CDP 连接执行浏览器操作，自动集成 humanize——open、click、type、fill、snapshot、screenshot、tab 管理、batch 批量执行等
- **`--fast` 标志**：所有自动化命令支持跳过 humanize，用于测试场景
- **多源配置**：YAML 配置文件 → 环境变量 → CLI 参数，优先级可覆盖

## 能力划分

### 新增能力

- `manager-sdk`：封装 Manager 完整 REST API 的 Python SDK——profile CRUD、浏览器生命周期、剪贴板、CDP 连接并自动应用 humanize。包含 Pydantic 数据模型、ConfigLoader 和基于 httpx 的 HTTP 客户端。
- `browser-automation`：基于 CDP 的浏览器操作能力——导航（open/back/forward/reload）、交互（click/type/fill/press/hover/focus/select/check/uncheck）、信息获取（snapshot/get text/html/value/attr/title/url/count/box）、截图导出（screenshot/pdf）、标签页/窗口管理、batch 批量执行、eval。
- `cli-configuration`：多源配置系统，支持 YAML 文件（`~/.cloakcli/config.yaml`）、环境变量（`CLOAKBROWSER_HOST`、`CLOAKBROWSER_TOKEN`）和 CLI 参数（`--host`、`--token`、`--profile`）。优先级：CLI > 环境变量 > 配置文件 > 默认值。

### 修改的能力

<!-- 无现有能力需要修改 -->

## 影响范围

- **新建仓库**：`CloakCLI`——独立包，不修改 Manager 或 CloakBrowser 现有代码
- **依赖**：`cloakbrowser >= 0.3.31`（`connect_and_humanize`、`humanize_browser`、`humanize_context`）、`playwright`（CDP 连接）、`httpx`、`typer`、`rich`、`pydantic`、`pyyaml`
- **前置条件**：Plan B 的 `connect_and_humanize` / `humanize_browser` / `humanize_context` 函数需先在 `cloakbrowser/browser.py` 中实现
- **API 面**：消费现有 Manager 的 REST 和 WebSocket 端点——Manager 无需修改
