using System.Text;
using YunTianYou.Domain.Entities;

namespace YunTianYou.Application.Services;

/// <summary>
/// 代码生成器服务 - 从数据模型生成代码
/// </summary>
public class CodeGeneratorService
{
    private readonly List<DataModel> _dataModels = new();
    private readonly List<GeneratedCode> _generatedCodes = new();
    
    /// <summary>
    /// 创建数据模型
    /// </summary>
    public async Task<DataModel> CreateDataModelAsync(
        string name, string description, string schema, Guid createdByUserId)
    {
        var model = new DataModel
        {
            Id = Guid.NewGuid(),
            Name = name,
            Description = description,
            Schema = schema,
            TableName = ToSnakeCase(name),
            IsPublished = false,
            CreatedByUserId = createdByUserId,
            CreatedAt = DateTime.UtcNow
        };
        
        _dataModels.Add(model);
        return await Task.FromResult(model);
    }
    
    /// <summary>
    /// 生成所有代码
    /// </summary>
    public async Task<List<GeneratedCode>> GenerateAllCodeAsync(Guid dataModelId)
    {
        var model = _dataModels.FirstOrDefault(m => m.Id == dataModelId);
        if (model == null)
        {
            throw new ArgumentException("数据模型不存在");
        }
        
        var codes = new List<GeneratedCode>
        {
            await GenerateEntityAsync(model),
            await GenerateServiceAsync(model),
            await GenerateControllerAsync(model),
            await GenerateReactComponentAsync(model),
            await GenerateSqlAsync(model)
        };
        
        _generatedCodes.AddRange(codes);
        model.IsPublished = true;
        
        return codes;
    }
    
