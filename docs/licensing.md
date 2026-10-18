# 上游授權與檔案判定

查核日期：2026-10-18。本頁記錄查核證據與採取的發布範圍，不作法律結論或代表作者授權。

## 查核方法

透過GitHub API讀取倉庫授權metadata、固定commit完整檔案樹（均未截斷），搜尋LICENSE／LICENCE／COPYING／NOTICE，並檢查該commit的README、Cargo.toml、package.json及pyproject.toml（如存在）。

| 上游 | 使用的commit | 查核結果 | 本 repo 處理 |
| --- | --- | --- | --- |
| [kanna_connection_redive_2](https://github.com/SonderXiaoming/kanna_connection_redive_2) | `35723baae36f63edf6b20852bc8e56307d44d505` | API license=null；未找到授權檔或檢查範圍內的授權聲明 | 不放原碼、快照或其改寫登入客戶端 |
| [pcr_login_helper](https://github.com/SonderXiaoming/pcr_login_helper) | `d1e6b1691a4da49cc2c9c5c20944cc4042cf4ddb` | 同上 | 不放Rust快照或依其改寫的解碼器 |
| [root-bluestacks-air](https://github.com/hanreev/root-bluestacks-air) | `9056f43fef6f2c0a6d3577cbd061fa6ff5f8ac50` | 同上 | 不放root.sh、Magisk元件或修改映像 |

機器可讀查核摘要：[upstream-license-audit.json](upstream-license-audit.json)。這不涵蓋作者私下授權或未檢查的外部聲明，也不是未來版本的授權保證。

GitHub說明：沒有授權時，預設著作權規則仍適用；公開可讀與GitHub站內fork權利，不應直接當成任意重新散布／改作許可。[GitHub授權文件](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)

## 檔案判定

| 類別 | 是否公開 | 原因 |
| --- | --- | --- |
| 自行撰寫的去識別化方法、Mermaid圖與結果摘要 | 納入 | 描述實驗與方法，非複製上游程式實作 |
| 合成JSON範例 | 納入 | 沒有真實帳號、憑證或角色池 |
| 公開倉庫名稱、commit、來源連結 | 納入 | 明確引用來源，不重新散布原碼 |
| 自行撰寫的檔案清單／公開內容檢查器 | 納入 | 不包含遊戲協定或上游改寫實作 |
| tw_offline.py、check_local_identity.py、live_export.py | 暫不整檔納入 | 混合上游衍生核心與本次自寫部分；具體函數與可拆分範圍見[程式來源分析](code-provenance.md) |
| 依上游原碼抽取AST的差異測試及reference快照 | 暫不納入 | 需要上游原碼，不能繞過授權缺口 |
| 真實角色JSON、識別值、完整封包或日誌 | 不納入 | 私人帳號資料，無必要公開 |
| iPhone備份、plist、Manifest.db | 不納入 | 含私人裝置及App資訊 |
| APK、Air安裝器、Magisk APK、root／原始映像 | 不納入 | 不屬本專案自行撰寫內容，也不需要放進方法分享repo |
| 虛擬環境、套件、快取、個人絕對路徑 | 不納入 | 機器相依或多餘內容 |

## 要公開可執行客戶端，還缺什麼

已完成[逐函數來源分析](code-provenance.md)：自寫 transport、檢查與 JSON 輸出可進一步拆分；目前登入／解碼核心仍有上游來源關係，且 headers 直接讀取上游原碼。不是所有工具都一概無法公開。

先取得涵蓋所用程式碼的明確授權／許可，或另選具有合適授權的實作來源，再確認改作與散布條件。重新選擇來源也要重新測試，不能只替換來源標籤。這次沒有聯絡上游作者。

專案作者已選定以 [Apache License 2.0](../LICENSE) 授權本 repo 的自寫內容：文件、圖表、合成範例與檢查器。此授權不涵蓋上游專案的原碼或依其改寫的客戶端，那些內容仍不在本 repo 內；本 repo 也不能稱為已授權的開源登入客戶端。

## 其他來源

BlueStacks、遊戲與第三方套件均不隨本 repo 重新散布。
