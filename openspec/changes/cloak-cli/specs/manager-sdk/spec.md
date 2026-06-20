# manager-sdk

Manager REST API 的 Python SDK，提供 `CloakBrowserManagerClient` 类用于编程调用 Manager 的全部接口。

## ADDED Requirements

### Requirement: Profile CRUD 操作

SDK 必须提供对 Profile 资源的完整 CRUD 操作。

#### Scenario: 列出所有 profiles

- **WHEN** 调用 `client.profiles.list()`
- **THEN** SDK 向 `GET /api/profiles` 发起 HTTP 请求，携带 `Authorization: Bearer <token>` 请求头（若 token 已配置）
- **THEN** 返回 `list[Profile]` 对象列表，包含 id、name、status、tags 等所有字段

#### Scenario: 获取单个 profile

- **WHEN** 调用 `client.profiles.get("profile-id")`
- **THEN** SDK 向 `GET /api/profiles/profile-id` 发起 HTTP 请求
- **THEN** 返回单个 `Profile` 对象
- **THEN** 若 profile 不存在，抛出 `NotFoundError` 异常

#### Scenario: 创建 profile

- **WHEN** 调用 `client.profiles.create(name="test", proxy="http://proxy:8080", humanize=True)`
- **THEN** SDK 向 `POST /api/profiles` 发起 HTTP 请求，JSON body 包含所有传入字段
- **THEN** 返回新创建的 `Profile` 对象（状态码 201）
- **THEN** 未传的字段使用 Manager 侧默认值

#### Scenario: 更新 profile

- **WHEN** 调用 `client.profiles.update("profile-id", name="renamed", humanize=False)`
- **THEN** SDK 向 `PUT /api/profiles/profile-id` 发起 HTTP 请求，JSON body 仅包含显式传入的字段（`exclude_unset=True`）
- **THEN** 返回更新后的 `Profile` 对象

#### Scenario: 删除 profile

- **WHEN** 调用 `client.profiles.delete("profile-id")`
- **THEN** SDK 向 `DELETE /api/profiles/profile-id` 发起 HTTP 请求
- **THEN** 返回 `True`
- **THEN** `force=True` 时不要求用户确认

### Requirement: 浏览器生命周期控制

SDK 必须提供 launch、stop 和 status 操作。

#### Scenario: 启动浏览器

- **WHEN** 调用 `client.launch("profile-id")`
- **THEN** SDK 向 `POST /api/profiles/profile-id/launch` 发起 HTTP 请求
- **THEN** 返回 `LaunchResult` 对象，包含 `profile_id`、`status`、`vnc_ws_port`、`display`、`cdp_url`

#### Scenario: 停止浏览器

- **WHEN** 调用 `client.stop("profile-id")`
- **THEN** SDK 向 `POST /api/profiles/profile-id/stop` 发起 HTTP 请求
- **THEN** 返回 `True`

#### Scenario: 查询状态

- **WHEN** 调用 `client.status()`（无参数）
- **THEN** SDK 向 `GET /api/status` 发起 HTTP 请求，返回 `SystemStatus`（running_count, binary_version, profiles_total）

- **WHEN** 调用 `client.status("profile-id")`（带参数）
- **THEN** SDK 向 `GET /api/profiles/profile-id/status` 发起 HTTP 请求，返回 `ProfileStatus`（status, vnc_ws_port, display, cdp_url）

### Requirement: CDP 连接与 humanize

SDK 必须提供通过 CDP 连接到运行中浏览器并自动应用 humanize 的能力。

#### Scenario: 连接并启用 humanize

- **WHEN** 调用 `await client.connect("profile-id")`
- **THEN** SDK 先从 `GET /api/profiles/profile-id` 获取 `humanize` 和 `human_preset` 配置
- **THEN** SDK 从 `GET /api/profiles/profile-id/cdp` 获取 CDP WebSocket URL
- **THEN** SDK 调用 `pw.chromium.connect_over_cdp(cdp_url)` 获取 Playwright Browser
- **THEN** SDK 调用 `cloakbrowser.connect_and_humanize(cdp_url, human_preset=...)` 应用 humanize patch
- **THEN** 返回已 humanize 的 Playwright Browser 对象，用户可自行操作

### Requirement: 剪贴板操作

SDK 必须提供剪贴板读写功能。

#### Scenario: 读取剪贴板

- **WHEN** 调用 `client.clipboard.read("profile-id")`
- **THEN** SDK 向 `GET /api/profiles/profile-id/clipboard` 发起 HTTP 请求
- **THEN** 返回剪贴板中的文本字符串

#### Scenario: 写入剪贴板

- **WHEN** 调用 `client.clipboard.write("profile-id", "text to paste")`
- **THEN** SDK 向 `POST /api/profiles/profile-id/clipboard` 发起 HTTP 请求，body 为 `{"text": "text to paste"}`
- **THEN** 文本长度超过 1MB 时抛出 `ValueError`

### Requirement: 鉴权处理

SDK 必须正确处理 Manager 的 Bearer token 鉴权。

#### Scenario: 携带 token 请求

- **WHEN** 初始化 `CloakBrowserManagerClient(host="...", token="secret")`
- **THEN** 所有 HTTP 请求必须携带 `Authorization: Bearer secret` 请求头

#### Scenario: 无 token 请求

- **WHEN** 初始化 `CloakBrowserManagerClient(host="...", token=None)`
- **THEN** 请求不携带 Authorization 请求头

#### Scenario: 鉴权失败

- **WHEN** Manager 返回 401 Unauthorized
- **THEN** SDK 抛出 `AuthenticationError` 异常

### Requirement: 错误处理

SDK 必须将 HTTP 错误状态码映射为明确的异常类型。

#### Scenario: 通用错误映射

- **WHEN** Manager 返回 4xx/5xx
- **THEN** SDK 抛出对应的异常：401 → `AuthenticationError`，404 → `NotFoundError`，409 → `ConflictError`，其他 → `APIError`
