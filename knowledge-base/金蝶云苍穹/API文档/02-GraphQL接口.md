# 金蝶云苍穹GraphQL接口文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-002-iteration7  
**创建时间**: 2026-03-20

---

## 📋 概述

本文档详细说明金蝶云苍穹的GraphQL接口，包括查询语法、Schema定义、最佳实践等内容。

---

## 🔍 GraphQL基础

### 1. Schema定义

**类型定义**:
```graphql
# 用户类型
type User {
  id: ID!
  username: String!
  email: String!
  phone: String
  roles: [Role!]!
  permissions: [String!]!
  createTime: DateTime!
  updateTime: DateTime!
}

# 角色类型
type Role {
  id: ID!
  name: String!
  code: String!
  permissions: [Permission!]!
  users: [User!]!
}

# 权限类型
type Permission {
  id: ID!
  name: String!
  code: String!
  resource: String!
  action: String!
}

# 单据类型
type Bill {
  id: ID!
  billNo: String!
  billDate: Date!
  billType: BillType!
  status: BillStatus!
  customer: Customer
  entries: [BillEntry!]!
  totalAmount: Decimal!
  totalQty: Decimal!
  creator: User!
  createTime: DateTime!
  auditor: User
  auditTime: DateTime
  auditOpinion: String
}

# 单据明细
type BillEntry {
  id: ID!
  seq: Int!
  material: Material!
  qty: Decimal!
  price: Decimal!
  amount: Decimal!
  taxRate: Decimal!
  taxAmount: Decimal!
  remark: String
}

# 客户类型
type Customer {
  id: ID!
  code: String!
  name: String!
  region: String
  level: CustomerLevel!
  creditLimit: Decimal!
  balance: Decimal!
}

# 物料类型
type Material {
  id: ID!
  code: String!
  name: String!
  category: MaterialCategory
  unit: Unit!
  price: Decimal!
  stockQty: Decimal!
}

# 分页信息
type PageInfo {
  pageNum: Int!
  pageSize: Int!
  total: Int!
  pages: Int!
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
}

# 分页结果
type BillConnection {
  edges: [BillEdge!]!
  pageInfo: PageInfo!
}

type BillEdge {
  node: Bill!
  cursor: String!
}

# 枚举类型
enum BillType {
  SALES_ORDER
  PURCHASE_ORDER
  DELIVERY_NOTE
  RECEIPT
}

enum BillStatus {
  DRAFT
  SUBMITTED
  AUDITED
  REJECTED
  CLOSED
}

enum CustomerLevel {
  VIP
  GOLD
  SILVER
  NORMAL
}

# 输入类型
input BillQueryInput {
  billNo: String
  billDateStart: Date
  billDateEnd: Date
  billType: BillType
  status: BillStatus
  customerId: ID
  customerName: String
  minAmount: Decimal
  maxAmount: Decimal
}

input BillCreateInput {
  billType: BillType!
  customerId: ID!
  entries: [BillEntryInput!]!
  remark: String
}

input BillEntryInput {
  materialId: ID!
  qty: Decimal!
  price: Decimal!
  taxRate: Decimal
  remark: String
}

input BillUpdateInput {
  id: ID!
  customerId: ID
  entries: [BillEntryInput!]
  remark: String
}

# 查询根类型
type Query {
  # 用户查询
  user(id: ID!): User
  users(pageNum: Int, pageSize: Int): UserConnection!
  currentUser: User!
  
  # 单据查询
  bill(id: ID!): Bill
  bills(query: BillQueryInput, pageNum: Int, pageSize: Int): BillConnection!
  billByNo(billNo: String!): Bill
  
  # 客户查询
  customer(id: ID!): Customer
  customers(pageNum: Int, pageSize: Int): CustomerConnection!
  searchCustomers(keyword: String!, limit: Int): [Customer!]!
  
  # 物料查询
  material(id: ID!): Material
  materials(pageNum: Int, pageSize: Int): MaterialConnection!
  searchMaterials(keyword: String!, limit: Int): [Material!]!
}

# 变更根类型
type Mutation {
  # 用户操作
  login(username: String!, password: String!): AuthPayload!
  logout: Boolean!
  refreshToken(token: String!): AuthPayload!
  
  # 单据操作
  createBill(input: BillCreateInput!): Bill!
  updateBill(input: BillUpdateInput!): Bill!
  deleteBill(id: ID!): Boolean!
  submitBill(id: ID!): Bill!
  auditBill(id: ID!, result: String!, opinion: String): Bill!
  rejectBill(id: ID!, reason: String!): Bill!
  
  # 批量操作
  batchDeleteBills(ids: [ID!]!): BatchResult!
  batchAuditBills(ids: [ID!]!, result: String!, opinion: String): BatchResult!
}

# 订阅根类型
type Subscription {
  # 单据状态变更
  billStatusChanged(billId: ID): BillStatusPayload!
  
  # 消息通知
  messageReceived(userId: ID!): Message!
}

# 响应类型
type AuthPayload {
  token: String!
  refreshToken: String!
  user: User!
  expiresIn: Int!
}

type BillStatusPayload {
  billId: ID!
  oldStatus: BillStatus!
  newStatus: BillStatus!
  operator: User!
  operateTime: DateTime!
}

type Message {
  id: ID!
  title: String!
  content: String!
  type: MessageType!
  read: Boolean!
  createTime: DateTime!
}

type BatchResult {
  success: Boolean!
  total: Int!
  successCount: Int!
  failCount: Int!
  errors: [BatchError!]
}

type BatchError {
  id: ID!
  message: String!
}

# 标量类型
scalar DateTime
scalar Date
scalar Decimal

enum MessageType {
  INFO
  WARNING
  ERROR
  SUCCESS
}
```

