<div align="center">

# pcr-tw-mac-login

![角色池匯出範例：三位角色整理名冊並匯出 JSON](assets/social-preview.jpg)

### 在 Mac 上取得台版公主連結的登入資料

**在 Apple Silicon Mac 上，透過 BlueStacks Air 取出台版《超異域公主連結☆Re:Dive》的登入資料，並用它從 Mac 登入官方 API。**

登入之後要做什麼由你決定：本次實測用來匯出自己的角色池，也可以延伸做其他研究。

![macOS](https://img.shields.io/badge/macOS-111111?logo=apple&logoColor=white)
![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-111111)
![Region TW](https://img.shields.io/badge/Region-TW-2563eb)
![Docs only](https://img.shields.io/badge/Content-Docs_only-2563eb)
![Experimental](https://img.shields.io/badge/Status-Experimental-d97706)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-2563eb)](LICENSE)

**[運作原理](#運作原理)** · **[完整流程](#完整流程)** · **[實測環境](#實測環境)** · **[致謝](#致謝)**

</div>

---

> [!NOTE]
> 這個 repo 只分享方法與實驗文件，不附登入／解碼工具。核心上游專案尚未查到授權聲明，因此暫不散布依其改寫的程式碼，詳見[上游授權與檔案判定](docs/licensing.md)。

## 運作原理

```mermaid
flowchart TB
    subgraph SETUP["首次設定／必要時更新憑證"]
        A["BlueStacks Air<br/>官方遊戲已登入"]
        R["暫時取得 root<br/>讀取指定 App 私有設定"]
        I["Mac 匯入工具<br/>解碼並驗證必要欄位"]
        K[("macOS 鑰匙圈<br/>保存最少必要憑證")]
        A --> R --> I --> K
        I --> Q["關閉 Air、還原正常遊玩環境"]
    end
    subgraph DAILY["日常查詢｜不使用 BlueStacks、ADB 或 root"]
        U["使用者要求更新"]
        C["Mac 查詢工具"]
        V{"鑰匙圈可讀<br/>且欄位驗證通過？"}
        S["登入官方 API<br/>可能影響其他裝置的登入"]
        F["驗證回應並保存<br/>白名單帳號快照"]
        X["停止並回報原因<br/>不自動 root 或重試"]
        U --> C --> V
        K --> V
        V -->|是| S
        V -->|否| X
        S -->|查詢成功| F
        S -->|認證或查詢失敗| X
    end
```

**實測完成（2026-10-19）：必要憑證已匯入鑰匙圈並核對讀回；BlueStacks 關閉、ADB 連接埠停止後，Mac 查詢成功。原始啟動映像已還原並核對 SHA-256，還原後鑰匙圈仍可讀。**

- **root 用在哪裡**：只在首次取得或更新遊戲私有設定時需要；日常查詢改從 macOS 鑰匙圈取得必要欄位。憑證失效時可能需要重新匯入，「首次設定」不代表永久有效。
- **為什麼切換映像**：原始實驗在 root 映像下開遊戲會黑屏，因此讓正常映像負責遊玩、root 映像只負責讀檔。匯入後已還原原始啟動映像，實測狀態見[實驗紀錄](docs/experiment.md)。
- **登入資料是什麼**：四個遊戲識別值，不是 Apple／Facebook 帳密，但具有帳號登入能力。鑰匙圈之外不另存憑證副本，完整設定、識別值、封包及 headers 不進成果檔或公開 repo。
- **分開環境不等於可同時登入**：查詢工具登入官方 API 仍可能讓原本遊戲連線失效。讀取權限、憑證有效性與伺服器登入成功是三個不同的驗證層次。

<details>
<summary><strong>四個欄位各是什麼</strong></summary>

| 欄位 | 是什麼 | 登入時怎麼用 |
| :--- | :--- | :--- |
| `UDID` | 遊戲自己產生的安裝識別碼（不是 iPhone 硬體 UDID） | 請求加密 IV 與 PARAM 簽章的材料 |
| `SHORT_UDID` | 較短的安裝識別值 | 編碼後放進 `SHORT-UDID` 請求標頭 |
| `VIEWER_ID` | 玩家帳號的內部 ID | 與伺服器編號合成完整玩家 ID |
| `TW_SERVER_ID` | 帳號所在的台服編號 | 參與合成完整玩家 ID；連線主機由合成後 ID 的首字元決定 |

設定檔位置、解碼與 ID 合成細節見[系統泳道圖與函數解釋](docs/architecture.md)。

</details>

<details>
<summary><strong>應用範例：角色池匯出格式</strong></summary>

只保留角色資料，不把登入資料寫進 JSON。以下為合成範例，不是真實玩家資料：

```json
{
  "schema_version": 1,
  "region": "TW",
  "units": [
    {
      "id": 100101,
      "name": null,
      "unit_rarity": 3,
      "battle_rarity": 3,
      "unit_level": 100,
      "promotion_level": 15,
      "unique_equip_slot": []
    }
  ]
}
```

| 需求 | 欄位 | 說明 |
| :--- | :--- | :--- |
| 角色 | `id` | 角色 ID；`name` 尚未對照 |
| 星數 | `unit_rarity`、`battle_rarity` | 持有星數與戰鬥選用星數 |
| 等級 | `unit_level` | 伺服器回傳值 |
| Rank | `promotion_level` | 伺服器回傳值 |
| 專武 | `unique_equip_slot` | 保留各 slot 原始欄位，顯示等級仍待交叉驗證 |

完整範例見[合成角色 JSON](examples/roster.synthetic.json)。

</details>

## 完整流程

此圖區分首次匯入與日常查詢；使用者在需要更新時執行，不背景輪詢。

```mermaid
sequenceDiagram
    actor U as 你
    participant A as BlueStacks Air
    participant I as Mac 匯入工具
    participant K as macOS 鑰匙圈
    participant M as Mac 查詢工具
    participant S as 官方伺服器

    rect rgb(240, 245, 255)
        Note over U,K: 首次設定／憑證失效後重設
        U->>A: 關閉遊戲，取得暫時 root
        I->>A: 經 ADB 讀指定私有設定
        A-->>I: XML（僅留記憶體）
        I->>I: 解碼並驗證必要欄位
        I->>K: 保存必要憑證並讀回核對
        U->>A: 關閉 Air、還原原始映像並校驗
    end
    rect rgb(240, 255, 245)
        Note over U,S: 日常查詢（已驗證不依賴 BlueStacks）
        U->>M: 要求更新快照
        M->>K: 讀取必要憑證
        K-->>M: 憑證／存取錯誤
        M->>M: 檢查欄位；失敗即停止
        M->>S: 登入及查詢（可能頂號）
        S-->>M: 帳號資料／錯誤
        M->>M: 驗證成功後保存白名單快照
    end
```

函數分工與歷史原型見[系統泳道圖與函數解釋](docs/architecture.md)。

## 實測環境

| 項目 | 2026-10-19 憑證分離實測 |
| :--- | :--- |
| Mac | Apple Silicon（M2） |
| macOS | 27.0.1 |
| BlueStacks Air | 5.21.790.7505 |
| Android | 13，arm64-v8a |
| 台版遊戲 | 5.9.0（versionCode 113） |
| 結果 | 四個 API 請求皆 HTTP 200、result_code=1 |

日常查詢在套件初始化後禁止建立子程序，並將 ADB 路徑設為不存在的位置；成功查詢沒有啟動 BlueStacks 或 ADB。這是單一環境、單一帳號的成功紀錄，版本邊界與未驗證項目見[方法與實驗結果](docs/experiment.md)。

## 致謝

<div align="center">

這個實驗建立在以下開源專案之上

**[pcr_login_helper](https://github.com/SonderXiaoming/pcr_login_helper)** · SonderXiaoming<br/>
PlayerPrefs 欄位解碼與 ID 組合

**[kanna_connection_redive_2](https://github.com/SonderXiaoming/kanna_connection_redive_2)** · SonderXiaoming<br/>
台版客戶端與通訊協定

**[root-bluestacks-air](https://github.com/hanreev/root-bluestacks-air)** · hanreev<br/>
BlueStacks Air 的 root 映像

</div>

---

<sub>實驗與審查紀錄：[方法與實驗結果](docs/experiment.md) · [上游授權與檔案判定](docs/licensing.md) · [程式來源分析](docs/code-provenance.md) · [公開範圍](docs/publication.md)</sub><br/>
<sub>本 repo 的文件、圖表、合成範例與檢查腳本以 [Apache License 2.0](LICENSE) 授權；不涵蓋上游專案的程式碼。</sub><br/>
<sub>非官方實驗專案，與遊戲開發商、營運商及 BlueStacks 無隸屬關係。</sub>

<sub>角色池匯出範例主視覺 · 非官方 AI 輔助二創，素材說明見 [封面說明](assets/README.md)。</sub>
