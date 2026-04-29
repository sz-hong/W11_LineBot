---
name: commit
description: 產出符合 Conventional Commits 規範的 Git commit message
---

## 💡 核心能力

- **自動分析變更**：根據 `git diff` 或變更描述，自動判斷 commit type
- **結構化輸出**：產出符合 Conventional Commits 格式的 commit message
- **中文描述**：支援繁體中文的 commit 描述
- **多行訊息**：支援 subject + body + footer 完整格式

## 🎯 適用場景

- 完成功能開發後需要 commit
- 修復 bug 後需要 commit
- 更新文件後需要 commit
- 重構程式碼後需要 commit

## 📋 Commit Type 對照表

| Type | 說明 | 使用時機 |
|------|------|----------|
| `feat` | 新功能 | 新增功能、新增 API endpoint |
| `fix` | 修復 | 修復 bug、修正錯誤行為 |
| `docs` | 文件 | 更新 README、新增 PRD、修改註解 |
| `style` | 格式 | 程式碼格式調整（不影響邏輯） |
| `refactor` | 重構 | 重構程式碼（不新增功能也不修 bug） |
| `test` | 測試 | 新增或修改測試 |
| `chore` | 雜務 | 更新依賴、設定檔調整 |
| `init` | 初始化 | 專案初始建立 |

## ⚠️ 注意事項

### 1. 格式規範
```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**：必填，從上方對照表選擇
- **scope**：選填，影響範圍（如 `app`、`db`、`linebot`）
- **subject**：必填，簡短描述（不超過 50 字元）
- **body**：選填，詳細說明變更內容
- **footer**：選填，Breaking Changes 或關聯 Issue

### 2. Subject 撰寫規則
- 使用祈使語氣（「新增」而非「新增了」）
- 不加句號
- 首字母不需大寫（中文無此規則）
- 簡短但有意義

### 3. 中文 commit 範例
- ✅ `feat(linebot): 新增股票查詢功能`
- ✅ `fix(db): 修復追蹤清單重複新增問題`
- ✅ `docs: 更新 README 心得報告`
- ❌ `update code`（太模糊）
- ❌ `修改了一些東西`（無意義）

## 📝 使用範例

### 範例 1：新功能 commit

**用戶輸入**：
> 我剛完成了股票查詢功能，可以用 twstock 查詢即時股價

**技能輸出**：
```
feat(stock): 新增台股即時價格查詢功能

- 整合 twstock 套件查詢即時股價
- 支援股票代號和名稱搜尋
- 顯示即時價格、漲跌幅、成交量
```

### 範例 2：修復 bug commit

**用戶輸入**：
> 修復了當股票代號不存在時程式會 crash 的問題

**技能輸出**：
```
fix(stock): 修復無效股票代號導致程式崩潰

- 新增股票代號驗證邏輯
- 查無股票時回覆友善提示訊息
- 加入 try/except 錯誤處理
```

### 範例 3：初始化專案 commit

**用戶輸入**：
> 專案初始建立，包含 app.py、requirements.txt、.env.example 和 Skills

**技能輸出**：
```
init: 初始化股票 LINE Bot 專案

- 建立 FastAPI + LINE Bot + Gemini + SQLite 主程式
- 設定 requirements.txt 依賴套件
- 建立 .env.example 環境變數範本
- 建立 linebot-implement、prd、commit Skills
- 建立 docs/PRD.md 產品需求文件
```

## 📊 輸出格式

```
<type>(<scope>): <簡短描述>

<詳細說明，使用條列式>
- 變更項目 1
- 變更項目 2
- 變更項目 3
```

## 🔗 相關技能

- [linebot-implement](../linebot-implement/SKILL.md)：產出 LINE Bot 主程式
- [prd](../prd/SKILL.md)：定義產品需求

## 💡 提示

- 每次 commit 應該是一個獨立的、有意義的變更
- 避免一次 commit 太多不相關的變更
- commit message 是給人看的，要清楚易懂
