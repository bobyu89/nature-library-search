# nature-library-search — 用自己圖書館做完整文獻檢索到 Zotero

把「登入圖書館 → 多資料庫檢索 → 全部匯出 → 去重 → AI 協助篩選 → PRISMA 流程圖 → 全文排除附表 → 依篩選階段匯入 Zotero」
變成可以重複執行的流程。來源是 2026 年 10 月兩篇台灣護理學會 A 類實證報告的實作（8 個資料庫匯出、2,680 筆紀錄），
每個資料庫的匯出技巧都經過實際驗證。架構沿用 nature 系列 skill（router＋manifest＋references＋scripts）。

## 支援的資料庫
PubMed（E-utilities）、Cochrane Library、Embase、CINAHL Complete（EBSCO 新介面）、華藝線上圖書館、Scopus（補充）。

## 安裝（Claude Code 或 Codex 都可以當載體）
```bash
git clone https://github.com/bobyu89/nature-library-search.git
cd nature-library-search
```
- Windows：`powershell -ExecutionPolicy Bypass -File install.ps1`（`-Target claude` 或 `-Target codex` 只裝一邊）
- macOS／Linux：`bash install.sh`（或 `bash install.sh codex`）

安裝程式會在 `~/.claude/skills/` 與 `~/.codex/skills/` 建立連結，都指向這個 git 資料夾，之後 `git pull` 就能讓兩邊同步更新。
兩個載體的工具名稱對照（瀏覽器、子代理、下載）見 `references/09-carriers.md`。

## 換成自己的圖書館
1. 複製 `config/library.template.yaml` 為 `config/library.<你的圖書館>.yaml`，填入：
   登入頁、各資料庫從圖書館入口點進去的網址（entry）、實際落地的網域、下載規範、館員聯絡方式。
2. 把 `manifest.yaml` 裡 `always_load` 的 `config/library.ndmu.yaml` 改成自己的設定檔。
3. 需要 Python 3（matplotlib）與載體提供的瀏覽器工具（Claude Code 內建瀏覽器／Claude in Chrome，或 Codex 的瀏覽器工具）；匯入 Zotero 需開著 Zotero 桌面版。
4. 跟 Claude 或 Codex 說「用我們圖書館幫我做完整搜尋」或「PRISMA 待填，幫我匯出去重篩選」即可觸發（Codex 也可用 `$nature-library-search`）。

不同圖書館的代理系統（EZproxy、flysheet、WebVPN）網址不同，但資料庫本身（Cochrane、Embase、EBSCO、華藝）的匯出方法相同。

## 原則
- 圖書館帳密、驗證碼一律由使用者自己在瀏覽器輸入；Claude 不登入個人帳號（MyEBSCO、Embase 個人帳號）。
- 只匯出書目，不大量下載全文；遵守圖書館下載上限。
- 每個資料庫記錄逐行檢索式、筆數、檢索日期與匯出日期；與先前數字不同時照實說明。
- AI 初篩與全文判讀一定要揭露，並由作者逐筆複核（台灣護理學會規定 GenAI 不得獨立完成方法與結果）。

## 檔案
| 位置 | 內容 |
|---|---|
| `SKILL.md` | 路由與流程總表 |
| `manifest.yaml` | 依階段／資料庫載入哪些檔案 |
| `config/` | 圖書館設定（國防醫學大學版、空白範本） |
| `references/` | 原則（含授權）、登入與各種代理系統、檢索策略、各資料庫操作、瀏覽器資料匯出、去重與雙人篩選、輸出、Zotero、檢索驗證與補充方法、PRISMA-S 與台灣護理學會評分自評 |
| `templates/` | 篩選條件範本、結構化檢索紀錄範本、證據摘要表骨架、各資料庫瀏覽器 JS 片段、平台健檢 preflight.js |
| `scripts/` | 流程：`state.py`（斷點續跑）；匯出：`pubmed_ris.py`、`collect_chunks.py`、`ctgov.py`；驗證：`seed_check.py`、`citation_chase.py`；去重與篩選：`dedup.py`、`pilot_sample.py`、`make_batches.py`、`screen_compare.py`（雙人 κ）、`screen_merge.py`；輸出：`prisma_diagram.py`、`prisma_s.py`、`to_csv.py`、`to_bib.py`、`export_formats.py`；Zotero：`zotero_import.py`（check／skip-existing）；維護：`living_update.py`、`archive.py` |
| `tests/` | `run_tests.py`：合成測試資料＋`--real` 重現 1,403→1,138、1,277→1,092 |
| `CHANGELOG.md` | 版本與每次修改的理由 |

## 搭配的 skill
`twna-ebhc-report`（寫報告）、`prisma-2020-master`（PRISMA 清單）、`nature-academic-search`（MeSH 策略、書目格式）、
`nature-downloader`（合法全文取得）、`apa7-master`（參考文獻格式）。
