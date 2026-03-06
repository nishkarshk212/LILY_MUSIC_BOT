#!/usr/bin/env bash
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/com.lily.music.bot.plist"
launchctl unload -w "$PLIST" >/dev/null 2>&1 || true
rm -f "$PLIST"
echo "Uninstalled com.lily.music.bot"
