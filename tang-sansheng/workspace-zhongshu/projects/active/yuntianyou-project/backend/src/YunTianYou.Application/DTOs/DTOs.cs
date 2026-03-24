namespace YunTianYou.Application.DTOs;

/// <summary>
/// 表单DTO
/// </summary>
public class FormDto
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Schema { get; set; } = "{}";
    public string Fields { get; set; } = "[]";
    public bool IsPublished { get; set; }
    public int Version { get; set; }
    public DateTime CreatedAt { get; set; }
    public string CreatedByUserName { get; set; } = string.Empty;
}

/// <summary>
/// 创建表单DTO
/// </summary>
public class CreateFormDto
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string? Schema { get; set; }
    public string? Fields { get; set; }
}

/// <summary>
/// 更新表单DTO
/// </summary>
public class UpdateFormDto
{
    public string? Name { get; set; }
    public string? Description { get; set; }
    public string? Schema { get; set; }
    public string? Fields { get; set; }
}

/// <summary>
/// 字段定义DTO
/// </summary>
public class FieldDefinitionDto
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public string Type { get; set; } = "text"; // text, number, date, select, etc.
    public bool Required { get; set; }
    public string? Placeholder { get; set; }
    public string? DefaultValue { get; set; }
    public object? Options { get; set; } // For select, radio, checkbox
    public Dictionary<string, object>? Validation { get; set; }
    public Dictionary<string, object>? Props { get; set; } // Additional properties
}

/// <summary>
/// 表单实例DTO
/// </summary>
public class FormInstanceDto
{
    public Guid Id { get; set; }
    public Guid FormId { get; set; }
    public string FormName { get; set; } = string.Empty;
    public string Data { get; set; } = "{}";
    public string Status { get; set; } = "draft";
    public DateTime CreatedAt { get; set; }
    public DateTime? SubmittedAt { get; set; }
    public string SubmittedByUserName { get; set; } = string.Empty;
}

/// <summary>
/// 提交表单实例DTO
/// </summary>
public class SubmitFormInstanceDto
{
    public Guid FormId { get; set; }
    public string Data { get; set; } = "{}";
}

/// <summary>
/// 用户DTO
/// </summary>
public class UserDto
{
    public Guid Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string? Role { get; set; }
    public string? Avatar { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
}

/// <summary>
/// 登录DTO
/// </summary>
public class LoginDto
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

/// <summary>
/// 注册DTO
/// </summary>
public class RegisterDto
{
    public string Username { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

/// <summary>
/// 认证响应DTO
/// </summary>
public class AuthResponseDto
{
    public bool Success { get; set; }
    public string? Token { get; set; }
    public string? Message { get; set; }
    public UserDto? User { get; set; }
}
