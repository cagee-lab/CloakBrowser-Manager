# browser-automation

基于 CDP 的浏览器自动化操作能力。CLI 通过 `run` 子命令暴露，SDK 通过 `client.run.*` 方法暴露。每个操作独立建立 CDP 连接，自动集成 humanize 人类化行为。

## ADDED Requirements

### Requirement: 页面导航

系统必须提供页面导航操作：打开 URL、后退、前进、刷新。

#### Scenario: 打开 URL

- **WHEN** 执行 `run <id> open <url>` 或调用 `client.run.open("id", url)`
- **THEN** 系统连接 CDP，获取活动页面，执行 `page.goto(url)`
- **THEN** 导航完成后关闭 CDP 连接

#### Scenario: 后退

- **WHEN** 执行 `run <id> back` 或调用 `client.run.back("id")`
- **THEN** 系统连接 CDP，获取活动页面，执行 `page.go_back()`

### Requirement: 快照

系统必须提供与 agent-browser 兼容的 accessibility tree 快照功能。

#### Scenario: 完整快照

- **WHEN** 执行 `run <id> snapshot` 或调用 `client.run.snapshot("id")`
- **THEN** 输出完整的 accessibility tree，每个节点格式为 `- <role> "<name>" [@eN]`
- **THEN** 每个可交互节点分配唯一 @ref 引用（@e1, @e2, ...）
- **THEN** 链接节点附 `-> url` 信息

#### Scenario: 仅可交互元素

- **WHEN** 执行 `run <id> snapshot -i` 或调用 `client.run.snapshot("id", interactive_only=True)`
- **THEN** 仅输出可交互元素（按钮、输入框、链接、下拉框等），跳空纯结构容器

#### Scenario: 紧凑模式

- **WHEN** 执行 `run <id> snapshot -c` 或调用 `client.run.snapshot("id", compact=True)`
- **THEN** 省略空的结构化容器节点（无文本、无可交互子节点的 div、section 等）

#### Scenario: 深度限制

- **WHEN** 执行 `run <id> snapshot -d 3` 或调用 `client.run.snapshot("id", max_depth=3)`
- **THEN** 仅输出深度不超过 3 层的节点

#### Scenario: CSS 范围限制

- **WHEN** 执行 `run <id> snapshot -s "#main"` 或调用 `client.run.snapshot("id", scope="#main")`
- **THEN** 仅输出匹配 `#main` 选择器的元素及其子节点

### Requirement: 元素交互（人类化）

系统必须提供带有人类化行为的元素交互操作。`--fast` 模式跳过人类化。

#### Scenario: 点击

- **WHEN** 执行 `run <id> click <sel>`（默认模式）
- **THEN** 系统连接 CDP 并应用 humanize patch
- **THEN** 执行 `page.click(sel)` ——鼠标沿 Bézier 曲线移动到目标、包含 aim delay 和随机 hold time
- **WHEN** 执行 `run <id> --fast click <sel>`
- **THEN** 跳过 humanize patch，执行原生 `page.click(sel)`

#### Scenario: 逐字键入

- **WHEN** 执行 `run <id> type <sel> <text>`（默认模式）
- **THEN** 聚焦指定元素，逐字符键入文本——每次按键带随机延迟、偶尔模拟误触+删除+重打
- **WHEN** 执行 `run <id> --fast type <sel> <text>`
- **THEN** 跳过 humanize，执行原生 `page.type(sel, text)`

#### Scenario: 清空填入

- **WHEN** 执行 `run <id> fill <sel> <text>`（默认模式）
- **THEN** 先清空输入框（三击 + Backspace），再逐字符键入
- **WHEN** 执行 `run <id> --fast fill <sel> <text>`
- **THEN** 跳过 humanize，执行原生 `page.fill(sel, text)`

#### Scenario: 按键

- **WHEN** 执行 `run <id> press <key>`
- **THEN** 支持特殊键名：Enter、Tab、Escape、Backspace、Delete、ArrowUp/Down/Left/Right
- **THEN** 支持组合键：Control+a、Shift+Tab、Meta+v 等

#### Scenario: 其他交互操作

- **WHEN** 执行 `dblclick <sel>`、`hover <sel>`、`focus <sel>`
- **THEN** 默认模式均带 humanize，`--fast` 模式跳过

#### Scenario: 表单控件操作

- **WHEN** 执行 `select <sel> <value>`、`check <sel>`、`uncheck <sel>`
- **THEN** 默认模式均带 humanize，`--fast` 模式跳过

### Requirement: 信息获取

系统必须提供从当前页面获取信息的能力。

#### Scenario: 获取元素信息

