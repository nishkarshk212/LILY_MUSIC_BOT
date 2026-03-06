#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/nishkarshk212/LILY_MUSIC_BOT.git"
APP_DIR="/opt/lily_music_bot"
SERVICE_NAME="lily-music-bot.service"

install_packages() {
  if command -v apt >/dev/null 2>&1; then
    apt update -y
    apt install -y python3 python3-venv python3-pip ffmpeg git
  elif command -v yum >/dev/null 2>&1; then
    yum install -y python3 python3-venv python3-pip ffmpeg git || true
  fi
}

clone_repo() {
  mkdir -p "$(dirname "$APP_DIR")"
  if [ -d "$APP_DIR/.git" ]; then
    cd "$APP_DIR"
    git pull --rebase
  else
    git clone "$REPO_URL" "$APP_DIR"
  fi
}

setup_venv() {
  cd "$APP_DIR"
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
}

create_service() {
  cat >/etc/systemd/system/$SERVICE_NAME <<EOF
[Unit]
Description=LILY Music Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/python $APP_DIR/ultra_music_bot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable $SERVICE_NAME
  systemctl restart $SERVICE_NAME
}

install_packages
clone_repo
setup_venv
create_service
echo "Deployment complete. Check status with: systemctl status $SERVICE_NAME"
