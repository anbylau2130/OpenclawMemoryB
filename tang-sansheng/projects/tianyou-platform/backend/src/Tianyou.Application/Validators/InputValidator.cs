using System.Text.RegularExpressions;

namespace Tianyou.Application.Validators;

/// <summary>
/// 输入验证帮助类
/// </summary>
public static class InputValidator
{
    // 常量定义
    private const int UsernameMinLength = 3;
    private const int UsernameMaxLength = 50;
    private const int EmailMaxLength = 255;
    private const int PasswordMinLength = 8;
    private const int PasswordMaxLength = 128;
    private const int FullNameMaxLength = 100;
    private const int KeywordMaxLength = 100;
    private const int PageSizeMin = 1;
    private const int PageSizeMax = 100;

    // 正则表达式
    private static readonly Regex EmailRegex = new(
        @"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    private static readonly Regex UsernameRegex = new(
        @"^[a-zA-Z0-9_-]+$",
        RegexOptions.Compiled);

    private static readonly Regex PasswordComplexityRegex = new(
        @"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
        RegexOptions.Compiled);

    /// <summary>
    /// 验证用户名
    /// </summary>
    public static void ValidateUsername(string username)
    {
        if (string.IsNullOrWhiteSpace(username))
        {
            throw new ArgumentException("用户名不能为空");
        }

        if (username.Length < UsernameMinLength || username.Length > UsernameMaxLength)
        {
            throw new ArgumentException($"用户名长度必须在{UsernameMinLength}到{UsernameMaxLength}个字符之间");
        }

        if (!UsernameRegex.IsMatch(username))
        {
            throw new ArgumentException("用户名只能包含字母、数字、下划线和连字符");
        }
    }

