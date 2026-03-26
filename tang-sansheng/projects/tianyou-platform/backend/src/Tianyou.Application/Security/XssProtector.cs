using System.Text;
using System.Text.RegularExpressions;

namespace Tianyou.Application.Security;

/// <summary>
/// XSS防护帮助类
/// </summary>
public static class XssProtector
{
    // 危险的HTML标签
    private static readonly string[] DangerousTags = 
    {
        "script", "iframe", "object", "embed", "form", 
        "input", "button", "textarea", "select", "style",
        "link", "meta", "base", "frame", "frameset"
    };

    // 危险的HTML属性
    private static readonly string[] DangerousAttributes = 
    {
        "onload", "onerror", "onclick", "onmouseover", "onmouseout",
        "onkeydown", "onkeyup", "onfocus", "onblur", "onsubmit",
        "onchange", "ondblclick", "oncontextmenu", "onwheel"
    };

    // 危险的模式
    private static readonly Regex ScriptPattern = new(
        @"<script.*?>.*?</script>",
        RegexOptions.Compiled | RegexOptions.IgnoreCase | RegexOptions.Singleline);

    private static readonly Regex EventPattern = new(
        @"on\w+\s*=",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    private static readonly Regex JavaScriptPattern = new(
        @"javascript\s*:",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    private static readonly Regex DataUrlPattern = new(
        @"data\s*:\s*text/html",
        RegexOptions.Compiled | RegexOptions.IgnoreCase);

    /// <summary>
    /// HTML编码 - 防止XSS攻击
    /// </summary>
    public static string HtmlEncode(string? input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return string.Empty;
        }

        var sb = new StringBuilder(input.Length);
        foreach (var c in input)
        {
            switch (c)
            {
                case '<':
                    sb.Append("&lt;");
                    break;
                case '>':
                    sb.Append("&gt;");
                    break;
                case '"':
                    sb.Append("&quot;");
                    break;
                case '\'':
                    sb.Append("&#x27;");
                    break;
                case '&':
                    sb.Append("&amp;");
                    break;
                case '/':
                    sb.Append("&#x2F;");
                    break;
                default:
                    sb.Append(c);
                    break;
            }
        }
        return sb.ToString();
    }

    /// <summary>
    /// HTML解码
    /// </summary>
    public static string HtmlDecode(string? input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return string.Empty;
        }

        return input
            .Replace("&lt;", "<")
            .Replace("&gt;", ">")
            .Replace("&quot;", "\"")
            .Replace("&#x27;", "'")
            .Replace("&amp;", "&")
            .Replace("&#x2F;", "/");
    }

    /// <summary>
    /// 清理HTML - 移除危险的标签和属性
    /// </summary>
    public static string SanitizeHtml(string? input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return string.Empty;
        }

        var result = input;

        // 移除script标签
        result = ScriptPattern.Replace(result, string.Empty);

        // 移除事件处理器
        result = EventPattern.Replace(result, string.Empty);

        // 移除javascript:协议
        result = JavaScriptPattern.Replace(result, string.Empty);

        // 移除data:text/html URL
        result = DataUrlPattern.Replace(result, string.Empty);

        // 移除危险标签
        foreach (var tag in DangerousTags)
        {
            var tagPattern = new Regex(
                $@"<{tag}.*?>.*?</{tag}>",
                RegexOptions.IgnoreCase | RegexOptions.Singleline);
            result = tagPattern.Replace(result, string.Empty);

            var selfClosingPattern = new Regex(
                $@"<{tag}.*?/>",
                RegexOptions.IgnoreCase);
            result = selfClosingPattern.Replace(result, string.Empty);
        }

        return result.Trim();
    }

    /// <summary>
    /// 验证字符串是否安全（不包含XSS攻击代码）
    /// </summary>
    public static bool IsSafe(string? input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return true;
        }

        // 检查是否包含script标签
        if (ScriptPattern.IsMatch(input))
        {
            return false;
        }

        // 检查是否包含事件处理器
        if (EventPattern.IsMatch(input))
        {
            return false;
        }

        // 检查是否包含javascript:协议
        if (JavaScriptPattern.IsMatch(input))
        {
            return false;
        }

        // 检查是否包含data:text/html
        if (DataUrlPattern.IsMatch(input))
        {
            return false;
        }

        return true;
    }

    /// <summary>
    /// 验证并清理输入（如果发现XSS攻击则抛出异常）
    /// </summary>
    public static string ValidateAndSanitize(string? input, string fieldName = "输入")
    {
        if (string.IsNullOrEmpty(input))
        {
            return string.Empty;
        }

        if (!IsSafe(input))
        {
            throw new ArgumentException($"{fieldName}包含不安全的内容");
        }

        return SanitizeHtml(input);
    }

    /// <summary>
    /// 对代码生成器输出进行编码（保留代码格式）
    /// </summary>
    public static string EncodeForCodeGeneration(string? input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return string.Empty;
        }

        // 只编码最危险的字符，保留代码格式
        return input
            .Replace("<", "&lt;")
            .Replace(">", "&gt;")
            .Replace("\"", "&quot;")
            .Replace("'", "&#x27;");
    }

    /// <summary>
    /// 对标识符进行安全检查（只允许字母、数字、下划线）
    /// </summary>
    public static string SanitizeIdentifier(string? input, string fieldName = "标识符")
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            throw new ArgumentException($"{fieldName}不能为空");
        }

        // 只保留字母、数字、下划线
        var result = Regex.Replace(input, @"[^a-zA-Z0-9_]", string.Empty);

        if (string.IsNullOrEmpty(result))
        {
            throw new ArgumentException($"{fieldName}格式不正确");
        }

        return result;
    }
}