### 2. 查询语法

**基础查询**:
```graphql
# 查询单个单据
query GetBill {
  bill(id: "1001") {
    id
    billNo
    billDate
    billType
    status
    customer {
      id
      code
      name
    }
    entries {
      id
      seq
      material {
        code
        name
      }
      qty
      price
      amount
    }
    totalAmount
    creator {
      username
    }
    createTime
  }
}

# 带参数的查询
query GetBills($query: BillQueryInput, $pageNum: Int, $pageSize: Int) {
  bills(query: $query, pageNum: $pageNum, pageSize: $pageSize) {
    edges {
      node {
        id
        billNo
        billDate
        status
        totalAmount
      }
    }
    pageInfo {
      pageNum
      pageSize
      total
      pages
      hasNextPage
    }
  }
}

# 查询变量
{
  "query": {
    "billDateStart": "2026-01-01",
    "billDateEnd": "2026-03-20",
    "status": "AUDITED"
  },
  "pageNum": 1,
  "pageSize": 20
}

# 使用片段
query GetBillWithDetails($id: ID!) {
  bill(id: $id) {
    ...BillBasicInfo
    ...BillCustomerInfo
    ...BillEntriesInfo
  }
}

fragment BillBasicInfo on Bill {
  id
  billNo
  billDate
  billType
  status
  totalAmount
}

fragment BillCustomerInfo on Bill {
  customer {
    id
    code
    name
    region
    level
  }
}

fragment BillEntriesInfo on Bill {
  entries {
    id
    seq
    material {
      code
      name
      unit {
        name
      }
    }
    qty
    price
    amount
  }
}

# 多个查询
query GetDashboard {
  currentUser {
    id
    username
    roles {
      name
    }
  }
  
  recentBills: bills(query: {}, pageNum: 1, pageSize: 10) {
    edges {
      node {
        id
        billNo
        billDate
        totalAmount
      }
    }
  }
  
  topCustomers: searchCustomers(keyword: "", limit: 10) {
    id
    code
    name
  }
}
```

### 3. 变更操作

**创建单据**:
```graphql
mutation CreateBill {
  createBill(input: {
    billType: SALES_ORDER
    customerId: "1001"
    entries: [
      {
        materialId: "2001"
        qty: 10
        price: 100.00
        taxRate: 0.13
      },
      {
        materialId: "2002"
        qty: 20
        price: 50.00
        taxRate: 0.13
      }
    ]
    remark: "测试订单"
  }) {
    id
    billNo
    billDate
    status
    totalAmount
    entries {
      id
      seq
      qty
      price
      amount
    }
  }
}
```

**更新单据**:
```graphql
mutation UpdateBill {
  updateBill(input: {
    id: "1001"
    customerId: "1002"
    entries: [
      {
        materialId: "2001"
        qty: 15
        price: 100.00
        taxRate: 0.13
      }
    ]
  }) {
    id
    billNo
    status
    totalAmount
  }
}
```

**提交和审核**:
```graphql
mutation SubmitAndAudit {
  # 提交单据
  submit: submitBill(id: "1001") {
    id
    status
  }
  
  # 审核单据
  audit: auditBill(id: "1001", result: "PASS", opinion: "审核通过") {
    id
    status
    auditor {
      username
    }
    auditTime
  }
}
```

### 4. 订阅操作

**订阅单据状态变更**:
```graphql
subscription OnBillStatusChanged {
  billStatusChanged(billId: "1001") {
    billId
    oldStatus
    newStatus
    operator {
      username
    }
    operateTime
  }
}
```