    /// <summary>
    /// 验证邮箱
    /// </summary>
    public static void ValidateEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            throw new ArgumentException("邮箱不能为空");
        }

        if (email.Length > EmailMaxLength)
        {
            throw new ArgumentException($"邮箱长度不能超过{EmailMaxLength}个字符");
        }

        if (!EmailRegex.IsMatch(email))
        {
            throw new ArgumentException("邮箱格式不正确");
        }
    }

    /// <summary>
    /// 验证密码
    /// </summary>
    public static void ValidatePassword(string password, bool requireComplexity = true)
    {
        if (string.IsNullOrWhiteSpace(password))
        {
            throw new ArgumentException("密码不能为空");
        }

        if (password.Length < PasswordMinLength || password.Length > PasswordMaxLength)
        {
            throw new ArgumentException($"密码长度必须在{PasswordMinLength}到{PasswordMaxLength}个字符之间");
        }

        if (requireComplexity && !PasswordComplexityRegex.IsMatch(password))
        {
            throw new ArgumentException("密码必须包含大写字母、小写字母、数字和特殊字符");
        }
    }

    /// <summary>
    /// 验证姓名
    /// </summary>
    public static void ValidateFullName(string fullName)
    {
        if (string.IsNullOrWhiteSpace(fullName))
        {
            throw new ArgumentException("姓名不能为空");
        }

        if (fullName.Length > FullNameMaxLength)
        {
            throw new ArgumentException($"姓名长度不能超过{FullNameMaxLength}个字符");
        }
    }

    /// <summary>
    /// 验证分页参数
    /// </summary>
    public static void ValidatePagination(int page, int size)
    {
        if (page < 1)
        {
            throw new ArgumentException("页码必须大于0");
        }

        if (size < PageSizeMin || size > PageSizeMax)
        {
            throw new ArgumentException($"每页大小必须在{PageSizeMin}到{PageSizeMax}之间");
        }
    }

    /// <summary>
    /// 验证关键词
    /// </summary>
    public static void ValidateKeyword(string? keyword)
    {
        if (!string.IsNullOrEmpty(keyword) && keyword.Length > KeywordMaxLength)
        {
            throw new ArgumentException($"关键词长度不能超过{KeywordMaxLength}个字符");
        }
    }

    /// <summary>
    /// 验证ID列表
    /// </summary>
    public static void ValidateIds(List<Guid>? ids, string fieldName = "ID列表")
    {
        if (ids != null && ids.Count == 0)
        {
            throw new ArgumentException($"{fieldName}不能为空列表");
        }
    }

    /// <summary>
    /// 验证GUID
    /// </summary>
    public static void ValidateGuid(Guid id, string fieldName = "ID")
    {
        if (id == Guid.Empty)
        {
            throw new ArgumentException($"{fieldName}不能为空");
        }
    }

    /// <summary>
    /// 验证实体名称
    /// </summary>
    public static void ValidateEntityName(string entityName)
    {
        if (string.IsNullOrWhiteSpace(entityName))
        {
            throw new ArgumentException("实体名称不能为空");
        }

        if (entityName.Length < 2 || entityName.Length > 100)
        {
            throw new ArgumentException("实体名称长度必须在2到100个字符之间");
        }

        if (!Regex.IsMatch(entityName, @"^[a-zA-Z][a-zA-Z0-9_]*$"))
        {
            throw new ArgumentException("实体名称必须以字母开头，只能包含字母、数字和下划线");
        }
    }

    /// <summary>
    /// 验证表名
    /// </summary>
    public static void ValidateTableName(string tableName)
    {
        if (string.IsNullOrWhiteSpace(tableName))
        {
            throw new ArgumentException("表名称不能为空");
        }

        if (tableName.Length < 2 || tableName.Length > 100)
        {
            throw new ArgumentException("表名称长度必须在2到100个字符之间");
        }

        if (!Regex.IsMatch(tableName, @"^[a-z][a-z0-9_]*$"))
        {
            throw new ArgumentException("表名称必须以小写字母开头，只能包含小写字母、数字和下划线");
        }
    }

    /// <summary>
    /// 验证描述
    /// </summary>
    public static void ValidateDescription(string? description)
    {
        if (!string.IsNullOrEmpty(description) && description.Length > 500)
        {
            throw new ArgumentException("描述长度不能超过500个字符");
        }
    }

    /// <summary>
    /// 验证字段名称
    /// </summary>
    public static void ValidateFieldName(string fieldName)
    {
        if (string.IsNullOrWhiteSpace(fieldName))
        {
            throw new ArgumentException("字段名称不能为空");
        }

        if (fieldName.Length < 2 || fieldName.Length > 100)
        {
            throw new ArgumentException("字段名称长度必须在2到100个字符之间");
        }

        if (!Regex.IsMatch(fieldName, @"^[a-zA-Z][a-zA-Z0-9_]*$"))
        {
            throw new ArgumentException("字段名称必须以字母开头，只能包含字母、数字和下划线");
        }
    }

    /// <summary>
    /// 验证字段类型
    /// </summary>
    public static void ValidateFieldType(string fieldType)
    {
        var allowedTypes = new[] { 
            "string", "int", "long", "decimal", "double", "float", 
            "bool", "datetime", "guid", "json", "text" 
        };

        if (string.IsNullOrWhiteSpace(fieldType))
        {
            throw new ArgumentException("字段类型不能为空");
        }

        if (!allowedTypes.Contains(fieldType.ToLower()))
        {
            throw new ArgumentException($"字段类型必须是: {string.Join(", ", allowedTypes)}");
        }
    }

    /// <summary>
    /// 验证最大长度
    /// </summary>
    public static void ValidateMaxLength(int? maxLength)
    {
        if (maxLength.HasValue && (maxLength.Value < 1 || maxLength.Value > 10000))
        {
            throw new ArgumentException("最大长度必须在1到10000之间");
        }
    }

    /// <summary>
    /// 验证租户名称
    /// </summary>
    public static void ValidateTenantName(string tenantName)
    {
        if (string.IsNullOrWhiteSpace(tenantName))
        {
            throw new ArgumentException("租户名称不能为空");
        }

        if (tenantName.Length < 2 || tenantName.Length > 100)
        {
            throw new ArgumentException("租户名称长度必须在2到100个字符之间");
        }
    }

    /// <summary>
    /// 验证租户代码
    /// </summary>
    public static void ValidateTenantCode(string tenantCode)
    {
        if (string.IsNullOrWhiteSpace(tenantCode))
        {
            throw new ArgumentException("租户代码不能为空");
        }

        if (tenantCode.Length < 2 || tenantCode.Length > 50)
        {
            throw new ArgumentException("租户代码长度必须在2到50个字符之间");
        }

        if (!Regex.IsMatch(tenantCode, @"^[a-z][a-z0-9-]*$"))
        {
            throw new ArgumentException("租户代码必须以小写字母开头，只能包含小写字母、数字和连字符");
        }
    }

    /// <summary>
    /// 验证域名
    /// </summary>
    public static void ValidateDomain(string? domain)
    {
        if (!string.IsNullOrEmpty(domain))
        {
            if (domain.Length > 255)
            {
                throw new ArgumentException("域名长度不能超过255个字符");
            }

            if (!Regex.IsMatch(domain, @"^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$"))
            {
                throw new ArgumentException("域名格式不正确");
            }
        }
    }

    /// <summary>
    /// 验证最大用户数
    /// </summary>
    public static void ValidateMaxUsers(int maxUsers)
    {
        if (maxUsers < 1 || maxUsers > 10000)
        {
            throw new ArgumentException("最大用户数必须在1到10000之间");
        }
    }

    /// <summary>
    /// 验证字段值类型是否匹配
    /// </summary>
    public static void ValidateFieldValueType(string fieldName, string fieldType, object? value)
    {
        if (value == null)
        {
            return; // null值允许，由IsRequired验证处理
        }

        var valueStr = value.ToString() ?? string.Empty;

        switch (fieldType.ToLower())
        {
            case "string":
            case "text":
                // 字符串类型，无需额外验证
                break;

            case "int":
                if (!int.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是整数类型");
                }
                break;

            case "long":
                if (!long.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是长整数类型");
                }
                break;

            case "decimal":
                if (!decimal.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是数字类型");
                }
                break;

            case "double":
            case "float":
                if (!double.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是浮点数类型");
                }
                break;

            case "bool":
                if (!bool.TryParse(valueStr, out _) && valueStr != "0" && valueStr != "1")
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是布尔类型（true/false）");
                }
                break;

            case "datetime":
                if (!DateTime.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是日期时间类型");
                }
                break;

            case "guid":
                if (!Guid.TryParse(valueStr, out _))
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是GUID类型");
                }
                break;

            case "json":
                try
                {
                    if (!string.IsNullOrWhiteSpace(valueStr))
                    {
                        System.Text.Json.JsonDocument.Parse(valueStr);
                    }
                }
                catch
                {
                    throw new ArgumentException($"字段 '{fieldName}' 必须是有效的JSON格式");
                }
                break;

            default:
                throw new ArgumentException($"未知的字段类型: {fieldType}");
        }
    }
}
