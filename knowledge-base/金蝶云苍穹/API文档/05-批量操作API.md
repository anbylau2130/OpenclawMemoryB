# 金蝶云苍穹 - 批量操作API

> 文档版本: v1.0
> 更新时间: 2026-03-21
> 维护者: 礼部

---

## 一、概述

批量操作API用于高效处理大量数据，支持批量创建、更新、删除等操作。

### 1.1 批量操作限制

| 限制项 | 限制值 | 说明 |
|-------|-------|------|
| 单次批量数量 | 1000条 | 单次最多处理1000条记录 |
| 并发批量任务 | 10个 | 同时运行的批量任务数 |
| 任务超时时间 | 30分钟 | 单个任务最大执行时间 |
| 文件大小限制 | 50MB | 批量导入文件最大50MB |

---

## 二、批量创建API

### 2.1 批量创建单据

**请求**:
```http
POST /api/v1/bill/batch_create
Content-Type: application/json
Authorization: Bearer {token}

{
  "formId": "kdev_salesorder",
  "bills": [
    {
      "billNo": "SO20260321001",
      "customerId": "100001",
      "date": "2026-03-21",
      "entries": [
        {
          "materialId": "M001",
          "qty": 10,
          "price": 100
        }
      ]
    },
    {
      "billNo": "SO20260321002",
      "customerId": "100002",
      "date": "2026-03-21",
      "entries": [
        {
          "materialId": "M002",
          "qty": 20,
          "price": 200
        }
      ]
    }
  ],
  "options": {
    "validateOnly": false,     // 仅校验不保存
    "stopOnError": false,      // 遇错停止
    "skipDuplicate": true      // 跳过重复数据
  }
}
```

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "taskId": "TASK_20260321_001",
    "status": "completed",
    "total": 2,
    "success": 2,
    "failed": 0,
    "results": [
      {
        "index": 0,
        "success": true,
        "billId": "100001",
        "billNo": "SO20260321001"
      },
      {
        "index": 1,
        "success": true,
        "billId": "100002",
        "billNo": "SO20260321002"
      }
    ]
  }
}
```

### 2.2 异步批量创建

**发起异步任务**:
```http
POST /api/v1/bill/batch_create_async
Content-Type: application/json
Authorization: Bearer {token}

{
  "formId": "kdev_salesorder",
  "bills": [...],  // 最多1000条
  "callback": {
    "url": "https://your-server.com/callback",
    "method": "POST",
    "headers": {
      "X-Signature": "{signature}"
    }
  }
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "taskId": "TASK_20260321_001",
    "status": "pending",
    "estimatedTime": 120  // 预计完成时间(秒)
  }
}
```

---

## 三、批量更新API

### 3.1 批量更新单据

**请求**:
```http
POST /api/v1/bill/batch_update
Content-Type: application/json
Authorization: Bearer {token}

{
  "formId": "kdev_salesorder",
  "updates": [
    {
      "id": "100001",
      "data": {
        "status": "audited",
        "auditor": "admin",
        "auditTime": "2026-03-21T10:00:00Z"
      }
    },
    {
      "id": "100002",
      "data": {
        "status": "audited",
        "auditor": "admin",
        "auditTime": "2026-03-21T10:00:00Z"
      }
    }
  ],
  "options": {
    "checkStatus": true,    // 检查状态是否允许更新
    "triggerWorkflow": true // 触发工作流
  }
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "taskId": "TASK_20260321_002",
    "total": 2,
    "success": 2,
    "failed": 0,
    "results": [...]
  }
}
```

### 3.2 批量字段更新

**按条件批量更新**:
```http
POST /api/v1/bill/batch_update_by_filter
Content-Type: application/json

{
  "formId": "kdev_salesorder",
  "filter": {
    "field": "status",
    "operator": "=",
    "value": "draft"
  },
  "update": {
    "status": "voided",
    "voidReason": "批量作废"
  }
}
```

---

## 四、批量删除API

### 4.1 批量删除单据

**请求**:
```http
POST /api/v1/bill/batch_delete
Content-Type: application/json
Authorization: Bearer {token}

