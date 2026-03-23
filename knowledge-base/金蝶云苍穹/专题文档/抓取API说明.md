# 金蝶云社区文档抓取API

> 发现时间: 2026-03-22
> 状态: ✅ 已验证可用

---

## 一、API接口列表

### 1.1 专题分类和文档列表

```
GET https://vip.kingdee.com/knowledgeapi/knowledge/special/{specialId}/path
```

**返回格式**:
```json
[
  {
    "id": 70765,
    "name": "初识开发平台",
    "itemList": [
      {
        "entityId": "355302802538757376",
        "entityType": "Knowledge",
        "name": "概述"
      }
    ]
  }
]
```

### 1.2 全部分类树

```
GET https://vip.kingdee.com/knowledgeapi/v2/classifies-tree?productLineId=29
```

### 1.3 文档详情（推测）

```
GET https://vip.kingdee.com/knowledgeapi/knowledge/detail/{entityId}
GET https://vip.kingdee.com/knowledgeapi/knowledge/entity/{entityId}
```

---

## 二、不截图获取内容的方法

| 方法 | API/工具 | 效率 | 推荐 |
|-----|----------|------|------|
| **API调用** | `fetch('/knowledgeapi/...')` | ⭐⭐⭐⭐⭐ | 🔥 最佳 |
| **snapshot** | `browser action=snapshot` | ⭐⭐⭐⭐ | ✅ 推荐 |
| **evaluate** | `browser action=act kind=evaluate` | ⭐⭐⭐ | ✅ 可用 |

---

## 三、使用示例

### 3.1 获取专题文档列表

```javascript
const specialId = '218022218066869248';
const response = await fetch(
  `https://vip.kingdee.com/knowledgeapi/knowledge/special/${specialId}/path`
);
const data = await response.json();

// 提取所有文档
const docs = [];
data.forEach(category => {
  category.itemList.forEach(item => {
    docs.push({
      id: item.entityId,
      title: item.name,
      categoryName: category.name
    });
  });
});

console.log(`共${docs.length}篇文档`);
```

### 3.2 使用browser工具提取

```javascript
browser action=act kind=evaluate fn=`
async () => {
  const response = await fetch(
    'https://vip.kingdee.com/knowledgeapi/knowledge/special/218022218066869248/path'
  );
  return await response.json();
}
`
```

---

## 四、已发现的专题ID

| 专题名称 | 专题ID | 文档数 |
|---------|--------|--------|
| 开发平台 | 218022218066869248 | 601 |
| 开发平台（专业版） | 248759291325464320 | - |
| 定制开发平台 | 773127159950388736 | - |

---

## 五、下一步

需要找到获取**文档正文内容**的API接口。

可能的API：
- `/knowledgeapi/knowledge/detail/{id}`
- `/knowledgeapi/knowledge/entity/{id}`
- `/knowledgeapi/v2/knowledge/{id}`

---

**维护者**: 礼部
**最后更新**: 2026-03-22
