# 程式來源與可拆分範圍

查核日期：2026-10-18。結論：私有原型同時包含上游改寫與本次新增程式；不能把三支工具全部稱為抄來的，也不能因為改寫或附上 credit 就宣稱已取得再散布許可。

本輪逐函數閱讀私有原型、固定版本上游快照與測試。以下是工程來源判定，不是著作權歸屬裁決；沒有以相似度百分比取代判斷，也沒有宣稱已搜尋世界上所有實作。函數與行號指向此次私有原型快照，原碼未隨本文散布。

## 對照來源

- **KCRR**：`SonderXiaoming/kanna_connection_redive_2`，commit `35723baae36f63edf6b20852bc8e56307d44d505`。
  - [TWClient、標頭、路由與封裝](https://github.com/SonderXiaoming/kanna_connection_redive_2/blob/35723baae36f63edf6b20852bc8e56307d44d505/client/apiclient.py)
  - [BaseClient 加解密與裝置識別](https://github.com/SonderXiaoming/kanna_connection_redive_2/blob/35723baae36f63edf6b20852bc8e56307d44d505/client/base.py)
  - [請求模型與 endpoint](https://github.com/SonderXiaoming/kanna_connection_redive_2/blob/35723baae36f63edf6b20852bc8e56307d44d505/client/request.py)
- **Helper**：`SonderXiaoming/pcr_login_helper`，commit `d1e6b1691a4da49cc2c9c5c20944cc4042cf4ddb`。
  - [設定檔解碼與 ID 組合](https://github.com/SonderXiaoming/pcr_login_helper/blob/d1e6b1691a4da49cc2c9c5c20944cc4042cf4ddb/src-tauri/src/dec_prefs.rs)

授權檢查範圍及限制見[授權紀錄](licensing.md)。這輪核對固定快照，沒有把先前 license=null 記錄當成所有未來版本的狀態。

## 逐檔、逐函數判定

| 私有檔案／位置 | 具體來源關係 | 本次新增與可拆分部分 | 現階段處理 |
| --- | --- | --- | --- |
| `tw_offline.py`：`decimal`、`normalize_udid`，18–36 | 一般數字與 UUID 輸入驗證；所查上游沒有相同的完整驗證實作 | canonical decimal、拒絕 bool、格式／範圍檢查 | 可列為本次自寫候選；沒有必要為湊程式碼單獨發布 |
| 同檔：`uuid_text`、`compose_viewer`、`Identity`，39–68 | UUID 格式與 KCRR `format_uuid` 對應；ID 組合依 Helper `tw_encode_high_bit` | 超過 30 bits 拒絕、隱藏 repr、資料類別是新增保護 | 混合來源，不把整段標成全新獨立實作；30-bit 限制不是通用有效規則 |
| 同檔：`route_audit`、`version_audit`，71–86 | 路由承襲 TWClient 首位數規則；版本是來源與實驗觀察 | 差異報告與不自動選版本是新增 | 文件可描述事實；協定程式先保留私有 |
| 同檔：`iv`、`create_key`、`encrypt_blob`、`decode_envelope`，89–108 | 對應 `_getiv`、`createkey`、`encrypt`、`unpack` 的線上格式 | secrets 隨機源、長度及 Base64 檢查不同 | 有明確參考關係；標準 AES 本身不等於上游專屬，但不能因此替整段改寫自動洗清來源 |
| 同檔：`encode_short`、`decode_short`，111–122 | `encode_short` 的長度前綴、每四字元插入、偏移與尾碼緊密對應 `_encode`；decode 為其逆向驗證 | 可注入隨機選擇器及長度檢查 | 列為需處理來源的核心部分 |
| 同檔：`build_candidate`，125–145 | SID、DEVICE-ID、PARAM、viewer 加密、MessagePack 及欄位順序參考 KCRR 三個來源檔 | 三 endpoint 白名單與離線回傳介面 | 不整檔公開；重新命名無法取代來源處理 |
| `check_local_identity.py`：`xor`、`b64`、`parse`，14–42 | 解碼常數、URL/Base64/XOR 順序、7/11 bytes 裁切、UDID 字元取法與 Helper 直接對應 | XML parser 替代 regex；新增 highBits、長度與 UUID 驗證；省去不必要 token | Rust 改寫成 Python 仍有來源關係；解碼器暫不納入 |
| 同檔：`assess`，44–66 | ID 公式沿用 Helper | 候選數量、high/low 與 OR 一致性、只回傳布林值是本次檢查設計 | 可拆出驗證框架，但仍須明列公式來源，不宣稱憑證解碼已獨立 |
| 同檔：`run`，68–78 | 呼叫上述解碼器 | ADB 子程序、檢查遊戲未啟動、只讀指定檔案、不輸出憑證的編排是本次新增 | 可拆成讀取介面；目前函數本身仍依賴 parse／assess |
| `live_export.py`：`save`，10–13 | 一般 Python JSON 寫入，所查上游未見相同函數 | 本次新增 | 可獨立整理；目前 mode 0600 只保證新建檔權限，既有檔權限不會自動改正，公開版應補強 |
| 同檔：`read_identity`，15–29 | 呼叫 Helper 衍生解碼與 ID 公式 | high/low 交叉核對、歧義停止是新增 | 混合依賴，不能直接搬走當獨立登入元件 |
| 同檔：`headers`，31–37 | **執行時用 AST 直接擷取上游 `tw_headers` 字典** | 覆寫實測 App／Unity 版本、移除 Expect | 這是明確原碼依賴，不只是口頭參考；不能刪掉 reference 後宣稱工具可運作 |
| 同檔：`run`，39–83 | 登入順序、路由與回應欄位依 KCRR；呼叫衍生封裝／解碼器 | 標準庫 HTTPS、TLS 驗證、無重試、容量上限、identity 不變檢查、角色白名單、JSON schema 與摘要是新增 | 可以拆出 transport／roster projection，但整個 run 不是獨立無依賴程式 |
| `test_offline.py`：`reference_classes`、差異測試 | 從上游快照抽 AST，再執行加解密方法比較 | 測試編排與合成案例是本次撰寫 | 測試程式不等於全部抄寫，但現有套件仍需 reference；發布時需處理來源，或另寫不依賴原碼的測試 |
| `tools/check_public_tree.py` | 沒有遊戲解碼／通訊功能，也不 import 私有原型 | 白名單、路徑／秘密樣式、連結、合成範例檢查 | 已納入本 repo |

## 最小可行的公開方案

**要讓別人直接重現完整匯出：優先處理 KCRR 與 Helper 這兩個來源的明確許可。** 它們目前同屬 SonderXiaoming，可把兩個 commit、要使用的檔案、Python 改寫、公開散布與預計採用的授權條件整理成一次詢問。作者也只能許可其有權授權的內容；若涉及更上游實作，仍須保留或補查其條件。這輪未聯絡作者。

同時可以把本次自寫的角色投影、JSON 輸出及連線保護拆成獨立模組，以合成資料測試。但這只讓自己的部分能獨立審閱，**不會自動補上缺少的解碼與登入能力**。本輪只做來源判定，尚未進行這個重構。

若上游不回覆，再評估明確授權的相容替代實作。不可把「改語言、改變數、補 credit」當成許可，也不能在已讀取來源後把普通重寫稱為已完成 clean-room。GitHub 的[授權說明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)明確區分公開存取與授權。

root 工具是另一個邊界：目前本 repo 只連結 root-bluestacks-air，不含其 script、APK 或映像。若未來要打包該工具，需另外處理其來源與授權；不必為分享自己的匯出器先把整套 root 工具收進 repo。

## 查核快照

以下只記原始碼雜湊，沒有帳號、憑證或裝置資料。用途是讓私人開發紀錄能對回這次分析，並非公開原型原碼。

| 檔案 | SHA-256 |
| --- | --- |
| tw_offline.py | `ec23e59a9b6c17091d3feebb2bcc6b72ea94f5e3d0c0cb9c6474cde3698ab55b` |
| check_local_identity.py | `c20d1a677febe81f866868047a31afd74a05e98c218285e41fec8076e6ceb840` |
| live_export.py | `e0ae5fa69deffa71a6c7d3950042c799460c09f3d527a128e9b3ff876cfc9b2d` |
| test_offline.py | `4b6282d24a54390fea64b5f8adff234c344a60291ab88ddcd920bec1b65588b1` |
