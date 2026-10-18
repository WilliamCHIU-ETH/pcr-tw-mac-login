<div align="center">

# pcr-tw-mac-login

### 在 Mac 上取得台版公主連結的登入資料

**在 Apple Silicon Mac 上，透過 BlueStacks Air 取出台版《超異域公主連結☆Re:Dive》的登入資料，並用它從 Mac 登入官方 API。**

登入之後要做什麼由你決定：本次實測用來匯出自己的角色池，也可以延伸做其他研究。

![macOS](https://img.shields.io/badge/macOS-111111?logo=apple&logoColor=white)
![Apple Silicon](https://img.shields.io/badge/Apple_Silicon-111111)
![Region TW](https://img.shields.io/badge/Region-TW-2563eb)
![Docs only](https://img.shields.io/badge/Content-Docs_only-2563eb)
![Experimental](https://img.shields.io/badge/Status-Experimental-d97706)

**[運作原理](#運作原理)** · **[實測環境](#實測環境)** · **[延伸閱讀](#延伸閱讀)**

</div>

---

> [!NOTE]
> 這個 repo 只分享方法與實驗文件，不附登入／解碼工具。核心上游專案尚未查到授權聲明，因此暫不散布依其改寫的程式碼，詳見[上游授權與檔案判定](docs/licensing.md)。

## 運作原理

```mermaid
flowchart TB
    subgraph AIR["BlueStacks Air（同一份 Android 使用者資料）"]
        B["Step 2：root 映像<br/>不開遊戲，只提供 root"]
        A["Step 1：原始映像<br/>開遊戲，完成官方引繼"]
        P[("playerprefs.xml<br/>遊戲的私有設定檔")]
        B -.->|"root 讓私有檔可被讀取"| P
        A -->|"引繼後寫入"| P
    end
    subgraph MAC["Mac：Python 客戶端（資料只留在記憶體）"]
        D["讀檔並解碼<br/>UDID · SHORT_UDID<br/>VIEWER_ID · TW_SERVER_ID"]
        C["重現遊戲通訊格式<br/>登入官方 API"]
        D --> C
    end
    subgraph SRV["官方伺服器"]
        F["角色池<br/>（本次已驗證）"]
        G["其他帳號資料<br/>（未驗證）"]
    end
    P -->|"經 ADB 通道拉回 Mac"| D
    C -->|"呼叫 API"| F
    C -.-> G
```

對照上圖：

- **為什麼要切換映像**：此環境在 root 映像下開遊戲會黑屏，所以讓原始映像負責引繼、root 映像只負責讀檔。兩者共用同一份使用者資料，也不必先下載 12.59 GB 的追加素材。
- **登入資料是什麼**：從 `playerprefs.xml` 解碼出的四個遊戲識別值，不是 Apple／Facebook 帳密。**但拿到它就能登入這個帳號，不要提交到 GitHub，也不要交給任何人。**
- **它能做什麼**：Mac 客戶端用它登入後，就能呼叫遊戲 API。本次讀取了 90 位角色；其他 API 可走同一個登入流程，尚未驗證。

<details>
<summary><strong>四個欄位各是什麼</strong></summary>

| 欄位 | 是什麼 | 登入時怎麼用 |
| :--- | :--- | :--- |
| `UDID` | 遊戲自己產生的安裝識別碼（不是 iPhone 硬體 UDID） | 證明是同一個安裝 |
| `SHORT_UDID` | 較短的安裝識別值 | 放進每個請求的標頭 |
| `VIEWER_ID` | 玩家帳號的內部 ID | 與伺服器編號合成完整玩家 ID |
| `TW_SERVER_ID` | 帳號所在的台服編號 | 決定連線的伺服器，也參與合成玩家 ID |

設定檔位置、解碼與 ID 合成細節見[泳道圖與函數說明](docs/architecture.md)。

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

## 實測環境

| 項目 | 本次實測 |
| :--- | :--- |
| Mac | Apple Silicon（M2） |
| macOS | 27.0.1 |
| BlueStacks Air | 5.21.790.7505 |
| Android | 13，arm64-v8a |
| 台版遊戲 | 5.9.0（versionCode 113） |
| 結果 | 三個 API 請求皆 HTTP 200、result_code=1 |

這是單一環境、單一帳號的成功紀錄，版本邊界與未驗證項目見[方法與實驗結果](docs/experiment.md)。

## 延伸閱讀

| 文件 | 內容 |
| :--- | :--- |
| [方法與實驗結果](docs/experiment.md) | 完整操作步驟、成功證據與限制 |
| [泳道圖與函數說明](docs/architecture.md) | 引繼、取檔、解碼、登入與匯出的資料流 |
| [上游授權與檔案判定](docs/licensing.md) | 為什麼不附程式碼 |
| [程式來源分析](docs/code-provenance.md) | 逐函數來源對照 |
| [公開範圍](docs/publication.md) | 私人資料隔離與公開條件 |

本專案參考：[pcr_login_helper](https://github.com/SonderXiaoming/pcr_login_helper)（欄位解碼）、[kanna_connection_redive_2](https://github.com/SonderXiaoming/kanna_connection_redive_2)（台版客戶端與協定）、[root-bluestacks-air](https://github.com/hanreev/root-bluestacks-air)（root 映像）、[magpie](https://github.com/yetone/magpie)（README 排版）。

非官方實驗專案，與遊戲開發商、營運商及 BlueStacks 無隸屬關係。
