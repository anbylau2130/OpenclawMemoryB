using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using Tianyou.Application.Security;

namespace Tianyou.Application.Services;

/// <summary>
/// 代码生成服务
/// </summary>
public class CodeGeneratorService
{
    private readonly TianyouDbContext _context;
    private readonly ILogger<CodeGeneratorService> _logger;

    public CodeGeneratorService(TianyouDbContext context, ILogger<CodeGeneratorService> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    public async Task<string> GenerateEntityCodeAsync(Guid entityId)
    {
        var entity = await _context.EntityDefinitions
            .Include(e => e.Fields)
            .FirstOrDefaultAsync(e => e.Id == entityId);

        if (entity == null)
        {
            _logger.LogWarning("生成代码失败：实体不存在 - EntityId: {EntityId}", entityId);
            throw new Exception("实体不存在");
        }

        // XSS防护：清理实体名称和描述
        var safeEntityName = XssProtector.SanitizeIdentifier(entity.EntityName, "实体名称");
        var safeDescription = XssProtector.SanitizeHtml(entity.Description);

        var code = $@"using System.ComponentModel.DataAnnotations;

namespace Tianyou.Domain.Entities;

/// <summary>
/// {safeEntityName}
/// </summary>
public class {safeEntityName}
{{
";
        foreach (var field in entity.Fields)
        {
            // XSS防护：清理字段名称
            var safeFieldName = XssProtector.SanitizeIdentifier(field.FieldName, "字段名称");
            var safeMaxLength = field.MaxLength.HasValue ? $"(MaxLength = {field.MaxLength})" : "";

            code += $@"    [Required{safeMaxLength}]
    public {GetCSharpType(field.FieldType)} {safeFieldName} {{ get; set; }}
";
        }

        code += @"}
";

        // 验证生成的代码安全性
        CodeGeneratorValidator.ValidateGeneratedCode(code, "生成的实体代码");

        _logger.LogInformation("代码生成成功 - EntityId: {EntityId}, EntityName: {EntityName}", entityId, safeEntityName);

        return code;
    }
    
    public async Task<CodeTemplate> CreateTemplateAsync(string templateName, string templateType, 
        string templateContent, string? description = null, string? language = "csharp")
    {
        // XSS防护：清理所有输入
        var safeTemplateName = XssProtector.SanitizeHtml(templateName);
        var safeDescription = XssProtector.SanitizeHtml(description);

        // 代码生成安全验证
        CodeGeneratorValidator.ValidateTemplateType(templateType, "模板类型");
        CodeGeneratorValidator.ValidateLanguage(language, "语言");
        CodeGeneratorValidator.ValidateTemplateContent(templateContent, "模板内容");

        var safeTemplateType = templateType.ToLower().Trim();
        var safeLanguage = language.ToLower().Trim();

        // 沙箱化模板内容（移除危险操作）
        var safeTemplateContent = CodeGeneratorValidator.SandboxTemplate(templateContent);

        var template = new CodeTemplate
        {
            Id = Guid.NewGuid(),
            TemplateName = safeTemplateName,
            TemplateType = safeTemplateType,
            TemplateContent = safeTemplateContent,
            Description = safeDescription,
            Language = safeLanguage,
            IsSystem = false,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        _context.CodeTemplates.Add(template);
        await _context.SaveChangesAsync();

        _logger.LogInformation("模板创建成功 - TemplateId: {TemplateId}, TemplateName: {TemplateName}", 
            template.Id, template.TemplateName);

        return template;
    }
    
    public async Task<List<CodeTemplate>> GetTemplatesAsync(string? templateType = null)
    {
        var query = _context.CodeTemplates.AsQueryable();

        if (!string.IsNullOrEmpty(templateType))
        {
            // XSS防护：清理模板类型
            var safeTemplateType = XssProtector.SanitizeHtml(templateType);
            query = query.Where(t => t.TemplateType == safeTemplateType);
        }

        var templates = await query.OrderBy(t => t.TemplateName).ToListAsync();

        _logger.LogInformation("查询模板列表 - TemplateType: {TemplateType}, Count: {Count}", 
            templateType ?? "all", templates.Count);

        return templates;
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