    /// <summary>
    /// 生成实体类代码
    /// </summary>
    private async Task<GeneratedCode> GenerateEntityAsync(DataModel model)
    {
        var sb = new StringBuilder();
        sb.AppendLine("using System.ComponentModel.DataAnnotations;");
        sb.AppendLine("using System.ComponentModel.DataAnnotations.Schema;");
        sb.AppendLine();
        sb.AppendLine($"namespace YunTianYou.Domain.Entities;");
        sb.AppendLine();
        sb.AppendLine($"/// <summary>");
        sb.AppendLine($"/// {model.Description ?? model.Name}实体");
        sb.AppendLine($"/// </summary>");
        sb.AppendLine($"[Table(\"{model.TableName}\")]");
        sb.AppendLine($"public class {model.Name} : BaseEntity");
        sb.AppendLine("{");
        sb.AppendLine("    // TODO: 根据Schema生成字段");
        sb.AppendLine("    public string Name { get; set; } = string.Empty;");
        sb.AppendLine("}");
        
        return new GeneratedCode
        {
            Id = Guid.NewGuid(),
            DataModelId = model.Id,
            CodeType = "entity",
            FileName = $"{model.Name}.cs",
            Content = sb.ToString(),
            Language = "csharp",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    /// <summary>
    /// 生成服务类代码
    /// </summary>
    private async Task<GeneratedCode> GenerateServiceAsync(DataModel model)
    {
        var sb = new StringBuilder();
        sb.AppendLine("using YunTianYou.Domain.Entities;");
        sb.AppendLine();
        sb.AppendLine($"namespace YunTianYou.Application.Services;");
        sb.AppendLine();
        sb.AppendLine($"/// <summary>");
        sb.AppendLine($"/// {model.Name}服务");
        sb.AppendLine($"/// </summary>");
        sb.AppendLine($"public class {model.Name}Service");
        sb.AppendLine("{");
        sb.AppendLine("    private readonly List<" + model.Name + "> _items = new();");
        sb.AppendLine();
        sb.AppendLine($"    public async Task<{model.Name}> CreateAsync({model.Name} item)");
        sb.AppendLine("    {");
        sb.AppendLine("        item.Id = Guid.NewGuid();");
        sb.AppendLine("        item.CreatedAt = DateTime.UtcNow;");
        sb.AppendLine("        _items.Add(item);");
        sb.AppendLine("        return await Task.FromResult(item);");
        sb.AppendLine("    }");
        sb.AppendLine();
        sb.AppendLine($"    public async Task<List<{model.Name}>> GetAllAsync()");
        sb.AppendLine("    {");
        sb.AppendLine("        return await Task.FromResult(_items.ToList());");
        sb.AppendLine("    }");
        sb.AppendLine();
        sb.AppendLine($"    public async Task<{model.Name}?> GetByIdAsync(Guid id)");
        sb.AppendLine("    {");
        sb.AppendLine("        return await Task.FromResult(_items.FirstOrDefault(i => i.Id == id));");
        sb.AppendLine("    }");
        sb.AppendLine("}");
        
        return new GeneratedCode
        {
            Id = Guid.NewGuid(),
            DataModelId = model.Id,
            CodeType = "service",
            FileName = $"{model.Name}Service.cs",
            Content = sb.ToString(),
            Language = "csharp",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    /// <summary>
    /// 生成控制器代码
    /// </summary>
    private async Task<GeneratedCode> GenerateControllerAsync(DataModel model)
    {
        var sb = new StringBuilder();
        sb.AppendLine("using Microsoft.AspNetCore.Mvc;");
        sb.AppendLine($"using YunTianYou.Application.Services;");
        sb.AppendLine($"using YunTianYou.Domain.Entities;");
        sb.AppendLine();
        sb.AppendLine($"namespace YunTianYou.Api.Controllers;");
        sb.AppendLine();
        sb.AppendLine($"[ApiController]");
        sb.AppendLine($"[Route(\"api/[controller]\")]");
        sb.AppendLine($"public class {model.Name}sController : ControllerBase");
        sb.AppendLine("{");
        sb.AppendLine($"    private readonly {model.Name}Service _service;");
        sb.AppendLine();
        sb.AppendLine($"    public {model.Name}sController({model.Name}Service service)");
        sb.AppendLine("    {");
        sb.AppendLine("        _service = service;");
        sb.AppendLine("    }");
        sb.AppendLine();
        sb.AppendLine("    [HttpGet]");
        sb.AppendLine($"    public async Task<ActionResult<List<{model.Name}>>> GetAll()");
        sb.AppendLine("    {");
        sb.AppendLine("        var items = await _service.GetAllAsync();");
        sb.AppendLine("        return Ok(items);");
        sb.AppendLine("    }");
        sb.AppendLine();
        sb.AppendLine("    [HttpGet(\"{id}\")]");
        sb.AppendLine($"    public async Task<ActionResult<{model.Name}>> GetById(Guid id)");
        sb.AppendLine("    {");
        sb.AppendLine("        var item = await _service.GetByIdAsync(id);");
        sb.AppendLine("        if (item == null) return NotFound();");
        sb.AppendLine("        return Ok(item);");
        sb.AppendLine("    }");
        sb.AppendLine();
        sb.AppendLine("    [HttpPost]");
        sb.AppendLine($"    public async Task<ActionResult<{model.Name}>> Create({model.Name} item)");
        sb.AppendLine("    {");
        sb.AppendLine("        var created = await _service.CreateAsync(item);");
        sb.AppendLine($"        return CreatedAtAction(nameof(GetById), new {{ id = created.Id }}, created);");
        sb.AppendLine("    }");
        sb.AppendLine("}");
        
        return new GeneratedCode
        {
            Id = Guid.NewGuid(),
            DataModelId = model.Id,
            CodeType = "controller",
            FileName = $"{model.Name}sController.cs",
            Content = sb.ToString(),
            Language = "csharp",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    /// <summary>
    /// 生成React组件代码
    /// </summary>
    private async Task<GeneratedCode> GenerateReactComponentAsync(DataModel model)
    {
        var sb = new StringBuilder();
        sb.AppendLine("import React, { useState, useEffect } from 'react';");
        sb.AppendLine("import { Table, Button, Modal, Form, Input } from 'antd';");
        sb.AppendLine("import axios from 'axios';");
        sb.AppendLine();
        sb.AppendLine($"const {model.Name}Management: React.FC = () => {{");
        sb.AppendLine("  const [data, setData] = useState([]);");
        sb.AppendLine("  const [loading, setLoading] = useState(false);");
        sb.AppendLine("  const [modalVisible, setModalVisible] = useState(false);");
        sb.AppendLine();
        sb.AppendLine("  useEffect(() => {");
        sb.AppendLine("    fetchData();");
        sb.AppendLine("  }, []);");
        sb.AppendLine();
        sb.AppendLine("  const fetchData = async () => {");
        sb.AppendLine("    setLoading(true);");
        sb.AppendLine($"    const response = await axios.get('/api/{model.Name.ToLower()}s');");
        sb.AppendLine("    setData(response.data);");
        sb.AppendLine("    setLoading(false);");
        sb.AppendLine("  };");
        sb.AppendLine();
        sb.AppendLine("  const columns = [");
        sb.AppendLine("    { title: 'ID', dataIndex: 'id', key: 'id' },");
        sb.AppendLine("    { title: '名称', dataIndex: 'name', key: 'name' },");
        sb.AppendLine("    { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt' },");
        sb.AppendLine("  ];");
        sb.AppendLine();
        sb.AppendLine("  return (");
        sb.AppendLine("    <div>");
        sb.AppendLine($"      <h1>{model.Name}管理</h1>");
        sb.AppendLine("      <Button type=\"primary\" onClick={() => setModalVisible(true)}>");
        sb.AppendLine("        新建");
        sb.AppendLine("      </Button>");
        sb.AppendLine("      <Table columns={columns} dataSource={data} loading={loading} />");
        sb.AppendLine("    </div>");
        sb.AppendLine("  );");
        sb.AppendLine("};");
        sb.AppendLine();
        sb.AppendLine($"export default {model.Name}Management;");
        
        return new GeneratedCode
        {
            Id = Guid.NewGuid(),
            DataModelId = model.Id,
            CodeType = "react",
            FileName = $"{model.Name}Management.tsx",
            Content = sb.ToString(),
            Language = "typescript",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    /// <summary>
    /// 生成SQL建表语句
    /// </summary>
    private async Task<GeneratedCode> GenerateSqlAsync(DataModel model)
    {
        var sb = new StringBuilder();
        sb.AppendLine($"-- {model.Description ?? model.Name}表");
        sb.AppendLine($"CREATE TABLE {model.TableName} (");
        sb.AppendLine("    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),");
        sb.AppendLine("    name VARCHAR(100) NOT NULL,");
        sb.AppendLine("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,");
        sb.AppendLine("    updated_at TIMESTAMP,");
        sb.AppendLine(");");
        sb.AppendLine();
        sb.AppendLine($"-- 索引");
        sb.AppendLine($"CREATE INDEX idx_{model.TableName}_name ON {model.TableName}(name);");
        sb.AppendLine($"CREATE INDEX idx_{model.TableName}_created ON {model.TableName}(created_at);");
        
        return new GeneratedCode
        {
            Id = Guid.NewGuid(),
            DataModelId = model.Id,
            CodeType = "sql",
            FileName = $"{model.TableName}.sql",
            Content = sb.ToString(),
            Language = "sql",
            CreatedAt = DateTime.UtcNow
        };
    }
    
    /// <summary>
    /// 转换为蛇形命名
    /// </summary>
    private string ToSnakeCase(string str)
    {
        return string.Concat(
            str.Select((x, i) => i > 0 && char.IsUpper(x) ? "_" + x.ToString() : x.ToString())
        ).ToLower();
    }
    
    /// <summary>
    /// 获取数据模型列表
    /// </summary>
    public async Task<List<DataModel>> GetDataModelsAsync()
    {
        return await Task.FromResult(_dataModels.ToList());
    }
    
    /// <summary>
    /// 获取生成的代码
    /// </summary>
    public async Task<List<GeneratedCode>> GetGeneratedCodesAsync(Guid dataModelId)
    {
        return await Task.FromResult(
            _generatedCodes.Where(c => c.DataModelId == dataModelId).ToList());
    }
}
