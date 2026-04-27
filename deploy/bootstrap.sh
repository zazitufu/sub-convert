#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/sub-convert}"
PROJECT_DIR="${PROJECT_DIR:-$APP_DIR/app}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
SUBSCRIPTIONS_DIR="${SUBSCRIPTIONS_DIR:-/srv/sub-convert/subscriptions}"
SCAN_INTERVAL_SECONDS="${SCAN_INTERVAL_SECONDS:-10}"
RULES_REFRESH_HOURS="${RULES_REFRESH_HOURS:-24}"
RULES_CACHE_DIR="${RULES_CACHE_DIR:-/var/lib/subscription-converter/rules}"
STATE_FILE="${STATE_FILE:-/var/lib/subscription-converter/converter-state.json}"
LOG_FILE="${LOG_FILE:-/var/log/subscription-converter.log}"
SERVICE_NAME="${SERVICE_NAME:-subscription-converter.service}"
SERVICE_TEMPLATE="${SERVICE_TEMPLATE:-$PROJECT_DIR/deploy/subscription-converter.service}"
SYSTEMD_DIR="${SYSTEMD_DIR:-/etc/systemd/system}"
SERVICE_DEST="${SERVICE_DEST:-$SYSTEMD_DIR/$SERVICE_NAME}"

log() {
    printf '[sub-convert] %s\n' "$*"
}

fail() {
    printf '[sub-convert] ERROR: %s\n' "$*" >&2
    exit 1
}

require_root() {
    if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
        fail "This script must be run as root."
    fi
}

check_os() {
    [[ -f /etc/os-release ]] || fail "Missing /etc/os-release; unsupported system."
    # shellcheck disable=SC1091
    . /etc/os-release
    case "${ID:-}" in
        debian|ubuntu)
            ;;
        *)
            fail "Unsupported distribution: ${ID:-unknown}. Debian or Ubuntu is required."
            ;;
    esac
    command -v apt-get >/dev/null 2>&1 || fail "apt-get is required."
}

check_prerequisites() {
    command -v systemctl >/dev/null 2>&1 || fail "systemctl is required."
    command -v python3 >/dev/null 2>&1 || fail "python3 is required."
    [[ -d "$PROJECT_DIR" ]] || fail "Project directory not found: $PROJECT_DIR"
    [[ -f "$PROJECT_DIR/requirements.txt" ]] || fail "Missing requirements.txt in $PROJECT_DIR"
    [[ -f "$SERVICE_TEMPLATE" ]] || fail "Missing service template: $SERVICE_TEMPLATE"
}

install_packages() {
    export DEBIAN_FRONTEND=noninteractive
    log "Updating apt package index"
    apt-get update
    log "Installing required packages"
    apt-get install -y python3 python3-venv python3-pip ca-certificates
}

prepare_directories() {
    log "Preparing directories"
    mkdir -p \
        "$APP_DIR" \
        "$SUBSCRIPTIONS_DIR" \
        "$RULES_CACHE_DIR" \
        "$(dirname "$STATE_FILE")" \
        "$(dirname "$LOG_FILE")"
}

setup_virtualenv() {
    if [[ ! -x "$VENV_DIR/bin/python" ]]; then
        log "Creating virtual environment at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi

    log "Upgrading pip"
    "$VENV_DIR/bin/pip" install --upgrade pip
    log "Installing Python dependencies"
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
}

install_service() {
    log "Installing systemd unit to $SERVICE_DEST"
    render_service_file
    chmod 0644 "$SERVICE_DEST"
}

