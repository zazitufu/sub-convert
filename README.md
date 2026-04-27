# sub-convert

`sub-convert` is a self-hosted subscription converter for extensionless Base64 source files.

It watches a source directory and generates:

- Clash / Mihomo subscriptions as `.yaml`
- sing-box subscriptions as `.json`

This public repository is intentionally redacted. It does not include any real production domain names, private IPs, hostnames, or deployment-specific private paths.

## Version

`0.4.5`

## What It Does

- Reads source files such as `myhy2`
- Writes sibling outputs such as `myhy2.yaml` and `myhy2.json`
- Rebuilds on content changes
- Rebuilds on `touch` / mtime-only changes
- Generates Clash / Mihomo and sing-box outputs from one normalized model
- Refreshes official remote rule assets on a schedule
- Runs continuously as a daemon on Linux servers

## Generic Default Paths

The public repository uses generic defaults:

- Scan directory: `/srv/sub-convert/subscriptions`
- Rule cache: `/var/lib/subscription-converter/rules`
- State file: `/var/lib/subscription-converter/converter-state.json`
- Log file: `/var/log/subscription-converter.log`

If your real deployment uses different paths, adjust them in `subscription_converter/config.py`.

## Deployment Scripts

This repository includes two deployment scripts:

- `deploy/bootstrap.sh`
  A full deployment bootstrap script with prerequisite checks, package installation, virtualenv setup, directory creation, systemd installation, and service restart.
- `deploy/install.sh`
  A compatibility wrapper that simply forwards to `bootstrap.sh`.

The bootstrap script checks:

- root privileges
- Debian / Ubuntu compatibility via `/etc/os-release`
- `apt-get`
- `python3`
- `systemctl`
- project files such as `requirements.txt` and `subscription-converter.service`

## One-Line Server Install

For a fresh Debian / Ubuntu server, run this as `root`:

```bash
apt-get update && apt-get install -y git && mkdir -p /opt/sub-convert && git clone https://github.com/zazitufu/sub-convert.git /opt/sub-convert/app && cd /opt/sub-convert/app && APP_DIR=/opt/sub-convert PROJECT_DIR=/opt/sub-convert/app VENV_DIR=/opt/sub-convert/venv SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions bash deploy/bootstrap.sh
```

If the project is already present on the server, run:

```bash
cd /opt/sub-convert/app && APP_DIR=/opt/sub-convert PROJECT_DIR=/opt/sub-convert/app VENV_DIR=/opt/sub-convert/venv SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions bash deploy/bootstrap.sh
```

The default subscription source directory created by the script is:

```text
/srv/sub-convert/subscriptions
```

## Policy Groups

Generated subscriptions include groups such as:

- `AI`
- `Google`
- `YouTube`
- `Telegram`
- `GitHub`
- `Netflix`
- `Microsoft`
- `Apple`
- `HK`
- `国内直连`
- `漏网之鱼`

Where official `MetaCubeX/meta-rules-dat` categories exist, the converter prefers official `geosite` and `geoip` classifications.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

## CLI

Run once:

```bash
python -m subscription_converter.cli --once
```

Run continuously:

```bash
python -m subscription_converter.cli
```

Check version:

```bash
python -m subscription_converter.cli --version
```

## Tests

```bash
PYTHONPATH=. pytest tests -v
```

## Chinese Docs

- [README.zh-CN.md](README.zh-CN.md)
- [docs/DEPLOYMENT.zh-CN.md](docs/DEPLOYMENT.zh-CN.md)

