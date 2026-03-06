#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/lily_music_bot"
SERVICE_NAME="lily-music-bot.service"

cd "$APP_DIR"
git pull --rebase
. .venv/bin/activate
pip install -r requirements.txt
systemctl restart "$SERVICE_NAME"
echo "Updated and restarted $SERVICE_NAME"
