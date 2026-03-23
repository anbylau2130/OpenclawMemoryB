---
name: codegen-lsp
description: 从JSON规范自动生成多语言类型代码（Python/Dotnet/SQLServer）。支持JSON Schema、OpenAPI、自定义规范。关键词：代码生成、LSP、类型定义、多语言、自动化。
---

# Codegen-LSP - 多语言类型代码生成器

基于 Microsoft lsprotocol 方法论，从 JSON 规范自动生成 Python、Dotnet（C#）和 SQL Server 代码。

## 核心理念

**单一数据源 → 多语言代码**

```
JSON 规范 → 代码生成器 → Python/Dotnet/SQL代码
  (1个)        (1个)        (N个语言)
```

---

## 支持的语言

| 语言 | 输出 | 用途 |
|------|------|------|
| **Python** | dataclass/pydantic | API 客户端、数据模型 |
| **Dotnet (C#)** | class/record | .NET 项目、ASP.NET |
| **SQL Server** | 表/存储过程 | 数据库架构 |

---

## 快速开始

### 1. 创建规范文件

**schema.json：**
```json
{
  "namespace": "MyApp.Models",
  "types": [
    {
      "name": "User",
      "description": "用户实体",
      "properties": [
        {"name": "id", "type": "integer", "description": "用户ID"},
        {"name": "username", "type": "string", "description": "用户名"},
        {"name": "email", "type": "string", "description": "邮箱"},
        {"name": "created_at", "type": "datetime", "description": "创建时间"}
      ]
    },
    {
      "name": "Order",
      "description": "订单实体",
      "properties": [
        {"name": "id", "type": "integer"},
        {"name": "user_id", "type": "integer", "foreign_key": "User.id"},
        {"name": "total", "type": "decimal"},
        {"name": "status", "type": "string", "enum": ["pending", "paid", "shipped"]}
      ]
    }
  ]
}
```

### 2. 生成代码

```bash
# 生成 Python 代码
python scripts/generate.py --input schema.json --language python --output ./models/python

# 生成 Dotnet 代码
python scripts/generate.py --input schema.json --language dotnet --output ./models/dotnet

# 生成 SQL Server 代码
python scripts/generate.py --input schema.json --language sqlserver --output ./models/sql

# 生成所有语言
python scripts/generate.py --input schema.json --all --output ./models
```

---

## 生成的代码示例

### Python（dataclass）

```python
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Enum, Optional

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"

@dataclass
class User:
    """用户实体"""
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None

@dataclass
class Order:
    """订单实体"""
    id: int
    user_id: int
    total: Decimal
    status: OrderStatus
```

### Dotnet (C#)

```csharp
using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace MyApp.Models
{
    /// <summary>
    /// 用户实体
    /// </summary>
    public class User
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        [Required]
        [StringLength(100)]
        public string Username { get; set; }

        [Required]
        [EmailAddress]
        [StringLength(255)]
        public string Email { get; set; }

        public DateTime? CreatedAt { get; set; }
    }

    /// <summary>
    /// 订单实体
    /// </summary>
    public class Order
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        [Required]
        [ForeignKey("User")]
        public int UserId { get; set; }

        [Column(TypeName = "decimal(18,2)")]
        public decimal Total { get; set; }

        [Required]
        [StringLength(20)]
        public string Status { get; set; }

        public virtual User User { get; set; }
    }
}
```

### SQL Server

```sql
-- 用户表
CREATE TABLE Users (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Username NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT CK_Users_Email CHECK (Email LIKE '%@%.%')
);

-- 订单表
CREATE TABLE Orders (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Total DECIMAL(18,2) NOT NULL,
    Status NVARCHAR(20) NOT NULL,
    CreatedAt DATETIME2 NULL DEFAULT GETUTCDATE(),
    CONSTRAINT FK_Orders_Users FOREIGN KEY (UserId) REFERENCES Users(Id),
    CONSTRAINT CK_Orders_Status CHECK (Status IN ('pending', 'paid', 'shipped'))
);

-- 创建索引
CREATE INDEX IX_Orders_UserId ON Orders(UserId);
CREATE INDEX IX_Orders_Status ON Orders(Status);

-- 存储过程：创建用户
CREATE PROCEDURE sp_CreateUser
    @Username NVARCHAR(100),
    @Email NVARCHAR(255)
AS
BEGIN
    INSERT INTO Users (Username, Email, CreatedAt)
    VALUES (@Username, @Email, GETUTCDATE());
    
    SELECT SCOPE_IDENTITY() AS Id;
END
```

---

## 规范文件格式

### 完整示例

```json
{
  "namespace": "MyApp.Models",
  "database": "MyAppDb",
  "types": [
    {
      "name": "TypeName",
      "description": "类型描述",
      "table_name": "table_name",
      "properties": [
        {
          "name": "property_name",
          "type": "integer|string|decimal|datetime|boolean|guid|binary",
          "description": "属性描述",
          "required": true,
          "primary_key": false,
          "foreign_key": "OtherTable.id",
          "enum": ["value1", "value2"],
          "default": "default_value",
          "max_length": 100,
          "precision": 18,
          "scale": 2
        }
      ],
      "indexes": [
        {"columns": ["column1", "column2"], "unique": false}
      ]
    }
  ]
}
```

### 支持的类型映射

| 规范类型 | Python | Dotnet | SQL Server |
|---------|--------|--------|-----------|
| `integer` | int | int | INT |
| `string` | str | string | NVARCHAR |
| `decimal` | Decimal | decimal | DECIMAL |
| `datetime` | datetime | DateTime | DATETIME2 |
| `boolean` | bool | bool | BIT |
| `guid` | UUID | Guid | UNIQUEIDENTIFIER |
| `binary` | bytes | byte[] | VARBINARY |

---

## 使用方法

### 命令行参数

```bash
python scripts/generate.py [OPTIONS]

Options:
  --input, -i      输入规范文件路径（JSON）
  --language, -l   目标语言（python|dotnet|sqlserver|all）
  --output, -o     输出目录
  --namespace, -n  命名空间（覆盖规范中的设置）
  --dry-run        只预览，不写入文件
  --verbose        显示详细输出
```

### 示例

```bash
# 基础用法
python scripts/generate.py --input schema.json --language python --output ./models

# 生成所有语言
python scripts/generate.py --input schema.json --all --output ./generated

# 自定义命名空间
python scripts/generate.py -i schema.json -l dotnet -o ./models -n MyCompany.Models

# 预览生成内容
python scripts/generate.py -i schema.json -l python --dry-run
```

---

## 高级功能

### 1. 自定义模板

```bash
# 使用自定义模板
python scripts/generate.py -i schema.json -l python --template ./my_templates/python
```

**模板结构：**
```
my_templates/
├── python/
│   ├── class.jinja2
│   ├── enum.jinja2
│   └── init.jinja2
├── dotnet/
│   ├── class.jinja2
│   └── enum.jinja2
└── sqlserver/
    ├── table.jinja2
    └── procedure.jinja2
```

### 2. 部分生成

```bash
# 只生成指定的类型
python scripts/generate.py -i schema.json -l python --types User,Order

# 排除某些类型
python scripts/generate.py -i schema.json -l dotnet --exclude AuditLog
```

### 3. 验证规范

```bash
# 验证规范文件格式
python scripts/validate.py --input schema.json
```

---

## 项目结构

```
codegen-lsp/
├── SKILL.md                      # 本文档
├── README.md                     # 快速开始
├── scripts/
│   ├── generate.py              # 主生成器
│   ├── validate.py              # 规范验证
│   └── utils.py                 # 工具函数
├── templates/
│   ├── python/
│   │   ├── class.jinja2         # Python 类模板
│   │   ├── enum.jinja2          # 枚举模板
│   │   └── init.jinja2          # __init__.py 模板
│   ├── dotnet/
│   │   ├── class.jinja2         # C# 类模板
│   │   ├── enum.jinja2          # 枚举模板
│   │   └── namespace.jinja2     # 命名空间模板
│   └── sqlserver/
│       ├── table.jinja2         # 表模板
│       ├── index.jinja2         # 索引模板
│       └── procedure.jinja2     # 存储过程模板
├── examples/
│   ├── simple.json              # 简单示例
│   ├── ecommerce.json           # 电商示例
│   └── blog.json                # 博客示例
└── tests/
    ├── test_generator.py        # 生成器测试
    └── test_templates.py        # 模板测试
```

---

## 工作流程

### 标准流程

```
1. 定义规范
   ↓
2. 验证规范
   ↓
3. 生成代码
   ↓
4. 审查输出
   ↓
5. 集成到项目
```

### 与 Ralph Loop 集成

```markdown
# PRD 任务示例

## Task: 创建用户管理 API

1. 使用 codegen-lsp 生成数据模型
2. 实现 API 端点
3. 编写单元测试
4. 集成到项目

验收标准：
- 生成的代码通过类型检查
- API 端点正常工作
- 测试覆盖率 > 80%
```

---

## 设计模式

### 1. 插件架构

```python
class GeneratorPlugin(ABC):
    @abstractmethod
    def generate(self, model: dict) -> str:
        pass

class PythonPlugin(GeneratorPlugin):
    def generate(self, model):
        # Python 特定逻辑
        pass

class DotnetPlugin(GeneratorPlugin):
    def generate(self, model):
        # Dotnet 特定逻辑
        pass
```

### 2. 模板方法模式

```python
def generate_code(spec_file, language):
    # 1. 加载规范
    model = load_spec(spec_file)
    
    # 2. 验证规范
    validate_spec(model)
    
    # 3. 选择插件
    plugin = get_plugin(language)
    
    # 4. 生成代码
    code = plugin.generate(model)
    
    # 5. 写入文件
    write_output(code, output_dir)
```

---

## 最佳实践

### 1. 规范设计

✅ **推荐：**
```json
{
  "name": "User",
  "properties": [
    {"name": "id", "type": "integer", "primary_key": true},
    {"name": "email", "type": "string", "max_length": 255}
  ]
}
```

❌ **避免：**
```json
{
  "name": "user",
  "fields": [
    {"n": "id", "t": "int"},
    {"n": "email", "t": "str"}
  ]
}
```

### 2. 命名约定

| 规范 | Python | Dotnet | SQL |
|------|--------|--------|-----|
| `UserName` | `user_name` | `UserName` | `UserName` |
| `UserID` | `user_id` | `UserId` | `UserId` |

### 3. 类型选择

| 场景 | 推荐类型 |
|------|---------|
| 主键 | `integer` (自增) 或 `guid` |
| 金额 | `decimal` (precision=18, scale=2) |
| 时间戳 | `datetime` |
| 大文本 | `string` (max_length=MAX) |

---

## 常见问题

### Q: 如何生成外键关系？

```json
{
  "name": "Order",
  "properties": [
    {"name": "user_id", "type": "integer", "foreign_key": "User.id"}
  ]
}
```

### Q: 如何生成枚举？

```json
{
  "name": "status",
  "type": "string",
  "enum": ["pending", "active", "completed"]
}
```

### Q: 如何自定义表名？

```json
{
  "name": "User",
  "table_name": "app_users"
}
```

---

## 参考资料

- **lsprotocol GitHub：** https://github.com/microsoft/lsprotocol
- **LSP 规范：** https://microsoft.github.io/language-server-protocol/
- **Jinja2 文档：** https://jinja.palletsprojects.com/

---

_基于 Microsoft lsprotocol 方法论，适配 OpenClaw 框架_