---

## 🔧 GraphQL实现

### 1. 服务端实现

**GraphQL配置**:
```java
@Configuration
public class GraphQLConfig {
    
    @Bean
    public GraphQLScalarType dateTimeScalar() {
        return GraphQLScalarType.newScalar()
            .name("DateTime")
            .description("Date Time scalar")
            .coercing(new Coercing<LocalDateTime, String>() {
                @Override
                public String serialize(Object dataFetcherResult) {
                    if (dataFetcherResult instanceof LocalDateTime) {
                        return ((LocalDateTime) dataFetcherResult)
                            .format(DateTimeFormatter.ISO_DATE_TIME);
                    }
                    throw new CoercingSerializeException("Invalid DateTime");
                }
                
                @Override
                public LocalDateTime parseValue(Object input) {
                    try {
                        if (input instanceof String) {
                            return LocalDateTime.parse((String) input);
                        }
                    } catch (DateTimeParseException e) {
                        throw new CoercingParseValueException(e);
                    }
                    throw new CoercingParseValueException("Invalid DateTime");
                }
                
                @Override
                public LocalDateTime parseLiteral(Object input) {
                    if (input instanceof StringValue) {
                        try {
                            return LocalDateTime.parse(
                                ((StringValue) input).getValue());
                        } catch (DateTimeParseException e) {
                            throw new CoercingParseLiteralException(e);
                        }
                    }
                    throw new CoercingParseLiteralException("Invalid DateTime");
                }
            })
            .build();
    }
}
```

**DataFetcher实现**:
```java
@Component
public class GraphQLDataFetchers {
    
    @Autowired
    private BillService billService;
    
    @Autowired
    private CustomerService customerService;
    
    /**
     * 查询单据
     */
    @SchemaMapping(typeName = "Query", field = "bill")
    public Bill getBill(@Argument String id) {
        return billService.getBillById(id);
    }
    
    /**
     * 查询单据列表
     */
    @SchemaMapping(typeName = "Query", field = "bills")
    public BillConnection getBills(@Argument BillQueryInput query,
                                    @Argument Integer pageNum,
                                    @Argument Integer pageSize) {
        return billService.queryBills(query, pageNum, pageSize);
    }
    
    /**
     * 创建单据
     */
    @SchemaMapping(typeName = "Mutation", field = "createBill")
    public Bill createBill(@Argument BillCreateInput input) {
        return billService.createBill(input);
    }
    
    /**
     * 更新单据
     */
    @SchemaMapping(typeName = "Mutation", field = "updateBill")
    public Bill updateBill(@Argument BillUpdateInput input) {
        return billService.updateBill(input);
    }
    
    /**
     * 单据客户关联
     */
    @SchemaMapping(typeName = "Bill", field = "customer")
    public Customer getBillCustomer(Bill bill) {
        if (bill.getCustomerId() == null) {
            return null;
        }
        return customerService.getCustomerById(bill.getCustomerId());
    }
    
    /**
     * 单据明细
     */
    @SchemaMapping(typeName = "Bill", field = "entries")
    public List<BillEntry> getBillEntries(Bill bill) {
        return billService.getBillEntries(bill.getId());
    }
}
```

---

## ✅ 最佳实践

### 1. 查询优化

**使用DataLoader避免N+1问题**:
```java
@Component
public class CustomerDataLoader implements BatchLoader<String, Customer> {
    
    @Autowired
    private CustomerService customerService;
    
    @Override
    public CompletionStage<List<Customer>> load(List<String> keys) {
        return CompletableFuture.supplyAsync(() -> {
            // 批量查询客户
            Map<String, Customer> customerMap = customerService
                .getCustomersByIds(keys);
            
            // 按顺序返回结果
            return keys.stream()
                .map(customerMap::get)
                .collect(Collectors.toList());
        });
    }
}

@Configuration
public class DataLoaderConfig {
    
    @Bean
    public DataLoaderRegistry dataLoaderRegistry(
            CustomerDataLoader customerDataLoader) {
        DataLoaderRegistry registry = new DataLoaderRegistry();
        registry.register("customerLoader", 
            DataLoader.newDataLoader(customerDataLoader));
        return registry;
    }
}
```

---

## 📚 相关文档

- [REST API参考](01-REST API参考.md)
- [WebSocket接口](02-WebSocket接口.md)
- [插件开发深入](../二开文档/14-插件开发深入.md)

---

**文档版本**: v1.0  
**最后更新**: 2026-03-20  
**维护者**: 尚书省·工部