{
  "formId": "kdev_salesorder",
  "ids": ["100001", "100002", "100003"],
  "options": {
    "checkStatus": true,     // 检查状态
    "deleteRelated": false,  // 删除关联数据
    "backup": true           // 备份删除数据
  }
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 3,
    "success": 2,
    "failed": 1,
    "results": [
      {
        "id": "100001",
        "success": true
      },
      {
        "id": "100002",
        "success": true
      },
      {
        "id": "100003",
        "success": false,
        "error": "单据状态不允许删除"
      }
    ]
  }
}
```

---

## 五、批量操作API

### 5.1 批量执行操作

**请求**:
```http
POST /api/v1/bill/batch_operate
Content-Type: application/json
Authorization: Bearer {token}

{
  "formId": "kdev_salesorder",
  "operation": "audit",
  "ids": ["100001", "100002", "100003"],
  "params": {
    "auditResult": "pass",
    "auditOpinion": "批量审核通过"
  }
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "total": 3,
    "success": 3,
    "failed": 0,
    "results": [
      {
        "id": "100001",
        "success": true,
        "newStatus": "audited"
      },
      {
        "id": "100002",
        "success": true,
        "newStatus": "audited"
      },
      {
        "id": "100003",
        "success": true,
        "newStatus": "audited"
      }
    ]
  }
}
```

### 5.2 支持的批量操作

| 操作 | 说明 | 前置条件 |
|-----|------|---------|
| submit | 提交 | 单据状态为draft |
| audit | 审核 | 单据状态为submitted |
| reject | 驳回 | 单据状态为submitted |
| void | 作废 | 单据状态为audited |
| reopen | 反审核 | 单据状态为audited |
| close | 关闭 | 单据状态为audited |

---

## 六、任务查询API

### 6.1 查询任务状态

**请求**:
```http
GET /api/v1/task/{taskId}
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "taskId": "TASK_20260321_001",
    "type": "batch_create",
    "status": "running",
    "progress": {
      "total": 1000,
      "completed": 500,
      "success": 498,
      "failed": 2,
      "percentage": 50
    },
    "startTime": "2026-03-21T10:00:00Z",
    "estimatedEndTime": "2026-03-21T10:02:00Z"
  }
}
```

### 6.2 查询任务结果

**请求**:
```http
GET /api/v1/task/{taskId}/results?page=1&pageSize=100
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "taskId": "TASK_20260321_001",
    "results": {
      "total": 1000,
      "page": 1,
      "pageSize": 100,
      "rows": [
        {
          "index": 0,
          "success": true,
          "billId": "100001",
          "billNo": "SO20260321001"
        }
      ]
    }
  }
}
```

### 6.3 取消任务

**请求**:
```http
POST /api/v1/task/{taskId}/cancel
Authorization: Bearer {token}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "taskId": "TASK_20260321_001",
    "status": "cancelled",
    "completed": 500,
    "cancelled": 500
  }
}
```

---

## 七、代码示例

### 7.1 Java SDK

```java
// 批量创建单据
public class BatchOperationDemo {
    
    private K3CloudClient client;
    
    public void batchCreate() {
        // 准备数据
        List<BillData> bills = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
            BillData bill = new BillData();
            bill.setBillNo("SO" + String.format("%04d", i));
            bill.setCustomerId("C001");
            bills.add(bill);
        }
        
        // 批量创建请求
        BatchCreateRequest request = new BatchCreateRequest();
        request.setFormId("kdev_salesorder");
        request.setBills(bills);
        request.setOptions(new BatchOptions()
            .setStopOnError(false)
            .setSkipDuplicate(true));
        
        // 执行批量创建
        BatchResult result = client.batchCreate(request);
        
