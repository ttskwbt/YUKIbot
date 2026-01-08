#!/bin/bash
# YUKIbotをlaunchdに登録するスクリプト

SCRIPT_DIR="/Users/user/Desktop/YUKIbot"
PLIST_FILE="$SCRIPT_DIR/com.yukibot.plist"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "YUKIbotをlaunchdに登録します..."

# LaunchAgentsディレクトリが存在しない場合は作成
mkdir -p "$LAUNCHD_DIR"

# plistファイルをLaunchAgentsにコピー
cp "$PLIST_FILE" "$LAUNCHD_DIR/"

# launchdに登録
launchctl load "$LAUNCHD_DIR/com.yukibot.plist"

echo "✓ 登録完了！"
echo ""
echo "以下のコマンドで管理できます："
echo "  停止: launchctl unload $LAUNCHD_DIR/com.yukibot.plist"
echo "  開始: launchctl load $LAUNCHD_DIR/com.yukibot.plist"
echo "  状態確認: launchctl list | grep yukibot"
echo "  ログ確認: tail -f $SCRIPT_DIR/yuki_bot.log"
