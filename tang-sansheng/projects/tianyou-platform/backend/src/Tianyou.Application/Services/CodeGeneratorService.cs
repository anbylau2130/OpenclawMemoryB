using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;

namespace Tianyou.Application.Services;

/// <summary>
/// 代码生成服务
/// </summary>
public class CodeGeneratorService
{
    private readonly TianyouDbContext _context;
    
    public CodeGeneratorService(TianyouDbContext context)
    {
        _context = context;
    }
    
    public async Task<string> GenerateEntityCodeAsync(Guid entityId)
    {
        var entity = await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == entityId);
            
        if (entity == null) throw new Exception("实体不存在");
        
        var code = $@"using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// {entity.EntityName}
/// </summary>
public class {entity.EntityName}
{{
";
        foreach (var field in entity.Fields)
        {
            code += $@"    [Required{(field.MaxLength.HasValue ? $"(MaxLength = {field.MaxLength})" : "")}]
    public {GetCSharpType(field.FieldType)} {field.FieldName} {{ get; set; }}
";
        }
        
        code += @"}
";
        
        return code;
    }
    
    public async Task<CodeTemplate> CreateTemplateAsync(string templateName, string templateType, 
        string templateContent, string? description = null, string? language = "csharp")
    {
        var template = new CodeTemplate
        {
            Id = Guid.NewGuid(),
            TemplateName = templateName,
            TemplateType = templateType,
            TemplateContent = templateContent,
            Description = description,
            Language = language,
            IsSystem = false,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.CodeTemplates.Add(template);
        await _context.SaveChangesAsync();
        
        return template;
    }
    
    public async Task<List<CodeTemplate>> GetTemplatesAsync(string? templateType = null)
    {
        var query = _context.CodeTemplates.AsQueryable();
        
        if (!string.IsNullOrEmpty(templateType))
        {
            query = query.Where(t => t.TemplateType == templateType);
        }
        
        return await query.OrderBy(t => t.TemplateName).ToListAsync();
    }
    
    private string GetCSharpType(string fieldType)
    {
        return fieldType.ToLower() switch
        {
            "text" or "string" => "string",
            "number" or "int" => "int",
            "decimal" or "money" => "decimal",
            "bool" or "boolean" => "bool",
            "date" or "datetime" => "DateTime",
            "guid" => "Guid",
            _ => "string"
        };
    }
}