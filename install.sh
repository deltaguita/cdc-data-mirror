#!/bin/bash
set -euo pipefail

# CDC Data Mirror 安裝腳本
# 此腳本會將 systemd unit 檔安裝到系統，並啟用每日自動更新

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📦 安裝 CDC mirror systemd units..."

# 確認需要 root 權限
if [[ $EUID -ne 0 ]]; then
   echo "❌ 此腳本需要 root 權限，請使用 sudo 執行" 
   exit 1
fi

# 確認 systemd 目錄存在
if [[ ! -d "$SCRIPT_DIR/systemd" ]]; then
    echo "❌ 找不到 systemd/ 目錄"
    exit 1
fi

# 複製 unit 檔到系統目錄
echo "  → 複製 unit 檔到 /etc/systemd/system/"
cp "$SCRIPT_DIR/systemd/cdc-mirror.service" /etc/systemd/system/
cp "$SCRIPT_DIR/systemd/cdc-mirror.timer" /etc/systemd/system/

# 修改 service 檔中的 WorkingDirectory 與 ExecStart 路徑
echo "  → 設定 WorkingDirectory 為 $SCRIPT_DIR"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$SCRIPT_DIR|" /etc/systemd/system/cdc-mirror.service
sed -i "s|ExecStart=.*|ExecStart=$SCRIPT_DIR/update.sh|" /etc/systemd/system/cdc-mirror.service

# 設定執行權限
chmod +x "$SCRIPT_DIR/update.sh"

# 重新載入 systemd daemon
echo "  → 重新載入 systemd daemon"
systemctl daemon-reload

# 啟用並啟動 timer
echo "  → 啟用 cdc-mirror.timer"
systemctl enable cdc-mirror.timer
systemctl start cdc-mirror.timer

echo ""
echo "✅ 安裝完成！"
echo ""
echo "檢查 timer 狀態："
systemctl status cdc-mirror.timer --no-pager
echo ""
echo "下次執行時間："
systemctl list-timers cdc-mirror.timer --no-pager