render_service_file() {
    APP_DIR="$APP_DIR" \
    PROJECT_DIR="$PROJECT_DIR" \
    VENV_DIR="$VENV_DIR" \
    SUBSCRIPTIONS_DIR="$SUBSCRIPTIONS_DIR" \
    SCAN_INTERVAL_SECONDS="$SCAN_INTERVAL_SECONDS" \
    RULES_REFRESH_HOURS="$RULES_REFRESH_HOURS" \
    RULES_CACHE_DIR="$RULES_CACHE_DIR" \
    STATE_FILE="$STATE_FILE" \
    LOG_FILE="$LOG_FILE" \
    SERVICE_TEMPLATE="$SERVICE_TEMPLATE" \
    SERVICE_DEST="$SERVICE_DEST" \
    python3 - <<'PY'
from pathlib import Path
import os
import sys

template_path = Path(os.environ["SERVICE_TEMPLATE"])
dest_path = Path(os.environ["SERVICE_DEST"])
text = template_path.read_text(encoding="utf-8")

replacements = {
    "WorkingDirectory=/opt/sub-convert/app": f"WorkingDirectory={os.environ['PROJECT_DIR']}",
    "Environment=PYTHONPATH=/opt/sub-convert/app": f"Environment=PYTHONPATH={os.environ['PROJECT_DIR']}",
    "Environment=SUBSCRIPTIONS_DIR=/srv/sub-convert/subscriptions": f"Environment=SUBSCRIPTIONS_DIR={os.environ['SUBSCRIPTIONS_DIR']}",
    "Environment=SCAN_INTERVAL_SECONDS=10": f"Environment=SCAN_INTERVAL_SECONDS={os.environ['SCAN_INTERVAL_SECONDS']}",
    "Environment=RULES_REFRESH_HOURS=24": f"Environment=RULES_REFRESH_HOURS={os.environ['RULES_REFRESH_HOURS']}",
    "Environment=RULES_CACHE_DIR=/var/lib/subscription-converter/rules": f"Environment=RULES_CACHE_DIR={os.environ['RULES_CACHE_DIR']}",
    "Environment=STATE_FILE=/var/lib/subscription-converter/converter-state.json": f"Environment=STATE_FILE={os.environ['STATE_FILE']}",
    "Environment=LOG_FILE=/var/log/subscription-converter.log": f"Environment=LOG_FILE={os.environ['LOG_FILE']}",
    "ExecStart=/opt/sub-convert/venv/bin/python -m subscription_converter.cli": f"ExecStart={os.environ['VENV_DIR']}/bin/python -m subscription_converter.cli",
}

missing = [needle for needle in replacements if needle not in text]
if missing:
    sys.stderr.write("Service template is missing expected line(s):\n")
    for needle in missing:
        sys.stderr.write(f"- {needle}\n")
    raise SystemExit(1)

for needle, replacement in replacements.items():
    text = text.replace(needle, replacement)

dest_path.write_text(text, encoding="utf-8")
PY
}

reload_and_start() {
    log "Reloading systemd"
    systemctl daemon-reload
    log "Enabling $SERVICE_NAME"
    systemctl enable "$SERVICE_NAME"
    log "Restarting $SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "$SERVICE_NAME is active"
    else
        log "$SERVICE_NAME is not active after restart; recent logs follow"
        journalctl -u "$SERVICE_NAME" -n 80 --no-pager || true
        return 1
    fi
}

print_deployment_summary() {
    cat <<EOF
[sub-convert] Deployment summary
[sub-convert] Service: $SERVICE_NAME
[sub-convert] Project directory: $PROJECT_DIR
[sub-convert] Virtualenv: $VENV_DIR
[sub-convert] Subscription directory: $SUBSCRIPTIONS_DIR
[sub-convert] Scan interval: ${SCAN_INTERVAL_SECONDS}s
[sub-convert] Rules refresh interval: ${RULES_REFRESH_HOURS}h
[sub-convert] Rule cache: $RULES_CACHE_DIR
[sub-convert] State file: $STATE_FILE
[sub-convert] Log file: $LOG_FILE
[sub-convert] Run once: cd "$PROJECT_DIR" && PYTHONPATH="$PROJECT_DIR" "$VENV_DIR/bin/python" -m subscription_converter.cli --once
[sub-convert] Check service: systemctl status "$SERVICE_NAME" --no-pager
[sub-convert] Follow logs: journalctl -u "$SERVICE_NAME" -f
[sub-convert] Add source files without suffix under: $SUBSCRIPTIONS_DIR
[sub-convert] Generated outputs will be sibling .yaml and .json files.
EOF
}

main() {
    require_root
    check_os
    check_prerequisites
    install_packages
    prepare_directories
    setup_virtualenv
    install_service
    reload_and_start
    print_deployment_summary
}

main "$@"