- **WHEN** 执行 `get text|html|value|attr|box <sel> [name]`
- **THEN** 返回对应的元素文本、innerHTML、当前值、属性值或边界框坐标
- **THEN** `--json` 标志输出 JSON 格式

#### Scenario: 获取页面信息

- **WHEN** 执行 `get title`、`get url`、`get count <sel>`
- **THEN** 返回页面标题、当前 URL 或匹配元素数量
- **THEN** `--json` 标志输出 JSON 格式

### Requirement: 截图与导出

系统必须提供截图和 PDF 导出功能。

#### Scenario: 截图

- **WHEN** 执行 `run <id> screenshot [path]`
- **THEN** 对当前页面截图并保存到指定路径（默认 `screenshot-<timestamp>.png`）
- **THEN** `--full` 参数截取全页面（非仅可视区域）

#### Scenario: PDF

- **WHEN** 执行 `run <id> pdf <path>`
- **THEN** 将当前页面输出为 PDF 并保存到指定路径

### Requirement: 标签页管理

系统必须提供标签页和窗口的管理操作。

#### Scenario: 列出标签页

- **WHEN** 执行 `run <id> tab` 或调用 `client.run.tab_list("id")`
- **THEN** 列出所有标签页，每行格式：`tN: "标题" [URL] (active)`
- **THEN** 活动标签页标记 `(active)`

#### Scenario: 新建标签页

- **WHEN** 执行 `run <id> tab new <url>` 或调用 `client.run.tab_new("id", url)`
- **THEN** 创建新标签页并导航到指定 URL
- **WHEN** 执行 `run <id> tab new`（无 URL）
- **THEN** 创建空白标签页

#### Scenario: 切换标签页

- **WHEN** 执行 `run <id> tab switch t2` 或调用 `client.run.tab_switch("id", "t2")`
- **THEN** 切换到第 2 个标签页
- **THEN** 支持标签 label 引用

#### Scenario: 关闭标签页

- **WHEN** 执行 `run <id> tab close t1` 或调用 `client.run.tab_close("id", "t1")`
- **THEN** 关闭指定标签页
- **WHEN** 执行 `run <id> tab close`（无参数）
- **THEN** 关闭当前活动标签页

#### Scenario: 新建窗口

- **WHEN** 执行 `run <id> window new` 或调用 `client.run.window_new("id")`
- **THEN** 在新窗口中创建标签页

### Requirement: 批处理

系统必须支持在单次 CDP 连接中批量执行多条操作。

#### Scenario: 批处理执行

- **WHEN** 执行 `run <id> batch <file.json>` 或调用 `client.run.batch("id", commands)`
- **THEN** 建立一次 CDP 连接，应用 humanize 一次
- **THEN** 在同一连接内按顺序执行 JSON 文件中的所有命令
- **THEN** 所有命令共享同一 humanize 上下文（连续操作的鼠标位置、键盘状态保持自然）
- **WHEN** 执行 `run <id> --fast batch <file.json>`
- **THEN** 跳过 humanize，所有命令瞬时执行

#### Scenario: 批处理 JSON 格式

- **WHEN** batch 文件包含 `[["open", "url"], ["click", "#btn"], ["snapshot", "-i"]]`
- **THEN** 系统按数组顺序解析并执行命令，数组格式为 `["命令名", "参数1", "参数2", ...]`
- **THEN** 格式与 agent-browser batch 兼容

### Requirement: eval 执行

系统必须支持在当前页面执行 JavaScript。

#### Scenario: 执行 JavaScript

- **WHEN** 执行 `run <id> eval <code>` 或调用 `client.run.eval("id", code)`
- **THEN** 在当前页面上下文中执行 JavaScript 代码
- **THEN** `--json` 标志时输出 JSON 序列化后的返回值

### Requirement: 等待与滚动

系统必须提供等待和滚动操作。

#### Scenario: 等待毫秒

- **WHEN** 执行 `run <id> wait 2000`
- **THEN** 暂停 2000 毫秒后返回

#### Scenario: 等待选择器

- **WHEN** 执行 `run <id> wait "#result"`
- **THEN** 等待指定元素在页面上可见后返回
- **THEN** `--state hidden` 等待元素消失

#### Scenario: 等待网络空闲

- **WHEN** 执行 `run <id> wait --load networkidle`
- **THEN** 等待网络请求完成后返回

#### Scenario: 滚动

- **WHEN** 执行 `run <id> scroll down 300` 或 `run <id> scroll up 200`
- **THEN** 页面向指定方向滚动指定像素（默认模式带人类化平滑滚动）
- **WHEN** 执行 `run <id> scrollintoview <sel>`
- **THEN** 滚动页面直到指定元素进入可视区域
