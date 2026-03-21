# 金蝶云苍穹GraphQL API文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-002-iteration7  
**创建时间**: 2026-03-20

---

## 📋 GraphQL概述

### 1. Schema定义

```graphql
type Query {
  # 单据查询
  bill(billId: ID!): Bill
  bills(filter: BillFilter!, page: PaginationInput): BillConnection
  
  # 客户查询
  customer(customerId: ID!): Customer
  customers(filter: CustomerFilter!, page: PaginationInput): CustomerConnection
  
  # 用户查询
  user(userId: ID!): User
  users(filter: UserFilter!, page: PaginationInput): UserConnection
}

type Mutation {
  # 单据操作
  createBill(input: CreateBillInput!): Bill!
  updateBill(billId: ID!, input: UpdateBillInput!): Bill!
  deleteBill(billId: ID!): Boolean!
  
  # 客户操作
  createCustomer(input: CreateCustomerInput!): Customer!
  updateCustomer(customerId: ID!, input: UpdateCustomerInput!): Customer!
  deleteCustomer(customerId: ID!): Boolean!
}

type Subscription {
  # 实时订阅
  billUpdated(billId: ID!): Bill!
  customerCreated: Customer!
  userLoggedIn: User!
}
```

### 2. 类型定义

```graphql
# 单据类型
type Bill {
  billId: ID!
  billNo: String!
  billDate: Date!
  status: BillStatus!
  amount: Decimal!
  customerId: ID!
  customer: Customer
  entries: [BillEntry!]!
  createTime: DateTime!
  updateTime: DateTime!
}

enum BillStatus {
  DRAFT
  SUBMITTED
  APPROVED
  REJECTED
}

# 单据明细
type BillEntry {
  entryId: ID!
  billId: ID!
  productId: ID!
  product: Product
  quantity: Decimal!
  price: Decimal!
  amount: Decimal!
}

# 客户类型
type Customer {
  customerId: ID!
  customerName: String!
  customerCode: String!
  customerType: CustomerType!
  contactPerson: String
  phoneNumber: String
  email: String
  address: String
  createTime: DateTime!
  updateTime: DateTime!
}

enum CustomerType {
  INDIVIDUAL
  ENTERPRISE
}

# 分页连接
interface Connection {
  edges: [Edge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type BillConnection implements Connection {
  edges: [BillEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

interface Edge {
  node: Node!
  cursor: String!
}

type BillEdge implements Edge {
  node: Bill!
  cursor: String!
}

interface Node {
  id: ID!
}

# 分页信息
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# 分页输入
input PaginationInput {
  first: Int
  last: Int
  after: String
  before: String
}

# 筛选条件
input BillFilter {
  billNo: StringFilter
  billDate: DateFilter
  status: BillStatus
  customerId: ID
  amount: DecimalFilter
  createTime: DateTimeFilter
}

input StringFilter {
  eq: String
  contains: String
  startsWith: String
  endsWith: String
  in: [String!]
}

input DateFilter {
  eq: Date
  gte: Date
  gt: Date
  lte: Date
  lt: Date
}

# 创建输入
input CreateBillInput {
  billNo: String!
  billDate: Date!
  customerId: ID!
  amount: Decimal!
  entries: [CreateBillEntryInput!]!
  remarks: String
}

input CreateBillEntryInput {
  productId: ID!
  quantity: Decimal!
  price: Decimal!
  amount: Decimal!
}
```

### 3. 查询示例

```graphql
# 查询单据详情
query GetBill($billId: ID!) {
  bill(billId: $billId) {
    billId
    billNo
    billDate
    status
    amount
    customer {
      customerId
      customerName
      customerCode
    }
    entries {
      entryId
      product {
        productId
        productName
        productCode
      }
      quantity
      price
      amount
    }
  }
}

# 分页查询单据
query GetBills($filter: BillFilter!, $page: PaginationInput!) {
  bills(filter: $filter, page: $page) {
    edges {
      node {
        billId
        billNo
        billDate
        status
        amount
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}

# 创建单据
mutation CreateBill($input: CreateBillInput!) {
  createBill(input: $input) {
    billId
    billNo
    billDate
    status
    amount
  }
}

# 订阅单据更新
subscription OnBillUpdated($billId: ID!) {
  billUpdated(billId: $billId) {
    billId
    billNo
    status
    amount
  }
}
```

---

## 🌐 WebSocket API文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-002-iteration8  
**创建时间**: 2026-03-20

---

## 📋 WebSocket概述

### 1. 连接配置

```javascript
// WebSocket连接
const ws = new WebSocket('ws://k3cloud.yourdomain.com/ws');

// 连接事件
ws.onopen = (event) => {
  console.log('WebSocket connected:', event);
  
  // 发送认证消息
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

ws.onclose = (event) => {
  console.log('WebSocket disconnected:', event);
  
  // 自动重连
  setTimeout(() => {
    reconnect();
  }, 3000);
};

ws.onerror = (event) => {
  console.error('WebSocket error:', event);
};

// 心跳保活
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'ping',
      timestamp: Date.now()
    }));
  }
}, 30000);
```

### 2. 消息协议

```typescript
// 消息类型
interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: number;
  id?: string;
}

// 认证消息
interface AuthMessage extends WebSocketMessage {
  type: 'auth';
  token: string;
}

// 心跳消息
interface PingMessage extends WebSocketMessage {
  type: 'ping';
  timestamp: number;
}

// 订阅消息
interface SubscribeMessage extends WebSocketMessage {
  type: 'subscribe';
  topic: string;
}

// 取消订阅消息
interface UnsubscribeMessage extends WebSocketMessage {
  type: 'unsubscribe';
  topic: string;
}

// 通知消息
interface NotificationMessage extends WebSocketMessage {
  type: 'notification';
  notificationId: string;
  title: string;
  content: string;
  type: 'info' | 'warning' | 'error';
  timestamp: number;
}

// 单据更新消息
interface BillUpdateMessage extends WebSocketMessage {
  type: 'bill_update';
  billId: string;
  billNo: string;
  status: string;
  oldStatus: string;
  updateTime: number;
}

// 用户登录消息
interface UserLoginMessage extends WebSocketMessage {
  type: 'user_login';
  userId: string;
  username: string;
  loginTime: number;
  ipAddress: string;
}
```

### 3. 实时推送

```typescript
// 订阅单据更新
const subscribeBillUpdates = (billId: string) => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    topic: `bill:${billId}`
  }));
};

// 订阅所有通知
const subscribeNotifications = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    topic: 'notifications'
  }));
};

// 订阅用户登录事件
const subscribeUserLogin = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    topic: 'user:login'
  }));
};

// 消息处理
const handleMessage = (message: WebSocketMessage) => {
  switch (message.type) {
    case 'notification':
      handleNotification(message as NotificationMessage);
      break;
    case 'bill_update':
      handleBillUpdate(message as BillUpdateMessage);
      break;
    case 'user_login':
      handleUserLogin(message as UserLoginMessage);
      break;
    case 'pong':
      // 心跳响应
      break;
    default:
      console.warn('Unknown message type:', message.type);
  }
};
```

### 4. 断线重连

```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  
  connect(url: string, token: string) {
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.authenticate(token);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect(url, token);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }
  
  private authenticate(token: string) {
    this.ws?.send(JSON.stringify({
      type: 'auth',
      token: token
    }));
  }
  
  private reconnect(url: string, token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
        this.connect(url, token);
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    } else {
      console.error('Max reconnect attempts reached');
    }
  }
}
```

---

**文档版本**: v8.0  
**最后更新**: 2026-03-20 (迭代7-8）  
**作者**: 太子
