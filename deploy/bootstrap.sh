#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/sub-convert}"
PROJECT_DIR="${PROJECT_DIR:-$APP_DIR/app}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
SUBSCRIPTIONS_DIR="${SUBSCRIPTIONS_DIR:-/srv/sub-convert/subscriptions}"
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
    mkdir -p "$APP_DIR" "$SUBSCRIPTIONS_DIR" /var/lib/subscription-converter/rules
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
    sed \
        -e "s#/opt/sub-convert#$APP_DIR#g" \
        -e "s#WorkingDirectory=.*#WorkingDirectory=$PROJECT_DIR#g" \
        -e "s#Environment=PYTHONPATH=.*#Environment=PYTHONPATH=$PROJECT_DIR#g" \
        -e "s#ExecStart=.*#ExecStart=$VENV_DIR/bin/python -m subscription_converter.cli#g" \
        "$SERVICE_TEMPLATE" >"$SERVICE_DEST"
    chmod 0644 "$SERVICE_DEST"
}

reload_and_start() {
    log "Reloading systemd"
    systemctl daemon-reload
    log "Enabling $SERVICE_NAME"
    systemctl enable "$SERVICE_NAME"
    log "Restarting $SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    log "Service status"
    systemctl status "$SERVICE_NAME" --no-pager
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
    log "Deployment finished successfully."
    log "Subscription directory: $SUBSCRIPTIONS_DIR"
}

main "$@"
