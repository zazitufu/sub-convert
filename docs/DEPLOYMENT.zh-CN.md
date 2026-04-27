# 部署说明（中文）

本文档使用脱敏后的通用示例，不包含任何真实服务器信息。

## 推荐目录结构

```text
/opt/sub-convert/
  app/
  venv/

/srv/sub-convert/subscriptions/
```

- `/opt/sub-convert/app` 放项目代码
- `/opt/sub-convert/venv` 放 Python 虚拟环境
- `/srv/sub-convert/subscriptions` 放原始 Base64 订阅源和生成结果

## 一键部署

全新 Debian / Ubuntu 服务器可以用 `root` 执行：

```bash
apt-get update && apt-get install -y git && mkdir -p /opt/sub-convert && git clone https://github.com/zazitufu/sub-convert.git /opt/sub-convert/app && cd /opt/sub-convert/app && APP_DIR=/opt/sub-convert PROJECT_DIR=/opt/sub-convert/app VENV_DIR=/opt/sub-convert/venv SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions bash deploy/bootstrap.sh
```

如果项目已经在服务器上：

```bash
cd /opt/sub-convert/app
bash deploy/bootstrap.sh
```

兼容入口也可以：

```bash
bash deploy/install.sh
```

## 可配置环境变量

部署脚本会把这些变量写入 systemd 服务文件，程序启动后会由 `ConverterConfig()` 读取：

- `APP_DIR`：应用根目录，默认 `/opt/sub-convert`
- `PROJECT_DIR`：项目代码目录，默认 `/opt/sub-convert/app`
- `VENV_DIR`：Python 虚拟环境目录，默认 `/opt/sub-convert/venv`
- `SUBSCRIPTIONS_DIR`：订阅源目录，默认 `/srv/sub-convert/subscriptions`
- `SCAN_INTERVAL_SECONDS`：扫描间隔，默认 `10`
- `RULES_REFRESH_HOURS`：规则刷新间隔，默认 `24`
- `RULES_CACHE_DIR`：规则缓存目录，默认 `/var/lib/subscription-converter/rules`
- `STATE_FILE`：状态文件，默认 `/var/lib/subscription-converter/converter-state.json`
- `LOG_FILE`：日志文件路径，默认 `/var/log/subscription-converter.log`
- `SERVICE_NAME`：systemd 服务名，默认 `subscription-converter.service`

自定义示例：

```bash
APP_DIR=/data/sub-convert \
PROJECT_DIR=/data/sub-convert/app \
VENV_DIR=/data/sub-convert/venv \
SUBSCRIPTIONS_DIR=/data/subscriptions \
RULES_CACHE_DIR=/data/sub-convert/rules \
STATE_FILE=/data/sub-convert/state.json \
LOG_FILE=/data/sub-convert/converter.log \
bash deploy/bootstrap.sh
```

## 部署脚本会做什么

- 检查是否以 root 运行
- 检查系统是否为 Debian / Ubuntu
- 检查 `apt-get`、`python3`、`systemctl`
- 安装 `python3`、`python3-venv`、`python3-pip`、`ca-certificates`
- 创建虚拟环境并安装依赖
- 创建订阅目录、规则缓存目录、状态文件目录和日志目录
- 渲染并安装 systemd 服务
- 重载 systemd、启用并启动服务
- 输出服务名、目录、CLI、日志等部署后提示

## 部署后常用命令

手动执行一次转换：

```bash
cd /opt/sub-convert/app
PYTHONPATH=/opt/sub-convert/app /opt/sub-convert/venv/bin/python -m subscription_converter.cli --once
```

查看服务状态：

```bash
systemctl status subscription-converter.service --no-pager
```

跟踪日志：

```bash
journalctl -u subscription-converter.service -f
```

查看最近日志：

```bash
journalctl -u subscription-converter.service -n 100 --no-pager
```

重启服务：

```bash
systemctl restart subscription-converter.service
```

## 使用方式

把无后缀 Base64 订阅源放到订阅目录，例如：

```text
/srv/sub-convert/subscriptions/myhy2
```

服务会自动生成同名输出：

```text
/srv/sub-convert/subscriptions/myhy2.yaml
/srv/sub-convert/subscriptions/myhy2.json
```

## 公开仓库脱敏提醒

不要把下面这些内容直接写进公开仓库：

- 真实线上域名
- 真实服务器 IP
- 私钥、token、密码
- 真实订阅内容
- 私有路径和真实运维备注
