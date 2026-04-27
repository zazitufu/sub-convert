# sub-convert 中文说明

`sub-convert` 是一个部署在服务器上的订阅转换器。

它会监控一个目录中的无后缀 Base64 订阅源文件，然后自动生成：

- Clash / Mihomo 使用的 `.yaml`
- sing-box 使用的 `.json`

这个公开仓库已经做过脱敏处理：

- 不包含真实线上域名
- 不包含真实服务器 IP
- 不包含私有部署路径
- 默认路径全部改成了通用示例

## 当前版本

`0.4.6`

## 适用场景

如果你有一份或多份 `v2rayN` 风格的 Base64 订阅源，例如：

```text
/srv/sub-convert/subscriptions/myhy2
/srv/sub-convert/subscriptions/mysub
```

那么 `sub-convert` 会自动生成：

```text
/srv/sub-convert/subscriptions/myhy2.yaml
/srv/sub-convert/subscriptions/myhy2.json
/srv/sub-convert/subscriptions/mysub.yaml
/srv/sub-convert/subscriptions/mysub.json
```

## 功能概览

- 监听无后缀订阅源文件
- 同时输出 Clash 和 sing-box 两种格式
- 支持内容变化重建
- 支持仅修改时间戳也触发重建
- 支持远程规则定时刷新
- 支持 Debian / Ubuntu 环境下用 systemd 常驻运行

## 默认路径

公开仓库里的默认值如下：

- 扫描目录：`/srv/sub-convert/subscriptions`
- 规则缓存：`/var/lib/subscription-converter/rules`
- 状态文件：`/var/lib/subscription-converter/converter-state.json`
- 日志文件：`/var/log/subscription-converter.log`

这些只是示例默认值，不代表你的真实线上环境。你可以按自己的服务器结构修改：

- `subscription_converter/config.py`

程序也支持通过环境变量覆盖这些值：

- `SUBSCRIPTIONS_DIR`
- `SCAN_INTERVAL_SECONDS`
- `RULES_REFRESH_HOURS`
- `RULES_CACHE_DIR`
- `STATE_FILE`
- `LOG_FILE`

## 部署脚本

仓库现在提供两层部署脚本：

- `deploy/bootstrap.sh`
  完整部署脚本，会检查系统、依赖、目录和 systemd，再完成安装与启动。
- `deploy/install.sh`
  兼容入口，内部直接转调 `bootstrap.sh`。

`bootstrap.sh` 会检查：

- 是否以 root 运行
- 是否为 Debian / Ubuntu
- 是否存在 `apt-get`
- 是否存在 `python3`
- 是否存在 `systemctl`
- 是否存在 `requirements.txt` 和服务文件模板

安装完成后，脚本会输出一组综合提示，包括：

- systemd 服务名
- 项目目录和虚拟环境目录
- 订阅源目录、规则缓存目录、状态文件和日志文件
- 手动执行一次转换的 CLI 命令
- 查看服务状态和跟踪日志的命令

## 一键安装命令

如果是全新的 Debian / Ubuntu 服务器，可以直接用 `root` 执行下面这一条：

```bash
apt-get update && apt-get install -y git && mkdir -p /opt/sub-convert && git clone https://github.com/zazitufu/sub-convert.git /opt/sub-convert/app && cd /opt/sub-convert/app && APP_DIR=/opt/sub-convert PROJECT_DIR=/opt/sub-convert/app VENV_DIR=/opt/sub-convert/venv SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions bash deploy/bootstrap.sh
```

如果项目代码已经在服务器上，只需要执行：

```bash
cd /opt/sub-convert/app && APP_DIR=/opt/sub-convert PROJECT_DIR=/opt/sub-convert/app VENV_DIR=/opt/sub-convert/venv SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions bash deploy/bootstrap.sh
```

脚本默认会创建订阅目录：

```text
/srv/sub-convert/subscriptions
```

## 当前分流思路

当前生成逻辑会优先使用官方 `MetaCubeX/meta-rules-dat` 分类：

- AI：`openai`、`anthropic`
- Google：`geosite google` + `geoip google`
- YouTube：`geosite youtube`
- Telegram：`geosite telegram` + `geoip telegram`
- GitHub：`geosite github`
- Netflix：`geosite netflix` + `geoip netflix`
- Microsoft：`geosite microsoft`
- Apple：`geosite apple`
- 国内直连：`private`、`cn`
- 香港：保留 `hk` / `tvb.com` / `geoip hk`

## 安装

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

如果需要运行测试或开发环境，请安装开发依赖：

```bash
pip install -r requirements-dev.txt
```

## 命令行

单次执行：

```bash
python -m subscription_converter.cli --once
```

常驻运行：

```bash
python -m subscription_converter.cli
```

查看版本：

```bash
python -m subscription_converter.cli --version
```

## 测试

```bash
PYTHONPATH=. pytest tests -v
```

## 进一步部署说明

详细部署步骤请看：

- [docs/DEPLOYMENT.zh-CN.md](docs/DEPLOYMENT.zh-CN.md)

