# 金蝶云苍穹 REST API 参考文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-001  
**创建时间**: 2026-03-20

---

## 📋 概述

金蝶云苍穹提供完整的RESTful API，支持单据操作、数据查询、文件管理等核心功能。

## 🔧 API基础

### 1. 认证授权

**获取访问令牌（JSON）**:
```json
POST /api/oauth2/token
{
  "grant_type": "password",
  "username": "your_username",
  "password": "your_password",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "refresh_token_here"
}
```

**获取访问令牌（C#）**:
```csharp
using K3Cloud.API.Authentication;

public class AuthClient
{
    private readonly HttpClient _httpClient;
    private readonly string _clientId;
    private readonly string _clientSecret;
    
    public AuthClient(string clientId, string clientSecret)
    {
        _httpClient = new HttpClient();
        _clientId = clientId;
        _clientSecret = clientSecret;
    }
    
    public async Task<AuthToken> GetAccessTokenAsync(string username, string password)
    {
        var request = new TokenRequest
        {
            GrantType = "password",
            Username = username,
            Password = password,
            ClientId = _clientId,
            ClientSecret = _clientSecret
        };
        
        var response = await _httpClient.PostAsJsonAsync("/api/oauth2/token", request);
        return await response.Content.ReadAsAsync<AuthToken>();
    }
}

public class AuthToken
{
    public string AccessToken { get; set; }
    public string TokenType { get; set; }
    public int ExpiresIn { get; set; }
    public string RefreshToken { get; set; }
}
```

### 2. API端点

**基础URL**:
- 生产环境: `https://api.kingdee.com`
- 开发环境: `https://dev-api.kingdee.com`

**通用请求头**:
```javascript
{
  "Authorization": "Bearer {access_token}",
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

## 📚 核心API

### 1. 单据操作API

#### 1.1 创建单据

**创建单据请求（JSON）**:
```json
POST /api/bill/create
{
  "billFormId": "kdev_custom_bill",
  "data": {
    "bill_no": "CUSTOM_BILL_001",
    "bill_date": "2026-03-20",
    "status": "draft",
    "entries": [
      {
        "entry_no": 1,
        "product_id": "PROD_001",
        "quantity": 100,
        "price": 150.00
      }
    ]
  }
}

Response:
{
  "status": "success",
  "message": "单据创建成功",
  "data": {
    "billId": "BILL_20260320_001",
    "billNo": "CUSTOM_BILL_001",
    "createTime": "2026-03-20T00:00:00Z"
  }
}
```

**创建单据请求（C#）**:
```csharp
using K3Cloud.API.Bill;

public class BillService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUri;
    
    public BillService(HttpClient httpClient, string baseUri)
    {
        _httpClient = httpClient;
        _baseUri = baseUri;
    }
    
    public async Task<BillResponse> CreateBillAsync(BillRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync(
            $"{_baseUri}/api/bill/create", 
            request
        );
        
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadAsAsync<BillResponse>();
    }
}

public class BillRequest
{
    public string BillFormId { get; set; }
    public BillData Data { get; set; }
}

public class BillData
{
    public string BillNo { get; set; }
    public string BillDate { get; set; }
    public string Status { get; set; }
    public List<BillEntry> Entries { get; set; }
}

public class BillResponse
{
    public string Status { get; set; }
    public string Message { get; set; }
    public BillResult Data { get; set; }
}

