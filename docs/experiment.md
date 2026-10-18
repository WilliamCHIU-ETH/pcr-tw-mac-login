# 方法與實驗結果

此文件是已完成私人實驗的去識別化摘要。公開候選沒有附登入工具、私人角色池、裝置備份或遊戲二進位檔。

## 目的

把自己的角色資料交給AI分析配隊與培養方向，先成功匯出一次，之後手動更新。最低需求為角色、星數、等級、Rank及專武。

## 成功路徑

1. 在Apple Silicon Mac安裝BlueStacks Air，備份其原始啟動映像。
2. 在原始映像的官方台版遊戲內，手動完成自己帳號的引繼。
3. 在12.59GB追加下載提示取消，不先下載完整素材。
4. 完整關閉Air，再換成已校驗的root啟動映像。Android使用者資料保留。
5. 啟動Air，僅開ADB及Shell root，不啟動遊戲。讀指定App的PlayerPrefs。
6. 在記憶體解碼UDID、SHORT_UDID、VIEWER_ID及TW_SERVER_ID；檢查候選唯一性與ID一致性。
7. 由Mac Python客戶端發出一次登入／初始化流程及load/index，將unit_list中的角色欄位匯出。

本次無須關閉SIP。替換App內映像曾需要macOS的Terminal App管理權限與sudo，兩者不能混為一談；原始備份也用於黑屏診斷對照。

## 為什麼切換兩種映像

root映像下遊戲黑屏，還原原始映像後可以正常顯示。這支持環境相關性，沒有證明具體的反root檢查或某一行圖形錯誤是原因。

把正常引繼與root讀檔分開，避開了「必須在root下開遊戲」這個不必要條件。

## 成功證據摘要

| 檢查 | 結果 |
| --- | --- |
| 普通ADB shell讀測試App私有檔案 | Permission denied |
| Shell root讀同一檔案 | 成功，測試標記相符 |
| 引繼後、追加下載前的台版PlayerPrefs | 必要識別欄位可解碼 |
| check/check_agreement | HTTP 200、result_code=1 |
| check/game_start | HTTP 200、result_code=1 |
| load/index | HTTP 200、result_code=1 |
| 匯出 | 90位角色、90個唯一角色ID |
| 角色ID、星數、等級、Rank | 無缺值 |
| 專武 | 103筆slot，保留原始欄位，不等於103把已裝備專武 |
| TLS驗證 | 開啟 |

版本：Air 5.21.790.7505、Android 13、台版5.9.0／113；測試設備為M2 Mac，macOS 27.0.1。這是當次測試，不是全部機型與版本的相容性保證。

## 尚未完成的事

角色名稱mapping、專武顯示等級交叉驗證、各服路由、憑證壽命與未來版本相容性仍未完整驗證。登入可能更新session，不能承諾伺服器零副作用。

## iPhone路線的結論

曾測試加密本機備份索引與USB容器。索引可解密且SQLite quick_check通過，找到遊戲domain但沒有目標preference；USB容器請求未獲存取。這不證明手機上沒有憑證，也不證明iOS永遠不可行；它只表示該次方法沒有取得目標資料。

本repo不附iPhone備份或索引，避免公開私人App及裝置資訊。
