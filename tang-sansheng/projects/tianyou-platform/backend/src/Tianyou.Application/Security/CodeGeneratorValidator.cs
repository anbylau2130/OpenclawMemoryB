using System.Text.RegularExpressions;

namespace Tianyou.Application.Security;

/// <summary>
/// 代码生成器安全验证器
/// </summary>
public static class CodeGeneratorValidator
{
    // 危险的命名空间
    private static readonly string[] DangerousNamespaces = 
    {
        "System.IO", "System.Net", "System.Diagnostics",
        "System.Reflection", "System.Runtime.InteropServices",
        "Microsoft.Win32", "System.Threading", "System.Security"
    };

    // 危险的类型
    private static readonly string[] DangerousTypes = 
    {
        "Process", "ProcessStartInfo", "File", "Directory", 
        "FileStream", "StreamWriter", "StreamReader",
        "WebClient", "HttpClient", "Socket",
        "Registry", "RegistryKey"
    };

    // 危险的方法
    private static readonly string[] DangerousMethods = 
    {
        "Execute", "Run", "Start", "Kill", "Delete",
        "CreateDirectory", "WriteAllText", "WriteAllBytes",
        "DownloadFile", "DownloadString", "UploadFile",
        "GetExecutingAssembly", "GetType"
    };

    // 允许的模板类型
    private static readonly string[] AllowedTemplateTypes = 
    {
        "entity", "service", "controller", "dto", 
        "interface", "repository", "validator", "model"
    };

    // 允许的语言
    private static readonly string[] AllowedLanguages = 
    {
        "csharp", "cs", "typescript", "ts", "javascript", "js", 
        "sql", "json", "xml", "html", "css"
    };

    /// <summary>
    /// 验证模板内容是否安全
    /// </summary>
    public static void ValidateTemplateContent(string? templateContent, string fieldName = "模板内容")
    {
        if (string.IsNullOrWhiteSpace(templateContent))
        {
            throw new ArgumentException($"{fieldName}不能为空");
        }

        // 检查危险的命名空间
        foreach (var ns in DangerousNamespaces)
        {
            if (templateContent.Contains(ns, StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException($"{fieldName}包含危险的命名空间: {ns}");
            }
        }

        // 检查危险的类型
        foreach (var type in DangerousTypes)
        {
            var pattern = $@"\b{type}\b";
            if (Regex.IsMatch(templateContent, pattern, RegexOptions.IgnoreCase))
            {
                throw new ArgumentException($"{fieldName}包含危险的类型: {type}");
            }
        }

        // 检查危险的方法
        foreach (var method in DangerousMethods)
        {
            var pattern = $@"\.{method}\s*\(";
            if (Regex.IsMatch(templateContent, pattern, RegexOptions.IgnoreCase))
            {
                throw new ArgumentException($"{fieldName}包含危险的方法调用: {method}");
            }
        }

        // 检查反射和动态代码执行
        if (Regex.IsMatch(templateContent, @"typeof\s*\(", RegexOptions.IgnoreCase))
        {
            throw new ArgumentException($"{fieldName}包含危险的typeof操作");
        }

        if (Regex.IsMatch(templateContent, @"Activator\.CreateInstance", RegexOptions.IgnoreCase))
        {
            throw new ArgumentException($"{fieldName}包含危险的动态实例化");
        }

        if (Regex.IsMatch(templateContent, @"Assembly\.Load", RegexOptions.IgnoreCase))
        {
            throw new ArgumentException($"{fieldName}包含危险的程序集加载");
        }
    }

    /// <summary>
    /// 验证模板类型是否允许
    /// </summary>
    public static void ValidateTemplateType(string? templateType, string fieldName = "模板类型")
    {
        if (string.IsNullOrWhiteSpace(templateType))
        {
            throw new ArgumentException($"{fieldName}不能为空");
        }

        var normalizedType = templateType.ToLower().Trim();

        if (!AllowedTemplateTypes.Contains(normalizedType))
        {
            throw new ArgumentException(
                $"{fieldName}必须是以下类型之一: {string.Join(", ", AllowedTemplateTypes)}");
        }
    }

    /// <summary>
    /// 验证语言是否允许
    /// </summary>
    public static void ValidateLanguage(string? language, string fieldName = "语言")
    {
        if (string.IsNullOrWhiteSpace(language))
        {
            throw new ArgumentException($"{fieldName}不能为空");
        }

        var normalizedLanguage = language.ToLower().Trim();

        if (!AllowedLanguages.Contains(normalizedLanguage))
        {
            throw new ArgumentException(
                $"{fieldName}必须是以下语言之一: {string.Join(", ", AllowedLanguages)}");
        }
    }

    /// <summary>
    /// 验证生成的代码是否安全
    /// </summary>
    public static void ValidateGeneratedCode(string? generatedCode, string fieldName = "生成的代码")
    {
        if (string.IsNullOrWhiteSpace(generatedCode))
        {
            return; // 空代码不需要验证
        }

        // 检查危险的命名空间
        foreach (var ns in DangerousNamespaces)
        {
            if (generatedCode.Contains($"using {ns}", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException($"{fieldName}包含危险的命名空间引用: {ns}");
            }
        }

        // 检查危险的类型使用
        foreach (var type in DangerousTypes)
        {
            var pattern = $@"\b{type}\b";
            if (Regex.IsMatch(generatedCode, pattern, RegexOptions.IgnoreCase))
            {
                throw new ArgumentException($"{fieldName}包含危险的类型: {type}");
            }
        }
    }

    /// <summary>
    /// 沙箱化代码生成 - 移除所有危险内容
    /// </summary>
    public static string SandboxTemplate(string? templateContent)
    {
        if (string.IsNullOrWhiteSpace(templateContent))
        {
            return string.Empty;
        }

        var result = templateContent;

        // 移除危险的命名空间引用
        foreach (var ns in DangerousNamespaces)
        {
            var pattern = $@"using\s+{Regex.Escape(ns)}.*?;";
            result = Regex.Replace(result, pattern, string.Empty, RegexOptions.IgnoreCase);
        }

        // 移除危险的方法调用
        foreach (var method in DangerousMethods)
        {
            var pattern = $@"\.{method}\s*\([^)]*\);?";
            result = Regex.Replace(result, pattern, "// [已移除危险操作]", RegexOptions.IgnoreCase);
        }

        return result;
    }
}
