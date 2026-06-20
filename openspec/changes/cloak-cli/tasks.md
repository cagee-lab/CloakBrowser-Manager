# 实施任务

## 1. 项目搭建

- [ ] 1.1 创建仓库目录结构和 `pyproject.toml`（包名 `cloak-cli`，入口点 `cloak-cli = "cloakcli.cmd.main:main"`，依赖声明）
- [ ] 1.2 创建 `cloakcli/` 包目录和 `cmd/`、`cmd/run/` 子目录结构及 `__init__.py` 文件
- [ ] 1.3 确认 Plan B 前置依赖已就绪（`cloakbrowser` 的 `connect_and_humanize`、`humanize_browser`、`humanize_context` 已合并到主分支并发布）

## 2. SDK 核心

- [ ] 2.1 实现 `models.py`：Pydantic 模型（`Profile`、`ProfileCreate`、`ProfileUpdate`、`TagCreate`、`TagResponse`、`LaunchResult`、`SystemStatus`、`ProfileStatus`、`ClipboardRequest`）与 Manager `backend/models.py` 对齐
- [ ] 2.2 实现 `errors.py`：异常类（`APIError`、`AuthenticationError`、`NotFoundError`、`ConflictError`）
- [ ] 2.3 实现 `client.py` — ProfileAPI 子命名空间：`profiles.list()`、`.get()`、`.create()`、`.update()`、`.delete()`
- [ ] 2.4 实现 `client.py` — 浏览器生命周期：`launch()`、`stop()`、`status()`
- [ ] 2.5 实现 `client.py` — 剪贴板：`clipboard.read()`、`.write()`
- [ ] 2.6 实现 `client.py` — CDP 连接：`connect()`（获取 profile 配置 + CDP URL + `connect_over_cdp` + humanize）
- [ ] 2.7 实现 `client.py` — RunAPI 子命名空间：`run.open()`、`.click()`、`.type()`、`.fill()`、`.snapshot()`、`.screenshot()`、`.tab_*()`、`.batch()` 等，支持 `fast` 参数跳过 humanize
- [ ] 2.8 实现 `utils.py`：`format_table()`（Rich Table 输出）、`print_json()`（JSON 格式化）、`resolve_ref()`（@ref → CSS selector 解析）

## 3. 配置系统

- [ ] 3.1 实现 `config.py` — `Config` 类和 `ConfigLoader`：YAML 解析（`~/.cloakcli/config.yaml`）→ 环境变量读取（`CLOAKBROWSER_HOST`、`CLOAKBROWSER_TOKEN`）→ 默认值，优先级覆盖逻辑
- [ ] 3.2 实现 `config.py` — 多 profile 支持（`default`、自定义 profile），`--profile` 参数切换

## 4. CLI 入口与配置命令

- [ ] 4.1 实现 `cmd/main.py`：Typer 应用入口，注册全局选项（`--host`、`--token`、`--profile`），自动注入 `ConfigLoader` 到子命令
- [ ] 4.2 实现 `cmd/config_cmd.py`：`config show`（显示当前 host、token 脱敏、profile 名称、配置来源）、`config path`（显示配置文件路径）

## 5. CLI — Profile 命令

- [ ] 5.1 实现 `cmd/profile.py`：`profile list`（表格输出，含 id、name、status、proxy、tags）
- [ ] 5.2 实现 `cmd/profile.py`：`profile get <id>`（详细视图）
- [ ] 5.3 实现 `cmd/profile.py`：`profile create`（支持 --name、--proxy、--timezone、--locale、--platform、--screen-*、--humanize、--human-preset、--headless、--geoip、--auto-launch、--seed、--user-agent、--tag）
- [ ] 5.4 实现 `cmd/profile.py`：`profile update <id>`（部分更新，`model_dump(exclude_unset=True)`）
- [ ] 5.5 实现 `cmd/profile.py`：`profile delete <id> [--force]`

## 6. CLI — 浏览器生命周期命令

- [ ] 6.1 实现 `cmd/browser.py`：`launch <id>`（输出 LaunchResult 摘要：cdp_url、vnc_ws_port）
- [ ] 6.2 实现 `cmd/browser.py`：`stop <id>`
- [ ] 6.3 实现 `cmd/browser.py`：`status [id]`（无参数时系统状态，有参数时单 profile 状态）

## 7. CLI — 浏览器自动化 Run 命令

- [ ] 7.1 实现 `cmd/run/__init__.py`：`run` 命令组注册 + `batch` 命令（JSON 文件解析、单连接批量执行）
- [ ] 7.2 实现 `cmd/run/nav.py`：`open <url>`、`back`、`forward`、`reload`
- [ ] 7.3 实现 `cmd/run/interact.py`：`click`、`dblclick`、`type`、`fill`、`press`、`hover`、`focus`、`select`、`check`、`uncheck`
- [ ] 7.4 实现 `cmd/run/info.py`：`get text|html|value|attr|title|url|count|box`
- [ ] 7.5 实现 `cmd/run/capture.py`：`snapshot`（accessibility tree + @ref 输出）`screenshot`、`pdf`、`eval`
- [ ] 7.6 实现 `cmd/run/tab.py`：`tab`（列表）、`tab new`、`tab switch`、`tab close`、`window new`
- [ ] 7.7 实现 `cmd/run/util.py`：`wait`（毫秒/选择器/网络空闲/状态）、`scroll`（方向+像素）、`scrollintoview`

## 8. CLI — 剪贴板命令

- [ ] 8.1 实现 `cmd/clipboard.py`：`clipboard read <id>`（`--json` 输出）、`clipboard write <id> <text>`

## 9. 包导出

- [ ] 9.1 实现 `__init__.py`：导出 `CloakBrowserManagerClient`、`Config`、`__version__`

## 10. 测试

- [ ] 10.1 `tests/test_config.py`：ConfigLoader 单元测试（YAML 加载、环境变量覆盖、CLI 参数覆盖、不存在 profile、多 profile 切换）
- [ ] 10.2 `tests/test_client.py`：Client 单元测试（Mock httpx，测试所有 API 方法：profiles CRUD、launch/stop/status、clipboard、鉴权头、错误映射）
- [ ] 10.3 `tests/test_models.py`：模型反序列化测试（Manager 真实 JSON → Pydantic 校验）
- [ ] 10.4 `tests/test_cli.py`：CLI 调用测试（Typer CliRunner，验证各命令参数解析和输出格式）

## 11. 文档

- [ ] 11.1 编写 `README.md`：安装方式、快速开始、CLI 命令参考、SDK 用法示例
- [ ] 11.2 创建 `examples/basic_usage.py`：SDK 使用示例（profile 管理 + CDP 连接 + 浏览器操作）
- [ ] 11.3 创建 `examples/cli_workflow.sh`：CLI 典型工作流脚本（profile 创建 → launch → 操作 → stop → 清理）