public class BillResult
{
    public string BillId { get; set; }
    public string BillNo { get; set; }
    public DateTime CreateTime { get; set; }
}
```

#### 1.2 查询单据

**查询单据请求（JSON）**:
```json
POST /api/bill/query
{
  "billFormId": "kdev_custom_bill",
  "filters": [
    {
      "field": "bill_no",
      "operator": "=",
      "value": "CUSTOM_BILL_001"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "orderBy": "bill_date",
    "order": "desc"
  }
}

Response:
{
  "status": "success",
  "data": {
    "total": 1,
    "page": 1,
    "pageSize": 20,
    "rows": [
      {
        "billId": "BILL_20260320_001",
        "billNo": "CUSTOM_BILL_001",
        "billDate": "2026-03-20",
        "status": "submitted",
        "entries": [...]
      }
    ]
  }
}
```

**查询单据请求（C#）**:
```csharp
public class BillQueryService
{
    public async Task<QueryResponse<Bill>> QueryBillsAsync(BillQueryRequest request)
    {
        var response = await _httpClient.PostAsJsonAsync(
            $"{_baseUri}/api/bill/query", 
            request
        );
        
        return await response.Content.ReadAsAsync<QueryResponse<Bill>>();
    }
}

public class BillQueryRequest
{
    public string BillFormId { get; set; }
    public List<Filter> Filters { get; set; }
    public Pagination Pagination { get; set; }
}

public class Filter
{
    public string Field { get; set; }
    public string Operator { get; set; }  // =, !=, >, <, >=, <=, like, in
    public object Value { get; set; }
}

public class Pagination
{
    public int Page { get; set; }
    public int PageSize { get; set; }
    public string OrderBy { get; set; }
    public string Order { get; set; }  // asc, desc
}

public class QueryResponse<T>
{
    public string Status { get; set; }
    public QueryData<T> Data { get; set; }
}

public class QueryData<T>
{
    public int Total { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
    public List<T> Rows { get; set; }
}
```

### 2. 数据查询API

#### 2.1 基础资料查询

**查询基础资料（JSON）**:
```json
POST /api/base/query
{
  "entityName": "kdev_product",
  "filters": [
    {
      "field": "status",
      "operator": "=",
      "value": "active"
    }
  ],
  "fields": ["product_id", "product_name", "price", "category"],
  "pagination": {
    "page": 1,
    "pageSize": 50
  }
}

Response:
{
  "status": "success",
  "data": {
    "total": 100,
    "rows": [
      {
        "productId": "PROD_001",
        "productName": "产品A",
        "price": 150.00,
        "category": "category_01"
      }
    ]
  }
}
```

**查询基础资料（C#）**:
```csharp
public class BaseDataService
{
    public async Task<QueryResponse<BaseEntity>> QueryBaseDataAsync(
        string entityName, 
        List<Filter> filters,
        List<string> fields = null,
        Pagination pagination = null)
    {
        var request = new BaseDataQueryRequest
        {
            EntityName = entityName,
            Filters = filters,
            Fields = fields,
            Pagination = pagination ?? new Pagination { Page = 1, PageSize = 50 }
        };
        
        var response = await _httpClient.PostAsJsonAsync(
            $"{_baseUri}/api/base/query", 
            request
        );
        
        return await response.Content.ReadAsAsync<QueryResponse<BaseEntity>>();
    }
}

public class BaseEntity
{
    public string EntityId { get; set; }
    public string EntityName { get; set; }
    public Dictionary<string, object> Properties { get; set; }
}
```

### 3. 文件操作API

#### 3.1 上传文件

**上传文件请求（JSON）**:
```json
POST /api/file/upload
Content-Type: multipart/form-data

{
  "file": <binary data>,
  "folderId": "folder_001",
  "fileType": "document"
}

Response:
{
  "status": "success",
  "data": {
    "fileId": "FILE_20260320_001",
    "fileName": "document.pdf",
    "fileSize": 1024000,
    "url": "https://files.kingdee.com/FILE_20260320_001.pdf",
    "uploadTime": "2026-03-20T00:00:00Z"
  }
}
```

**上传文件请求（C#）**:
```csharp
using System.IO;

public class FileService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUri;
    
    public async Task<FileUploadResponse> UploadFileAsync(
        string filePath, 
        string folderId = null,
        string fileType = null)
    {
        using var form = new MultipartFormDataContent();
        using var fileStream = File.OpenRead(filePath);
        using var fileContent = new StreamContent(fileStream);
        
        form.Add(fileContent, "file", Path.GetFileName(filePath));
        if (!string.IsNullOrEmpty(folderId))
        {
            form.Add(new StringContent(folderId), "folderId");
        }
        if (!string.IsNullOrEmpty(fileType))
        {
            form.Add(new StringContent(fileType), "fileType");
        }
        
        var response = await _httpClient.PostAsync(
            $"{_baseUri}/api/file/upload", 
            form
        );
        
        return await response.Content.ReadAsAsync<FileUploadResponse>();
    }
}

public class FileUploadResponse
{
    public string Status { get; set; }
    public FileData Data { get; set; }
}

public class FileData
{
    public string FileId { get; set; }
    public string FileName { get; set; }
    public long FileSize { get; set; }
    public string Url { get; set; }
    public DateTime UploadTime { get; set; }
}
```

## 🎯 错误处理

### 错误响应格式
```json
{
  "status": "error",
  "code": "AUTH_001",
  "message": "访问令牌无效或已过期",
  "details": {
    "error": "invalid_token",
    "timestamp": "2026-03-20T00:00:00Z"
  }
}
```

### 常见错误代码
| 错误代码 | 说明 | 解决方案 |
|---------|------|----------|
| AUTH_001 | 访问令牌无效 | 重新获取访问令牌 |
| AUTH_002 | 访问令牌过期 | 使用刷新令牌或重新登录 |
| AUTH_003 | 权限不足 | 检查用户权限 |
| BILL_001 | 单据不存在 | 确认单据ID |
| BILL_002 | 单据状态不允许 | 检查单据当前状态 |
| VALIDATION_001 | 数据验证失败 | 检查请求参数 |
| VALIDATION_002 | 必填字段缺失 | 补充必填字段 |

## 📊 性能优化

### 1. 批量操作
```javascript
// 批量创建单据
POST /api/bill/batch_create
{
  "bills": [
    {...},
    {...},
    {...}
  ]
}
```

### 2. 分页查询
```javascript
// 使用分页减少数据传输量
POST /api/bill/query
{
  "pagination": {
    "page": 1,
    "pageSize": 50
  }
}
```

### 3. 字段过滤
```javascript
// 只查询需要的字段
POST /api/bill/query
{
  "fields": ["bill_id", "bill_no", "status"]
}
```

## 🛠️ 最佳实践

### 1. 认证管理
- 妥善保管访问令牌和密钥
- 定期刷新访问令牌
- 使用HTTPS协议

### 2. 错误处理
- 实现重试机制
- 记录错误日志
- 提供友好的错误提示

### 3. 性能优化
- 使用批量操作
- 合理使用分页
- 缓存常用数据

## 📚 相关资源

- **API文档**: https://developer.kingdee.com/api
- **SDK下载**: https://developer.kingdee.com/sdk
- **示例代码**: https://developer.kingdee.com/demo/api

---

**文档版本**: v8.0  
**最后更新**: 2026-03-20  
**作者**: 太子
