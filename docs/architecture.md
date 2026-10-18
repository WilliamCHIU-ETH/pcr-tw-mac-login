> 文件中的函數名用來說明私人原型，不表示此repo附有可執行客戶端。

# 系統泳道圖與函數解釋

紀錄日期：2026-10-18。依本次成功匯出90位角色的實作整理。圖使用 Mermaid 語法，可在支援 Mermaid 的 Markdown 閱讀器中呈現。

**核心邏輯：Android 提供登入資料來源，真正查詢角色池的是 Mac 上的 Python 客戶端。** 遊戲美術、語音等完整素材不參與這段 API 查詢，因此不必先完成12.59 GB追加下載。

以下拆成三張泳道式時序圖。每條直線代表一個操作對象，箭頭代表跨對象傳遞的指令或資料。這是已實作流程的說明，不是新增執行指令。

## 1. 準備階段：為什麼切換原始／root 映像

```mermaid
sequenceDiagram
    actor U as 你
    participant M as Mac／映像切換工具
    participant A as BlueStacks Android
    participant G as 官方台版遊戲
    participant S as 官方伺服器

    U->>M: 安裝 Air，保留原始啟動映像
    M->>M: 備份＋SHA-256 校驗
    M->>A: 使用原始映像啟動
    U->>G: 手動輸入引繼資訊
    G->>S: 官方遊戲處理認證與引繼
    S-->>G: 引繼成功
    G->>A: 將登入識別資料寫入私有 PlayerPrefs
    G-->>U: 提示下載 12.59 GB 追加資料
    U->>G: 取消下載
    U->>M: 關閉 Air，套用已校驗 root 映像
    M->>A: 再次啟動，保留原有使用者資料
    U->>A: 開啟 ADB，授權 Shell root
    Note over A,G: 此後不需要啟動遊戲
    Note over M,A: 切換啟動映像，不是清空遊戲資料
```

同一份遊戲資料留在 Android 裡，改變的是 Android 開機後是否能提供 root。本次 root 映像下遊戲曾黑屏，因此使用原始映像完成官方引繼，再切 root 讀檔，把「遊戲正常運作」和「讀取私有檔案」分成兩個階段。

官方遊戲內部如何交換引繼憑證，我們沒有逆向到函數層。圖中官方遊戲這一段表示操作與觀察結果；已證明取消追加下載後能讀到欄位，不代表精確掌握它在官方內部哪個函數、哪個瞬間落盤。

ADB 是 Mac 到 Android 的除錯通道，本身不等於 root。普通 shell 讀遊戲私有檔案會被沙盒權限阻擋；Shell root 才提供本次需要的讀取能力。

## 2. 匯出階段：我們實際寫的函數如何分工

以下是 `live_export.py` 的實際流程。

```mermaid
sequenceDiagram
    actor U as 你
    participant E as Mac／live_export.py
    participant A as ADB＋Android root
    participant D as 本機解碼與檢查
    participant S as 官方台版 API
    participant F as 本機成果檔

    U->>E: 執行 live_export.py
    E->>E: run(report)
    E->>E: read_identity()
    E->>A: pidof：確認遊戲沒有執行
    A-->>E: 沒有遊戲程序
    E->>A: su -c cat：讀指定 PlayerPrefs
    A-->>E: XML bytes，留在記憶體
    E->>D: parse(raw)
    D->>D: 解欄位名稱與值
    D-->>E: UDID、SHORT_UDID、viewer低位、server、高位
    E->>D: assess(fields)
    D->>D: 檢查候選數量、ID組合及一致性
    D-->>E: 布林檢查結果
    E->>E: read_identity()檢查必要欄位唯一性
    E->>E: normalize_udid()／decimal()
    E->>E: 建立 Identity，憑證只留記憶體
    E->>E: headers()：設定版本等標頭
    E->>E: 選擇主機，建立 TLS 驗證連線
    loop 依序執行三個 endpoint
        E->>D: create_key()＋build_candidate()
        D-->>E: 編碼後 body＋認證標頭
        E->>S: HTTPSConnection.request()：POST
        S-->>E: HTTP 回應
        E->>D: decode_envelope(raw, identity)
        D-->>E: data_headers＋data
        E->>E: 檢查狀態、帳號一致性及資源版本
    end
    E->>E: 從 load/index 的 data.unit_list 取角色
    E->>E: 只保留角色與專武白名單欄位
    E->>F: save("角色池.json")
    E->>F: save("線上匯出結果.json")
    E-->>U: 90 位角色，匯出成功
    Note over E,F: 不保存 XML、憑證、完整 API 回應或 headers
```

三個 endpoint 的順序：

```text
check/check_agreement
          ↓
check/game_start
          ↓
load/index
          ↓
data.unit_list
```

前兩個是上游台版客戶端採用的登入／初始化流程，第三個回傳帳號初始化資料，其中包含角色池。**角色資料由伺服器回傳，不是從手機存檔拼出來。**

目前程式以完整 viewer ID 的十進位首字元選擇上游主機，並在讀值時驗證它與解出的 server 一致。本帳號這次成功，不代表已證明所有台服路由皆適用同一規則。

三個請求均成功：HTTP 200、result_code=1。程式若遇到 HTTP、解碼、伺服器結果、帳號一致性或角色列表錯誤就停止，沒有自動換服或盲目重試。登入與初始化可能更新 session，不能當作伺服器絕對零副作用的操作。

## 3. 封包細節：憑證怎麼變成請求

