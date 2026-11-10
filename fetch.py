#!/usr/bin/env python3
"""下載疾管署開放資料 CSV 到 csv/，只有通過檢查才覆蓋既有檔。

檢查：HTTP 200、大小 > 1KB、內容開頭不是 '<'（排除 HTML 錯誤頁）。
任何一支失敗都保留上一份正式檔，不中止其他檔。
狀態寫進 status.json（機器可讀）與 MANIFEST.md（人讀），可重跑。
要增刪 CSV：改下方 FILES。
"""
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://od.cdc.gov.tw/eic/"
FILES = [
    "NHI_Diarrhea.csv",
    "NHI_EnteroviralInfection.csv",
    "NHI_Influenza_like_illness.csv",
    "Weekly_Age_County_Gender_061.csv",  # 登革熱，上游停更時回 404
]
MIN_BYTES = 1024
ROOT = Path(__file__).resolve().parent
CSV_DIR = ROOT / "csv"
STATUS = ROOT / "status.json"
MANIFEST = ROOT / "MANIFEST.md"
RAW = "https://raw.githubusercontent.com/deltaguita/cdc-data-mirror/main/csv/"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name, prev):
    dest = CSV_DIR / name
    fd, tmp = tempfile.mkstemp(dir=CSV_DIR, prefix=".tmp-")
    os.close(fd)
    try:
        r = subprocess.run(
            ["curl", "-sS", "-L", "--fail", "--max-time", "120",
             "-o", tmp, "-w", "%{http_code}", BASE + name],
            capture_output=True, text=True,
        )
        code = r.stdout.strip() or "000"
        size = os.path.getsize(tmp)
        with open(tmp, "rb") as f:
            head = f.read(64).lstrip(b"\xef\xbb\xbf \t\r\n")
        ok = r.returncode == 0 and code == "200" and size > MIN_BYTES and not head.startswith(b"<")
        entry = dict(prev)
        entry["last_attempt_utc"] = now()
        entry["last_http_status"] = int(code) if code.isdigit() else 0
        if ok:
            os.chmod(tmp, 0o644)
            os.replace(tmp, dest)
            entry["last_success_utc"] = entry["last_attempt_utc"]
            entry["result"] = "ok"
        else:
            reason = r.stderr.strip() or f"rejected (bytes={size}, html={head.startswith(b'<')})"
            entry["result"] = f"failed: {reason}"[:200]
        if dest.exists():
            entry["bytes"] = dest.stat().st_size
            entry["sha256"] = sha256(dest)
        return entry
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def write_manifest(status):
    lines = [
        "# MANIFEST",
        "",
        "每支檔最後一次嘗試與最後一次成功的紀錄（UTC）。`bytes`、`sha256` 指 repo 中目前的檔案；"
        "抓取失敗時保留上一份成功的檔案。",
        "",
        "| 檔案 | 最後成功 (UTC) | 最後嘗試 (UTC) | HTTP | bytes | sha256 | 結果 |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in FILES:
        e = status.get(name, {})
        link = f"[{name}]({RAW}{name})" if e.get("bytes") else name
        lines.append("| {} | {} | {} | {} | {} | `{}` | {} |".format(
            link, e.get("last_success_utc", "—"), e.get("last_attempt_utc", "—"),
            e.get("last_http_status", "—"), e.get("bytes", "—"),
            e.get("sha256", "—"), e.get("result", "—").replace("|", "/")))
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    CSV_DIR.mkdir(exist_ok=True)
    status = json.loads(STATUS.read_text()) if STATUS.exists() else {}
    for name in FILES:
        status[name] = fetch(name, status.get(name, {}))
        print(f"{name}: {status[name]['result']} http={status[name]['last_http_status']} bytes={status[name].get('bytes', '-')}")
    status = {k: status[k] for k in FILES}
    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_manifest(status)


if __name__ == "__main__":
    main()
