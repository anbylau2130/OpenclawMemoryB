using Serilog;
using Serilog.Events;
using Serilog.Sinks.Elasticsearch;
using System.Reflection;

namespace Tianyou.Api.Extensions;

/// <summary>
/// Serilog 配置扩展
/// </summary>
public static class SerilogExtensions
{
    /// <summary>
    /// 配置 Serilog 日志系统
    /// </summary>
    public static WebApplicationBuilder ConfigureSerilog(this WebApplicationBuilder builder)
    {
        var configuration = builder.Configuration;
        var environment = builder.Environment;

        // 创建 Serilog Logger
        var logger = new LoggerConfiguration()
            .ReadFrom.Configuration(configuration)
            .Enrich.FromLogContext()
            .Enrich.WithMachineName()
            .Enrich.WithEnvironmentUserName()
            .Enrich.WithThreadId()
            .Enrich.WithProperty("Application", "Tianyou API")
            .Enrich.WithProperty("Environment", environment.EnvironmentName)
            .Enrich.WithProperty("Version", Assembly.GetExecutingAssembly().GetName().Version?.ToString() ?? "1.0.0")
            
            // 控制台输出
            .WriteTo.Console(
                outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}"
            )
            
            // 文件输出（滚动日志）
            .WriteTo.File(
                path: "logs/tianyou-.log",
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 30,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}",
                restrictedToMinimumLevel: LogEventLevel.Information
            )
            
            // 错误日志单独文件
            .WriteTo.File(
                path: "logs/errors/tianyou-errors-.log",
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 90,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj} {Properties:j}{NewLine}{Exception}",
                restrictedToMinimumLevel: LogEventLevel.Error
            );

        // Seq 日志服务器（如果配置）
        var seqServerUrl = configuration["Serilog:Seq:ServerUrl"];
        if (!string.IsNullOrEmpty(seqServerUrl))
        {
            logger.WriteTo.Seq(
                serverUrl: seqServerUrl,
                apiKey: configuration["Serilog:Seq:ApiKey"],
                restrictedToMinimumLevel: LogEventLevel.Information
            );
        }

        // Elasticsearch 日志（如果配置）
        var elasticsearchUrl = configuration["Serilog:Elasticsearch:Url"];
        if (!string.IsNullOrEmpty(elasticsearchUrl))
        {
            logger.WriteTo.Elasticsearch(new ElasticsearchSinkOptions(new Uri(elasticsearchUrl))
            {
                AutoRegisterTemplate = true,
                AutoRegisterTemplateVersion = AutoRegisterTemplateVersion.ESv7,
                IndexFormat = $"tianyou-logs-{environment.EnvironmentName.ToLower()}-{DateTime.UtcNow:yyyy-MM}",
                MinimumLogEventLevel = LogEventLevel.Information,
                EmitEventFailure = EmitEventFailureHandling.WriteToSelfLog,
                BatchAction = ElasticOpType.Create
            });
        }

        // 创建 Logger
        Log.Logger = logger.CreateLogger();

        // 使用 Serilog
        builder.Host.UseSerilog();

        return builder;
    }

    /// <summary>
    /// 添加请求日志中间件
    /// </summary>
    public static WebApplication UseRequestLoggingMiddleware(this WebApplication app)
    {
        // 使用 Serilog 请求日志中间件
        app.UseSerilogRequestLogging(options =>
        {
            options.MessageTemplate = "HTTP {RequestMethod} {RequestPath} responded {StatusCode} in {Elapsed:0.0000} ms";
            options.EnrichDiagnosticContext = (diagnosticContext, httpContext) =>
            {
                diagnosticContext.Set("RequestHost", httpContext.Request.Host.Value);
                diagnosticContext.Set("RequestScheme", httpContext.Request.Scheme);
                diagnosticContext.Set("RemoteIpAddress", httpContext.Connection.RemoteIpAddress?.ToString());
                diagnosticContext.Set("UserId", httpContext.User?.Identity?.Name ?? "Anonymous");
                diagnosticContext.Set("UserAgent", httpContext.Request.Headers["User-Agent"].ToString());
            };
        });

        return app;
    }
}