```mermaid
sequenceDiagram
    participant E as live_export.run()
    participant C as tw_offline.py
    participant L as MessagePack／AES
    participant S as 官方 API

    E->>C: create_key()
    C-->>E: 本次請求的 32-byte key
    E->>C: build_candidate(identity, endpoint, key)
    C->>C: iv()：取 UDID 前16個 ASCII bytes
    C->>L: encrypt_blob(viewer_id)
    L-->>C: AES密文＋key
    C->>C: Base64 編碼 viewer_id
    C->>C: 組合 endpoint 的資料欄位
    C->>L: msgpack.packb(data)
    L-->>C: packed bytes
    C->>L: encrypt_blob(packed)
    L-->>C: body＝AES密文＋key
    C->>C: uuid_text()＋SHA-1：產生 PARAM
    C->>C: MD5：產生初始 SID、DEVICE-ID
    C->>C: encode_short()：產生 SHORT-UDID
    C-->>E: body＋headers
    E->>S: HTTPS POST
    S-->>E: Base64 包裝的回應
    E->>C: decode_envelope()
    C->>C: Base64 decode，拆出尾端 key
    C->>L: AES-CBC 解密＋移除 padding
    L-->>C: MessagePack bytes
    C->>L: msgpack.unpackb()
    L-->>C: Python dict
    C-->>E: 可檢查、可取角色的資料
```

### 這些技術各自做什麼

- **MessagePack**：把 Python 資料結構轉成二進位資料；用途類似 JSON，但格式不同。
- **AES-CBC 與 padding**：依遊戲協定包裝資料，讓內容符合區塊加密所需長度。
- **Base64**：二進位轉文字表示，不是加密。
- **PARAM**：依 UDID、endpoint、packed資料與viewer ID計算SHA-1，必須與送出的內容相符。
- **SID**：此實作依viewer ID、UUID與固定字串計算的初始識別標頭；不要與每次請求的AES key混用。
- **SHORT-UDID**：由short_udid產生協定要求的混淆字串，並非把原始十進位字串直接當標頭。

`create_key()`產生的是每次請求的加密key，不是帳號登入憑證；帳號識別資料來自PlayerPrefs。

上游協定把key附在封包尾端，因此AES包裝不能視為獨立的傳輸保密保障；實際網路傳輸仍依賴HTTPS與TLS憑證驗證。封包、headers與Base64內容也不能隨意當作無敏感資訊的除錯紀錄。

請求body是原始密文加key；回應則先有Base64外層，兩者不是完全相同的外層格式。IV取UDID前16個**ASCII位元組**，不是把32hex解碼成16bytes後當IV。

## 4. 函數對照

| 函數 | 主要責任 | 不代表什麼 |
|---|---|---|
| `read_identity()` | 經ADB讀指定XML，檢查候選唯一性及ID一致性，組成Identity | 不啟動遊戲、不做API登入 |
| `parse(raw)` | 解開PlayerPrefs裡的名稱和值，收集必要欄位候選 | 可解碼不等於憑證仍有效 |
| `assess(fields)` | 回報候選數、ID組合、高低位及server一致性 | 不等於所有台服路由都已驗證 |
| `normalize_udid()`、`decimal()` | 驗證並統一輸入格式 | 不修補不明或錯誤憑證 |
| `headers()` | 從上游標頭建立本次版本設定 | 不會自動查詢最新遊戲版本 |
| `create_key()` | 產生每次請求的32byte ASCII hex key | 不是從帳號取得的登入token |
| `build_candidate()` | 組合單次請求body、SID、PARAM等 | 本身不連網 |
| `encrypt_blob()` | AES-CBC加密、padding，尾端附key | 不等於傳輸已安全或帳號已認證 |
| `decode_envelope()` | 把回應解成Python資料 | 解密後仍須檢查伺服器結果 |
| `run(report)` | 串接取憑證、三次請求、驗證與角色整理 | 沒有自動重試或換服 |
| `save()` | 寫出角色JSON與去識別化摘要，建立檔案使用0600權限 | 不保存登入憑證 |

`build_candidate()`沿用離線階段名稱，現在由live_export.py呼叫。函數本身沒有HTTP，但主流程確實會將其輸出送往官方API。

## 5. 必須保留的實作修正：viewer ID

正式匯出流程沒有直接使用`compose_viewer()`的「低位必須小於30位」限制。

本帳號lowBits超過30位，高位為0；`read_identity()`依上游公式：

```python
full = (server << 30) | low
```

再確認它與儲存的64bit高低位組合相同，server也與full的十進位首字元相同，才繼續。沒有強制mask或截斷low值。

這條路徑最後得到伺服器成功回應。前次離線工具的30位限制是保守防錯，不是已證實的遊戲協定定律；不能把它畫成正式成功路徑的必經條件。

## 6. 權限、資料保存與成果邊界

| 區域 | 資料／權限 | 本次處理 |
|---|---|---|
| Android App沙盒 | PlayerPrefs登入識別資料 | Shell root讀指定檔案 |
| Mac程序記憶體 | XML、解碼值、Identity、封包、完整回應 | 不主動存入成果或日誌 |
| 官方API | 必要認證標頭與協定封包 | HTTPS、TLS驗證開啟 |
| 成果JSON | 角色ID、星數、等級、Rank、專武原始欄位 | 白名單輸出，不含登入識別資料 |
| 執行摘要 | endpoint、HTTP結果、數量與布林檢查 | 不含憑證值 |

「不保存」指工具沒有將原始內容寫入檔案，並不宣稱做過記憶體安全抹除。

最後取得90位角色，核心欄位無缺值，103筆專武slot；slot數不等於已裝備專武數。角色名稱尚未補入，專武顯示等級尚未與遊戲畫面交叉驗證。

這份圖文描述已完成的私人實驗。本 repo 不附原型程式，閱讀文件不需要開啟ADB或root；完成自己的除錯操作後應管理好這些權限。
