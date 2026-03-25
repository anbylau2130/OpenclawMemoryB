using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;
using Tianyou.Infrastructure.Data;
using System.Text.Json;

namespace Tianyou.Application.Services;

/// <summary>
/// 表单管理服务
/// </summary>
public class FormService
{
    private readonly TianyouDbContext _context;
    
    public FormService(TianyouDbContext context)
    {
        _context = context;
    }
    
    /// <summary>
    /// 创建表单定义
    /// </summary>
    public async Task<FormDefinition> CreateFormAsync(string formName, string? description = null, Guid? entityDefinitionId = null)
    {
        if (await _context.FormDefinitions.AnyAsync(f => f.FormName == formName))
        {
            throw new Exception($"表单名称 '{formName}' 已存在");
        }
        
        var form = new FormDefinition
        {
            Id = Guid.NewGuid(),
            FormName = formName,
            Description = description,
            EntityDefinitionId = entityDefinitionId,
            IsPublished = false,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };
        
        _context.FormDefinitions.Add(form);
        await _context.SaveChangesAsync();
        
        return form;
    }
    
    /// <summary>
    /// 添加表单字段
    /// </summary>
    public async Task<FormField> AddFormFieldAsync(Guid formId, string fieldName, string fieldType, 
        string? label = null, string? placeholder = null, string? defaultValue = null,
        bool isRequired = false, bool isVisible = true, bool isEditable = true,
        string? validationRules = null, string? fieldConfig = null)
    {
        var form = await _context.FormDefinitions.FindAsync(formId);
        if (form == null)
        {
            throw new Exception("表单不存在");
        }
        
        var field = new FormField
        {
            Id = Guid.NewGuid(),
            FormDefinitionId = formId,
            FieldName = fieldName,
            FieldType = fieldType,
            Label = label ?? fieldName,
            Placeholder = placeholder,
            DefaultValue = defaultValue,
            IsRequired = isRequired,
            IsVisible = isVisible,
            IsEditable = isEditable,
            DisplayOrder = await _context.FormFields.CountAsync(f => f.FormDefinitionId == formId),
            ValidationRules = validationRules,
            FieldConfig = fieldConfig,
            CreatedAt = DateTime.UtcNow
        };
        
        _context.FormFields.Add(field);
        await _context.SaveChangesAsync();
        
        return field;
    }
    
    /// <summary>
    /// 发布表单
    /// </summary>
    public async Task<FormDefinition> PublishFormAsync(Guid formId)
    {
        var form = await _context.FormDefinitions
            .Include(f => f.Fields)
            .FirstOrDefaultAsync(f => f.Id == formId);
            
        if (form == null)
        {
            throw new Exception("表单不存在");
        }
        
        if (!form.Fields.Any())
        {
            throw new Exception("表单至少需要一个字段");
        }
        
        form.IsPublished = true;
        form.UpdatedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return form;
    }
    
    /// <summary>
    /// 获取表单列表
    /// </summary>
    public async Task<List<FormDefinition>> GetFormsAsync()
    {
        return await _context.FormDefinitions
            .Include(f => f.Fields)
            .OrderByDescending(f => f.CreatedAt)
            .ToListAsync();
    }
    
    /// <summary>
    /// 获取表单详情
    /// </summary>
    public async Task<FormDefinition?> GetFormAsync(Guid formId)
    {
        return await _context.FormDefinitions
            .Include(f => f.Fields.OrderBy(field => field.DisplayOrder))
            .FirstOrDefaultAsync(f => f.Id == formId);
    }
}