        // 处理结果
        System.out.println("成功: " + result.getSuccess());
        System.out.println("失败: " + result.getFailed());
        
        for (BatchResult.Item item : result.getResults()) {
            if (!item.isSuccess()) {
                System.out.println("第" + item.getIndex() + "条失败: " + item.getError());
            }
        }
    }
    
    // 异步批量操作
    public void batchCreateAsync() {
        BatchCreateRequest request = new BatchCreateRequest();
        request.setFormId("kdev_salesorder");
        request.setBills(bills);
        
        // 设置回调
        request.setCallback(new Callback()
            .setUrl("https://your-server.com/callback")
            .setMethod("POST"));
        
        // 发起异步任务
        AsyncTask task = client.batchCreateAsync(request);
        System.out.println("任务ID: " + task.getTaskId());
        
        // 轮询任务状态
        while (task.getStatus() != TaskStatus.COMPLETED && 
               task.getStatus() != TaskStatus.FAILED) {
            Thread.sleep(5000);
            task = client.getTask(task.getTaskId());
            System.out.println("进度: " + task.getProgress().getPercentage() + "%");
        }
    }
}
```

### 7.2 JavaScript SDK

```javascript
// 批量操作示例
const batchDemo = {
    // 批量创建
    async batchCreate() {
        const bills = [];
        for (let i = 0; i < 100; i++) {
            bills.push({
                billNo: `SO${String(i).padStart(4, '0')}`,
                customerId: 'C001',
                entries: [
                    { materialId: 'M001', qty: 10, price: 100 }
                ]
            });
        }
        
        const result = await k3cloud.batchCreate({
            formId: 'kdev_salesorder',
            bills: bills,
            options: {
                stopOnError: false,
                skipDuplicate: true
            }
        });
        
        console.log(`成功: ${result.success}, 失败: ${result.failed}`);
        
        // 处理失败记录
        result.results
            .filter(r => !r.success)
            .forEach(r => {
                console.error(`第${r.index}条失败: ${r.error}`);
            });
    },
    
    // 异步批量操作
    async batchCreateAsync() {
        // 发起异步任务
        const task = await k3cloud.batchCreateAsync({
            formId: 'kdev_salesorder',
            bills: largeBillArray,
            callback: {
                url: 'https://your-server.com/callback'
            }
        });
        
        console.log('任务ID:', task.taskId);
        
        // 轮询任务状态
        const pollTask = async () => {
            const status = await k3cloud.getTask(task.taskId);
            
            if (status.status === 'completed' || status.status === 'failed') {
                console.log('任务完成:', status);
                return status;
            }
            
            console.log(`进度: ${status.progress.percentage}%`);
            await new Promise(r => setTimeout(r, 5000));
            return pollTask();
        };
        
        return pollTask();
    }
};
```

---

## 八、最佳实践

### 8.1 性能优化

1. **合理分批**: 单次请求控制在500条以内
2. **并发控制**: 控制并发请求数量
3. **使用异步**: 大数据量使用异步接口
4. **错误重试**: 实现失败重试机制

### 8.2 错误处理

```java
// 错误处理示例
public void handleBatchResult(BatchResult result) {
    // 分类处理结果
    List<BatchResult.Item> successItems = result.getResults().stream()
        .filter(BatchResult.Item::isSuccess)
        .collect(Collectors.toList());
    
    List<BatchResult.Item> failedItems = result.getResults().stream()
        .filter(item -> !item.isSuccess())
        .collect(Collectors.toList());
    
    // 记录失败原因
    failedItems.forEach(item -> {
        log.error("批量操作失败 - 索引:{}, 错误:{}", 
            item.getIndex(), item.getError());
    });
    
    // 重试失败记录
    if (!failedItems.isEmpty()) {
        retryFailedItems(failedItems);
    }
}
```

---

**相关文档**:
- [REST API参考](./01-REST%20API参考.md)
- [文件上传API](./03-文件上传API.md)
