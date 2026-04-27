# Changelog

## 0.4.5 - 2026-04-28

- Replaced test subscription fixtures with fully synthetic reserved-domain data
- Removed known private node markers from public test data
- Added a repository scan test to block known private fixture markers from reappearing

## 0.4.4 - 2026-04-28

- Added explicit CLI daemon shutdown handling
- Return exit code `0` for keyboard interrupts and `1` for unexpected crashes
- Log unexpected daemon crashes with stack traces before exiting

## 0.4.3 - 2026-04-27

- Removed unused production dependencies inherited from unrelated RSS / web-app code
- Moved `pytest` out of production installation and into the `dev` optional dependency group
- Declared runtime dependencies in `pyproject.toml` and made `requirements.txt` install the project metadata
- Added `requirements-dev.txt` for local testing and development installs

## 0.4.2 - 2026-04-27

- Added `deploy/bootstrap.sh` for full deployment with system checks and dependency installation
- Changed `deploy/install.sh` into a compatibility wrapper for `bootstrap.sh`
- Added deployment prerequisite checks for root, OS, apt, Python, and systemd
- Added generic directory creation and service installation logic to the deployment flow
- Updated public documentation to describe the deployment bootstrap process

## 0.4.1 - 2026-04-26

- Redacted public repository defaults to remove production-specific paths from code and docs
- Changed the generic default scan directory to `/srv/sub-convert/subscriptions`
- Added a detailed Chinese README
- Added a dedicated Chinese deployment guide with placeholder values
- Clarified public deployment structure and version usage

## 0.4.0 - 2026-04-26

- Added automatic conversion from extensionless Base64 subscriptions to Clash `.yaml` and sing-box `.json`
- Added change detection based on digest, file size, and mtime so `touch` also triggers rebuilds
- Added Clash / Mihomo rendering with policy groups, CN / Private direct routing, and HK routing
- Added sing-box rendering with official `MetaCubeX/meta-rules-dat` rule sets for `openai`, `anthropic`, `google`, `youtube`, `telegram`, `github`, `netflix`, `microsoft`, `apple`, `private`, and `cn`
- Added scheduled remote rule refresh support
- Added CLI entry point and daemon loop
- Added Debian systemd service file
- Added parser, renderer, and service tests

## 0.1.0 - 2026-04-24

- Initial working implementation of the subscription converter
