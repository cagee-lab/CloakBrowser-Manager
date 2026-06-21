# cli-configuration

多源配置系统，支持 YAML 配置文件、环境变量和 CLI 参数三级配置源，优先级可覆盖。

## ADDED Requirements

### Requirement: 多源配置加载

系统必须按优先级从高到低依次尝试 CLI 参数 > 环境变量 > 配置文件 > 默认值。

#### Scenario: 仅 CLI 参数

- **WHEN** 执行 `cloak-cli --host http://remote:8080 --token secret profile list`
- **THEN** 使用 `http://remote:8080` 作为 host，`secret` 作为 token
- **THEN** 不读取配置文件和环境变量

#### Scenario: 仅环境变量

- **WHEN** 设置 `CLOAKBROWSER_HOST=http://staging:8080` 和 `CLOAKBROWSER_TOKEN=env-token`
- **WHEN** 执行 `cloak-cli profile list`（无 --host/--token 参数，无配置文件）
- **THEN** 使用环境变量值

#### Scenario: 仅配置文件

- **WHEN** 无 CLI 参数，无环境变量
- **WHEN** `~/.cloakcli/config.yaml` 中 `default` profile 已配置 host 和 token
- **THEN** 使用配置文件中的值

#### Scenario: 默认值

- **WHEN** 无 CLI 参数、无环境变量、无配置文件
- **THEN** host 默认 `http://localhost:8080`，token 默认 `None`（无鉴权模式）

### Requirement: 配置 profile 切换

系统必须支持通过 `--profile` 参数切换配置文件中的不同环境。

#### Scenario: 切换到指定 profile

- **WHEN** 配置文件中有 `staging` profile
- **WHEN** 执行 `cloak-cli --profile staging profile list`
- **THEN** 加载 `staging` profile 下的 host 和 token

#### Scenario: 默认 profile

- **WHEN** 未指定 `--profile` 参数
- **THEN** 加载 `default` profile

### Requirement: 配置文件格式

配置文件必须是合法的 YAML 文件，位于 `~/.cloakcli/config.yaml`。

#### Scenario: 单 profile 配置

- **WHEN** 配置文件内容为：
```yaml
default:
  host: http://localhost:8080
  token: my-token
```
- **THEN** `Config.load()` 返回 host=`http://localhost:8080`，token=`my-token`

#### Scenario: 多 profile 配置

- **WHEN** 配置文件内容为：
```yaml
default:
  host: http://localhost:8080
staging:
  host: https://staging.example.com
  token: staging-token
```
- **THEN** `Config.load("staging")` 返回 host=`https://staging.example.com`，token=`staging-token`
- **THEN** `Config.load()` 返回 default 的值

### Requirement: config 命令

系统必须提供查看当前配置的 CLI 命令。

#### Scenario: 显示当前配置

- **WHEN** 执行 `cloak-cli config show`
- **THEN** 输出当前解析后的 host、token（脱敏显示）、使用的 profile 名称、配置来源（CLI/ENV/YAML/default）

#### Scenario: 显示配置文件路径

- **WHEN** 执行 `cloak-cli config path`
- **THEN** 输出配置文件的完整路径（`~/.cloakcli/config.yaml`）

### Requirement: Config 类编程接口

Config 类必须可从 SDK 层导入使用。

#### Scenario: 编程加载配置

- **WHEN** 调用 `Config.load("staging")` 或 `Config.load()`
- **THEN** 返回包含 `host` 和 `token` 属性的 Config 对象
- **THEN** 加载逻辑与 CLI 一致（优先级、默认值）

#### Scenario: 编程创建 Config

- **WHEN** 调用 `Config(host="http://x:8080", token="t")`
- **THEN** 直接使用传入值，不读取配置文件或环境变量
