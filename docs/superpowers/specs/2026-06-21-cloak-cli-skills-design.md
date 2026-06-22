# CloakCLI Agent Skills — 设计文档

为分发到其他 agent 中使用而编写的三个 cloak-cli skill。

## 目标

让 agent 能通过 cloak-cli 命令行操作 CloakBrowser Manager——管理 profile、启动浏览器、在浏览器中执行自动化操作。

目标使用者是 **直接执行 CLI 命令操作浏览器** 的 agent（场景 B）。

## Skill 架构

三个 skill，按命令组拆分：

| Skill | 文件 | 触发条件 | 内容量 |
|-------|------|---------|--------|
| `cloak-cli-profiles` | `cloak-cli-profiles/SKILL.md` | 需要管理 profile、启动/停止浏览器、配置连接 | ~250 词 |
| `cloak-cli-automation` | `cloak-cli-automation/SKILL.md` | 需要在浏览器中操作页面（导航/交互/快照/获取信息） | ~400 词 |
| `cloak-cli-batch` | `cloak-cli-batch/SKILL.md` | 需要批量执行多步操作、复杂自动化流程 | ~300 词 |

### 跨 Skill 一致性

- 每个 skill 开头都有快速连接模式（环境变量 vs 配置文件 vs CLI 参数）
- 都用 `@ref` 引用（来自 snapshot 的 `@eN`）作为主要元素定位方式
- 都区分 `--fast`（无 humanize）和默认（有 humanize）模式
- 命令速查表统一格式

---

## Skill 1: `cloak-cli-profiles`

Profile 管理与浏览器生命周期。

### 内容结构

1. **快速连接** — 三种配置方式速查（env / config.yaml / --host --token）
2. **工作流：从零创建并启动 profile**
   - `cloak-cli profile create --name "demo" --humanize`
   - `cloak-cli launch <id>`
   - `cloak-cli status <id>`
3. **工作流：管理已有 profile**
   - `cloak-cli profile list`
   - `cloak-cli profile get <id>`
   - `cloak-cli stop <id>`
4. **命令速查表** — 所有 profile/browser 命令的紧凑参考
5. **常见错误** — 401 鉴权失败、profile 不存在、已在运行

---

## Skill 2: `cloak-cli-automation`

浏览器自动化操作（run 子命令）。

### 内容结构

1. **核心概念速览**
   - 所有操作通过 `cloak-cli run <profile-id> <command>` 执行
   - 默认启用 humanize，`--fast` 跳过
   - 元素定位优先用 `@eN` 引用，也可用 CSS 选择器

2. **工作流：探索页面并操作**
   - `snapshot -i` 获取可交互元素 → `click "@e3"` → `type "@e5" "text"` → `press "Enter"`
   - 验证：`snapshot -i` + `screenshot`

3. **工作流：填写并提交表单**
   - `fill`（清空+填入）vs `type`（逐字键入）区别
   - `select` / `check` / `uncheck` 表单控件

4. **工作流：提取页面信息**
   - `get text/html/value/attr/title/url/count/box`

5. **快照选项速查** — `-i` / `-c` / `-d` / `-s` 各选项的适用场景

6. **标签页工作流** — `tab` / `tab new` / `tab switch` / `tab close`

7. **命令速查表** — 所有 run 子命令、参数、`--fast` 支持

8. **常见错误**
   - CSS 选择器找不到元素 → 先 snapshot -i
   - 页面未加载 → 用 wait
   - type vs fill 混淆

---

## Skill 3: `cloak-cli-batch`

批量执行与多步骤自动化。

### 内容结构

1. **核心理念**
   - 单次 CDP 连接，共享 humanize 上下文
   - 比多次 run 调用更高效，行为更真实

2. **工作流：构建 batch JSON 文件**
   - 数组格式 `["命令名", "参数1", ...]`
   - 与 agent-browser 兼容

3. **工作流：执行与验证**
   - `cloak-cli run <id> batch commands.json`
   - `--fast` / `--json` 输出

4. **最佳实践**
   - 以 open/snapshot 开头确认状态
   - 关键步骤后插入检查点
   - wait 放在导航后、交互前

5. **典型场景模板** — 登录、抓取、多页导航

6. **错误处理**
   - 单条失败不中断 batch
   - `--json` 解析每条结果
   - screenshot 辅助定位失败

7. **命令速查表** — batch 支持的所有命令

8. **常见错误**
   - JSON 格式错误
   - 忘记 wait
   - batch 中 fast/humanize 混用

---

## 部署位置

Skills 放在项目的 `.claude/skills/` 目录下，可复制到其他 agent 的同类目录中使用：

```
.claude/skills/
  cloak-cli-profiles/
    SKILL.md
  cloak-cli-automation/
    SKILL.md
  cloak-cli-batch/
    SKILL.md
```

## 不包含的内容

- **SDK 编程模式** — 目标 agent 只用 CLI，不写 Python 代码
- **Manager Web UI 操作** — 仅覆盖 CLI 能力
- **Docker 部署** — 假设 Manager 已经在运行
