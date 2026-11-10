# cdc-data-mirror

疾病管制署（CDC）開放資料的每日鏡像。

疾管署開放資料站 `od.cdc.gov.tw` 只接受台灣住宅／固網 IP，雲端與機房 IP 抓不到。本 repo 由一台台灣家用網路的主機每天抓取，再推到 GitHub，雲端服務可以改讀下方的 raw 網址。

## 固定網址

每支檔有兩個固定網址，內容相同，擇一使用。每日更新是覆蓋同一路徑的檔案，所以網址永遠不變，內容會跟著更新。

| 資料 | 來源（疾管署） |
|---|---|
| 健保門急診腹瀉 | [NHI_Diarrhea.csv](https://od.cdc.gov.tw/eic/NHI_Diarrhea.csv) |
| 健保門急診腸病毒 | [NHI_EnteroviralInfection.csv](https://od.cdc.gov.tw/eic/NHI_EnteroviralInfection.csv) |
| 健保門急診類流感 | [NHI_Influenza_like_illness.csv](https://od.cdc.gov.tw/eic/NHI_Influenza_like_illness.csv) |
| 登革熱（依週、年齡、縣市、性別） | [Weekly_Age_County_Gender_061.csv](https://od.cdc.gov.tw/eic/Weekly_Age_County_Gender_061.csv) |

GitHub Pages：

```text
https://deltaguita.github.io/cdc-data-mirror/csv/NHI_Diarrhea.csv
https://deltaguita.github.io/cdc-data-mirror/csv/NHI_EnteroviralInfection.csv
https://deltaguita.github.io/cdc-data-mirror/csv/NHI_Influenza_like_illness.csv
https://deltaguita.github.io/cdc-data-mirror/csv/Weekly_Age_County_Gender_061.csv
```

GitHub raw：

```text
https://raw.githubusercontent.com/deltaguita/cdc-data-mirror/main/csv/NHI_Diarrhea.csv
https://raw.githubusercontent.com/deltaguita/cdc-data-mirror/main/csv/NHI_EnteroviralInfection.csv
https://raw.githubusercontent.com/deltaguita/cdc-data-mirror/main/csv/NHI_Influenza_like_illness.csv
https://raw.githubusercontent.com/deltaguita/cdc-data-mirror/main/csv/Weekly_Age_County_Gender_061.csv
```

兩者都有 CDN 快取，push 後約幾分鐘內生效（raw 約 5 分鐘；Pages 要等 build 完成）。登革熱檔目前上游回 404，鏡像中暫無此檔，上述網址在上游恢復前會回 404。

使用範例：

```bash
curl -fsSL https://deltaguita.github.io/cdc-data-mirror/csv/NHI_EnteroviralInfection.csv -o NHI_EnteroviralInfection.csv
```

## 更新方式

- 每天 05:30（台灣時間）抓取一次，有變更才 commit。
- 檔案內容與疾管署原始檔逐位元組相同，本鏡像不做任何轉換；資料以疾管署原始發布為準。
- 某支檔抓取失敗（例如上游回 404 或錯誤頁）時，保留上一份成功的檔案。上游從未成功提供過的檔案不會出現在 `csv/`。
- 每支檔的最後成功時間、HTTP 狀態、大小與 sha256 記在 [MANIFEST.md](MANIFEST.md)，機器可讀版本在 [status.json](status.json)。

## 自建你自己的鏡像

疾管署只放行台灣住宅/固網 IP，機房與雲端 ASN 會被擋。若你有台灣家用網路環境，可以 clone 這個 repo 自己跑。

### 環境需求

- Python 3（執行 `fetch.py`）
- curl、git、gh（GitHub CLI）
- systemd（Linux）

### 安裝步驟

```bash
# 1. Clone repo
git clone https://github.com/deltaguita/cdc-data-mirror.git
cd cdc-data-mirror

# 2. 認證 GitHub CLI（需要 repo write 權限）
gh auth login

# 3. 跑安裝腳本（需要 sudo）
sudo ./install.sh
```

`install.sh` 會把 systemd unit 檔安裝到系統，並啟用每日 05:30 自動執行。

### 驗證

```bash
# 檢查 timer 狀態
systemctl status cdc-mirror.timer

# 手動執行一次
sudo systemctl start cdc-mirror.service
```

## 貢獻

歡迎開 issue 或 PR。疾管署新增其他開放資料檔時，可以在 `fetch.py` 補上對應項目。

## 授權

資料版權屬疾病管制署，依[政府資料開放授權條款](https://data.gov.tw/license)使用。

本 repo 的程式碼採用 MIT 授權，見 [LICENSE](LICENSE)。
