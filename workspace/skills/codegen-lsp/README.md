# Codegen-LSP - 多语言类型代码生成器

基于 LSP (Language Server Protocol) 规范驱动的代码生成器，支持 Python、Dotnet (C#) 和 SQL Server。

---

## 🚀 快速开始

### 安装依赖

```bash
pip install jinja2
```

### 基础使用

```bash
# 生成所有语言
python scripts/generate.py --input examples/ecommerce.json --output ./generated

# 只生成 Python
python scripts/generate.py -i examples/ecommerce.json -l python -o ./models

# 预览生成内容（不写入文件）
python scripts/generate.py -i examples/ecommerce.json -l python --dry-run
```

---

## 📝 规范文件格式

```json
{
  "namespace": "MyApp.Models",
  "database": "MyAppDb",
  "types": [
    {
      "name": "User",
      "description": "用户实体",
      "table_name": "users",
      "properties": [
        {
          "name": "Id",
          "type": "integer",
          "primary_key": true,
          "identity": true
        },
        {
          "name": "Username",
          "type": "string",
          "required": true,
          "max_length": 100
        },
        {
          "name": "Email",
          "type": "string",
          "required": true,
          "max_length": 255
        }
      ]
    }
  ]
}
```

---

## 🎯 支持的语言

| 语言 | 输出文件 | 特性 |
|------|---------|------|
| **Python** | dataclass, __init__.py | 类型提示, dataclass 装饰器 |
| **Dotnet (C#)** | Entity Framework 类 | Data Annotations, EF Core |
| **SQL Server** | CREATE TABLE, 存储过程 | 索引, 外键, 约束 |

---

## 📦 命令行参数

```bash
python scripts/generate.py [OPTIONS]

Options:
  --input, -i      输入规范文件路径（JSON）[必需]
  --language, -l   目标语言（python|dotnet|sqlserver|all）[默认: all]
  --output, -o     输出目录 [必需]
  --namespace, -n  命名空间（覆盖规范）
  --dry-run        只预览，不写入文件
  --verbose, -v    显示详细输出
```

---

## 💡 示例

### 1. 生成 Python 模型

```bash
python scripts/generate.py \
  --input examples/ecommerce.json \
  --language python \
  --output ./models \
  --namespace MyApp.Models
```

**输出：**
```
models/
└── python/
    ├── __init__.py
    ├── user.py
    └── order.py
```

### 2. 生成 Dotnet 模型

```bash
python scripts/generate.py \
  --input examples/ecommerce.json \
  --language dotnet \
  --output ./Models
```

**输出：**
```
Models/
└── dotnet/
    ├── User.cs
    └── Order.cs
```

### 3. 生成 SQL Server 脚本

```bash
python scripts/generate.py \
  --input examples/ecommerce.json \
  --language sqlserver \
  --output ./sql
```

**输出：**
```
sql/
└── sqlserver/
    ├── tables.sql
    └── procedures.sql
```

---

## 🎨 支持的类型

| 类型 | Python | Dotnet | SQL Server |
|------|--------|--------|-----------|
| `integer` | int | int | INT |
| `string` | str | string | NVARCHAR |
| `decimal` | Decimal | decimal | DECIMAL |
| `datetime` | datetime | DateTime | DATETIME2 |
| `boolean` | bool | bool | BIT |
| `guid` | UUID | Guid | UNIQUEIDENTIFIER |
| `binary` | bytes | byte[] | VARBINARY |

---

## 📚 高级功能

### 1. 枚举支持

```json
{
  "name": "Status",
  "type": "string",
  "enum": ["pending", "active", "completed"]
}
```

### 2. 外键关系

```json
{
  "name": "UserId",
  "type": "integer",
  "foreign_key": "User.Id"
}
```

### 3. 自定义表名

```json
{
  "name": "User",
  "table_name": "app_users"
}
```

### 4. 索引定义

```json
{
  "indexes": [
    {"columns": ["Email"], "unique": true},
    {"columns": ["UserId", "CreatedAt"], "unique": false}
  ]
}
```

---

## 🔧 自定义模板

可以使用自定义模板覆盖默认模板：

```bash
python scripts/generate.py \
  --input schema.json \
  --language python \
  --output ./models \
  --template ./my_templates
```

---

## 🎓 与 Ralph Loop 集成

```markdown
# PRD 任务

## Task: 创建用户管理 API

1. 使用 codegen-lsp 生成数据模型
2. 实现 API 端点
3. 编写单元测试

验收标准：
- 生成的代码通过类型检查
- API 端点正常工作
```

---

## 📖 参考资料

- **SKILL.md:** 完整文档
- **examples/:** 示例规范文件
- **templates/:** 模板文件

---

_基于 Microsoft lsprotocol 方法论_
