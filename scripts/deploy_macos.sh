#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")"/.. && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.lily.music.bot.plist"
PY="$APP_DIR/.venv/bin/python"
OUT_LOG="$APP_DIR/bot.out.log"
ERR_LOG="$APP_DIR/bot.err.log"

python3 -m venv "$APP_DIR/.venv"
. "$APP_DIR/.venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"

mkdir -p "$(dirname "$PLIST")"
cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key><string>com.lily.music.bot</string>
    <key>ProgramArguments</key>
    <array>
      <string>$PY</string>
      <string>$APP_DIR/ultra_music_bot/bot.py</string>
    </array>
    <key>WorkingDirectory</key><string>$APP_DIR</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>$OUT_LOG</string>
    <key>StandardErrorPath</key><string>$ERR_LOG</string>
  </dict>
</plist>
EOF

launchctl unload -w "$PLIST" >/dev/null 2>&1 || true
launchctl load -w "$PLIST"
echo "Loaded com.lily.music.bot. Logs: $OUT_LOG, $ERR_LOG"
