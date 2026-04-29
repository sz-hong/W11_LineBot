---
name: implementation
description: 建立實作規格，將功能需求轉化為技術實作細節
---

## 💡 核心能力

- **需求分析**：從功能規格中提取技術實作細節
- **結構化輸出**：生成符合業界標準的實作規格格式
- **技術細節設計**：設計 API 介面、資料結構和演算法
- **迭代優化**：根據反饋持續改進實作規格

## 🎯 適用場景

- 需要將功能規格轉化為技術實作
- 需要為開發團隊提供明確的實作指引
- 需要設計 API 介面和資料結構
- 需要定義演算法和處理邏輯

## 📝 使用範例

### 範例 1：建立新功能實作規格

**用戶輸入**：
> 我想建立一個線上訂單處理功能，包含訂單接收、付款處理和庫存檢查

**技能輸出**：
```markdown
# 實作規格：線上訂單處理功能

## 1. 功能概述
建立一個線上訂單處理功能，包含訂單接收、付款處理和庫存檢查。

## 2. API 介面設計

### 建立訂單
```http
POST /api/orders

Request:
{
  "items": [
    {
      "productId": "123",
      "quantity": 2
    }
  ],
  "shippingAddress": {
    "street": "123 Main St",
    "city": "Taipei",
    "zip": "10001"
  }
}

Response:
{
  "orderId": "ORD-2024-001",
  "status": "pending",
  "total": 99.99,
  "createdAt": "2024-01-15T10:00:00Z"
}
```

### 處理付款
```http
POST /api/orders/{orderId}/pay

Request:
{
  "paymentMethod": "credit_card",
  "cardNumber": "...",
  "expiryDate": "...",
  "cvv": "..."
}

Response:
{
  "status": "paid",
  "paidAt": "2024-01-15T10:05:00Z"
}
```

### 檢查庫存
```http
GET /api/products/{productId}/stock

Response:
{
  "productId": "123",
  "stock": 15,
  "available": true
}
```

## 3. 資料結構設計

### 訂單資料結構
```typescript
interface Order {
  orderId: string;
  userId: string;
  items: OrderItem[];
  shippingAddress: Address;
  status: OrderStatus;
  total: number;
  createdAt: Date;
  updatedAt: Date;
}

type OrderStatus = 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
```

### 庫存資料結構
```typescript
interface ProductStock {
  productId: string;
  stock: number;
  reserved: number;
  available: boolean;
}
```

## 4. 處理邏輯

### 訂單建立流程
1. 接收訂單請求
2. 驗證商品和庫存
3. 建立訂單記錄
4. 預留庫存
5. 返回訂單確認

### 付款處理流程
1. 接收付款請求
2. 驗證付款信息
3. 處理付款交易
4. 更新訂單狀態
5. 釋放預留庫存

### 庫存管理
- 訂單建立時預留庫存
- 付款成功後扣除庫存
- 缺貨時拒絕訂單
- 定時清理過期預留

## 5. 錯誤處理

### 常見錯誤
- 庫存不足：返回 400 錯誤
- 付款失敗：返回 400 錯誤
- 無效訂單：返回 400 錯誤
- 系統錯誤：返回 500 錯誤

### 錯誤響應範例
```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "庫存不足，請減少訂購數量"
  }
}
```

## 6. 測試案例

### 成功案例
- 正常訂單建立和付款
- 多商品訂單
- 使用不同付款方式

### 邊界案例
- 訂購最後一個商品
- 訂購量超過庫存
- 快速連續訂單

### 錯誤案例
- 庫存不足
- 無效付款信息
- 訂單信息錯誤

## 7. 效能考量

- 訂單建立：< 200ms
- 付款處理：< 500ms
- 庫存檢查：< 50ms
- 高併發支援：支援每秒 1000+ 訂單

## 8. 安全考量

- 付款信息加密
- 庫存操作原子性
- 訂單數據加密
- 訪問控制

## 9. 部署考量

- 支援水平擴展
- 支援資料庫備份
- 支援監控和日誌
- 支援災難恢復

## 10. 實施路線圖

### 第一階段：基礎功能
- 訂單建立
- 庫存檢查
- 付款處理

### 第二階段：進階功能
- 訂單管理
- 退款處理
- 庫存預留

### 第三階段：優化
- 效能優化
- 安全加強
- 監控完善

## 🔗 相關技能

- [prd](prd.md)：定義產品需求和功能
- [feature-spec](feature-spec.md)：編寫功能規格
- [api-design](api-design.md)：設計 API 介面
- [db-design](db-design.md)：設計資料庫結構
- [ux-design](ux-design.md)：設計用戶體驗

## 💡 提示

- 提供清晰的功能需求有助於更好的實作規格
- 越具體的技術細節，越容易實作
- 迭代優化是正常過程
- 保持溝通，隨時調整實作規格

## 💬 交流

如果你有任何問題或建議，請隨時提出！
```