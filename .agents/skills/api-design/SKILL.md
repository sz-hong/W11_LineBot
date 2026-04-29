---
name: api-design
description: 建立 API 設計，將功能需求轉化為 API 規格
---

## 💡 核心能力

- **需求分析**：從功能需求中提取 API 需求
- **結構化輸出**：生成符合業界標準的 API 設計
- **版本控制**：支援 API 版本管理
- **安全性設計**：設計安全的 API 認證和授權機制

## 🎯 適用場景

- 需要為新功能設計 API
- 需要優化現有 API
- 需要設計 API 規格和文件
- 需要建立 API 認證和授權機制

## 📝 使用範例

### 範例 1：建立新功能 API 設計

**用戶輸入**：
> 我想建立一個線上訂單系統，需要設計 API 規格

**技能輸出**：
```markdown
# API 設計：線上訂單系統

## 1. API 版本

- v1 (初始版本)
- v2 (未來擴展)

## 2. API 端點

### 顧客 API

#### 建立顧客
```http
POST /api/v1/customers
```

**請求**：
```json
{
  "name": "John Doe",
  "email": "[EMAIL_ADDRESS]",
  "phone": "1234567890",
  "address": "123 Main St"
}
```

**響應**：
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "email": "[EMAIL_ADDRESS]",
  "phone": "1234567890",
  "address": "123 Main St",
  "created_at": "2023-01-01T00:00:00Z"
}
```

#### 獲取顧客
```http
GET /api/v1/customers/{customer_id}
```

#### 更新顧客
```http
PUT /api/v1/customers/{customer_id}
```

#### 刪除顧客
```http
DELETE /api/v1/customers/{customer_id}
```

### 產品 API

#### 建立產品
```http
POST /api/v1/products
```

#### 獲取產品
```http
GET /api/v1/products/{product_id}
```

#### 更新產品
```http
PUT /api/v1/products/{product_id}
```

#### 刪除產品
```http
DELETE /api/v1/products/{product_id}
```

### 訂單 API

#### 建立訂單
```http
POST /api/v1/orders
```

#### 獲取訂單
```http
GET /api/v1/orders/{order_id}
```

#### 更新訂單
```http
PUT /api/v1/orders/{order_id}
```

#### 刪除訂單
```http
DELETE /api/v1/orders/{order_id}
```

## 3. 認證和授權

### 認證方式

- API Key
- OAuth 2.0
- JWT

### 權限管理

- 管理員
- 普通用戶
- 訪客

## 4. 錯誤處理

### 常見錯誤碼

- 400 Bad Request
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 500 Internal Server Error

## 5. 版本控制

### 版本升級策略

- 向後兼容
- 逐步淘汰舊版本
- 通知用戶升級

## 6. 效能優化

### 緩存策略
- 產品資料緩存
- 顧客資料緩存
- 訂單狀態緩存

### 分庫分表
- 按客戶分庫
- 按時間分表
- 按區域分表

### 讀寫分離
- 主庫處理寫操作
- 從庫處理讀操作

## 7. 安全考量

- 密碼加密
- 訪問控制
- 資料加密
- SQL 注入防護

## 8. 部署考量

- 支援水平擴展
- 支援 API 監控
- 支援日誌記錄
- 支援災難恢復

## 🔗 相關技能

- [prd](prd.md)：定義產品需求和 API 需求
- [feature-spec](feature-spec.md)：編寫功能規格
- [db-design](db-design.md)：設計資料庫結構
- [implementation](implementation.md)：建立實作規格

## 💡 提示

- 提供清晰的功能需求有助於更好的 API 設計
- 越具體的 API 需求，越容易設計
- 迭代優化是正常過程
- 保持溝通，隨時調整 API 設計

## 💬 交流

如果你有任何問題或建議，請隨時提出！
```