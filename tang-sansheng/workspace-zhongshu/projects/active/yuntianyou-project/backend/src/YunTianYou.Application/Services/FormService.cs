using YunTianYou.Application.DTOs;

namespace YunTianYou.Application.Services;

/// <summary>
/// 表单服务接口 - 低代码核心功能
/// </summary>
public interface IFormService
{
    Task<IEnumerable<FormDto>> GetAllFormsAsync();
    Task<FormDto?> GetFormByIdAsync(Guid id);
    Task<FormDto> CreateFormAsync(CreateFormDto dto);
    Task<FormDto?> UpdateFormAsync(Guid id, UpdateFormDto dto);
    Task<bool> DeleteFormAsync(Guid id);
    Task<bool> PublishFormAsync(Guid id);
    Task<IEnumerable<FieldDefinitionDto>> GetFormFieldsAsync(Guid formId);
}

/// <summary>
/// 表单服务实现
/// </summary>
public class FormService : IFormService
{
    private readonly YunTianYouDbContext _context;
    private readonly ILogger<FormService> _logger;
    
    public FormService(YunTianYouDbContext context, ILogger<FormService> logger)
    {
        _context = context;
        _logger = logger;
    }
    
    public async Task<IEnumerable<FormDto>> GetAllFormsAsync()
    {
        var forms = await _context.Forms
            .Include(f => f.CreatedByUser)
            .OrderByDescending(f => f.CreatedAt)
            .ToListAsync();
            
        return forms.Select(f => new FormDto
        {
            Id = f.Id,
            Name = f.Name,
            Description = f.Description,
            Schema = f.Schema,
            Fields = f.Fields,
            IsPublished = f.IsPublished,
            Version = f.Version,
            CreatedAt = f.CreatedAt,
            CreatedByUserName = f.CreatedByUser.Username
        });
    }
    
    public async Task<FormDto?> GetFormByIdAsync(Guid id)
    {
        var form = await _context.Forms
            .Include(f => f.CreatedByUser)
            .FirstOrDefaultAsync(f => f.Id == id);
            
        if (form == null) return null;
        
        return new FormDto
        {
            Id = form.Id,
            Name = form.Name,
            Description = form.Description,
            Schema = form.Schema,
            Fields = form.Fields,
            IsPublished = form.IsPublished,
            Version = form.Version,
            CreatedAt = form.CreatedAt,
            CreatedByUserName = form.CreatedByUser.Username
        };
    }
    
    public async Task<FormDto> CreateFormAsync(CreateFormDto dto)
    {
        // TODO: 从JWT token获取当前用户ID
        var currentUserId = Guid.Parse("00000000-0000-0000-0000-000000000001");
        
        var form = new Form
        {
            Name = dto.Name,
            Description = dto.Description,
            Schema = dto.Schema ?? "{}",
            Fields = dto.Fields ?? "[]",
            CreatedByUserId = currentUserId,
            IsPublished = false,
            Version = 1
        };
        
        _context.Forms.Add(form);
        await _context.SaveChangesAsync();
        
        return await GetFormByIdAsync(form.Id) ?? throw new Exception("创建表单失败");
    }
    
    public async Task<FormDto?> UpdateFormAsync(Guid id, UpdateFormDto dto)
    {
        var form = await _context.Forms.FindAsync(id);
        if (form == null) return null;
        
        if (!string.IsNullOrEmpty(dto.Name))
            form.Name = dto.Name;
            
        if (dto.Description != null)
            form.Description = dto.Description;
            
        if (dto.Schema != null)
            form.Schema = dto.Schema;
            
        if (dto.Fields != null)
            form.Fields = dto.Fields;
            
        form.Version++;
        form.UpdatedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return await GetFormByIdAsync(id);
    }
    
    public async Task<bool> DeleteFormAsync(Guid id)
    {
        var form = await _context.Forms.FindAsync(id);
        if (form == null) return false;
        
        _context.Forms.Remove(form);
        await _context.SaveChangesAsync();
        
        return true;
    }
    
    public async Task<bool> PublishFormAsync(Guid id)
    {
        var form = await _context.Forms.FindAsync(id);
        if (form == null) return false;
        
        form.IsPublished = true;
        form.UpdatedAt = DateTime.UtcNow;
        
        await _context.SaveChangesAsync();
        
        return true;
    }
    
    public async Task<IEnumerable<FieldDefinitionDto>> GetFormFieldsAsync(Guid formId)
    {
        var form = await _context.Forms.FindAsync(formId);
        if (form == null) return Enumerable.Empty<FieldDefinitionDto>();
        
        // 解析JSON字段定义
        try
        {
            var fields = JsonSerializer.Deserialize<List<FieldDefinitionDto>>(form.Fields);
            return fields ?? Enumerable.Empty<FieldDefinitionDto>();
        }
        catch
        {
            _logger.LogError("解析表单字段失败: {FormId}", formId);
            return Enumerable.Empty<FieldDefinitionDto>();
        }
    }
}
