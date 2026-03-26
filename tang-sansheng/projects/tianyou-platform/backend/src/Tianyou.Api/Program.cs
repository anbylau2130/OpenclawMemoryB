using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Text;
using Tianyou.Application.Services;
using Tianyou.Infrastructure.Data;
using AspNetCoreRateLimit;
using Prometheus;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using HealthChecks.UI.Client;
using Tianyou.Api.Extensions;
using Tianyou.Api.Middleware;

var builder = WebApplication.CreateBuilder(args);

// ==================== 配置 Serilog ====================
builder.ConfigureSerilog();

// ==================== 添加数据库上下文 ====================
builder.Services.AddDbContext<TianyouDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// ==================== 配置内存缓存 ====================
builder.Services.AddMemoryCache(options =>
{
    options.SizeLimit = 1000;
});

builder.Services.AddSingleton<Tianyou.Application.Services.ICacheService, Tianyou.Application.Services.MemoryCacheService>();

// ==================== 配置速率限制 ====================
builder.Services.Configure<IpRateLimitOptions>(builder.Configuration.GetSection("IpRateLimiting"));
builder.Services.Configure<IpRateLimitPolicies>(builder.Configuration.GetSection("IpRateLimitPolicies"));
builder.Services.Configure<ClientRateLimitOptions>(builder.Configuration.GetSection("ClientRateLimiting"));
builder.Services.Configure<ClientRateLimitPolicies>(builder.Configuration.GetSection("ClientRateLimitPolicies"));
builder.Services.AddInMemoryRateLimiting();
builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();

// ==================== 添加业务服务 ====================
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<EntityService>();
builder.Services.AddScoped<FormService>();
builder.Services.AddScoped<WorkflowService>();
builder.Services.AddScoped<PluginService>();
builder.Services.AddScoped<CodeGeneratorService>();
builder.Services.AddScoped<ReportService>();
builder.Services.AddScoped<NotificationService>();
builder.Services.AddScoped<TenantService>();
builder.Services.AddScoped<Tianyou.Infrastructure.Data.IndexOptimizationService>();

// ==================== 配置JWT认证 ====================
var jwtSettings = builder.Configuration.GetSection("Jwt");
var jwtKey = Environment.GetEnvironmentVariable("JWT_SECRET_KEY")
    ?? jwtSettings["Key"]
    ?? throw new InvalidOperationException("JWT密钥未配置！请设置环境变量JWT_SECRET_KEY或在appsettings.json中配置");
var key = Encoding.UTF8.GetBytes(jwtKey);

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtSettings["Issuer"],
        ValidAudience = jwtSettings["Audience"],
        IssuerSigningKey = new SymmetricSecurityKey(key),
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// ==================== 配置健康检查 ====================
builder.Services.AddHealthChecks()
    .AddCheck("self", () => Microsoft.Extensions.Diagnostics.HealthChecks.HealthCheckResult.Healthy("API is running"))
    .AddNpgSql(builder.Configuration.GetConnectionString("DefaultConnection") ?? "", name: "database", tags: new[] { "db", "postgresql" })
    .AddRedis(builder.Configuration.GetConnectionString("Redis") ?? "localhost:6379", name: "redis", tags: new[] { "cache", "redis" });

// ==================== 配置Swagger ====================
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Tianyou API",
        Version = "v1",
        Description = "Tianyou低代码平台API - 企业级低代码开发平台",
        Contact = new OpenApiContact
        {
            Name = "Tianyou Team",
            Email = "support@tianyou.com"
        }
    });
    
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme.",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });
    
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// ==================== 配置CORS ====================
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigins", policy =>
    {
        policy.WithOrigins(
                "http://192.168.50.251:8091",
                "http://localhost:8091",
                "http://localhost:5000",
                "http://127.0.0.1:8091",
                "http://127.0.0.1:5000"
              )
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});

var app = builder.Build();

// ==================== 自动运行数据库迁移 ====================
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<TianyouDbContext>();
    context.Database.EnsureCreated();
    Console.WriteLine("✅ SQLite数据库已创建");

    try
    {
        var indexService = scope.ServiceProvider.GetRequiredService<Tianyou.Infrastructure.Data.IndexOptimizationService>();
        indexService.CreatePerformanceIndexesAsync().GetAwaiter().GetResult();
        Console.WriteLine("✅ 性能优化索引已创建");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"⚠️  索引创建警告: {ex.Message}");
    }
}

// ==================== 应用速率限制 ====================
app.UseIpRateLimiting();
app.UseClientRateLimiting();
Console.WriteLine("✅ 速率限制已启用");

// ==================== 使用日志中间件 ====================
app.UseRequestLoggingMiddleware();
app.UseRequestLogging();
app.UseAuditLogging();
Console.WriteLine("✅ 日志中间件已启用");

// ==================== 启用 Prometheus 指标 ====================
app.UseMetricServer("/metrics");
app.UseHttpMetrics();
Console.WriteLine("✅ Prometheus 指标已启用");

// ==================== 配置Swagger ====================
var enableSwagger = app.Environment.IsDevelopment() || 
    builder.Configuration.GetValue<bool>("Swagger:Enabled", false);

if (enableSwagger)
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Tianyou API v1");
        c.RoutePrefix = "swagger";
    });
    
    Console.WriteLine("⚠️  Swagger已启用 - 仅建议在开发环境使用");
}
else
{
    app.UseHttpsRedirection();
    Console.WriteLine("✅ Swagger已禁用（生产环境）");
}

// ==================== 配置健康检查端点 ====================
app.MapHealthChecks("/health", new HealthCheckOptions
{
    Predicate = _ => true,
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready")
});

app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

// ==================== 应用其他中间件 ====================
app.UseCors("AllowSpecificOrigins");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

// ==================== 根端点 ====================
app.MapGet("/", () => Results.Ok(new
{
    name = "Tianyou API",
    version = "v1.0.0",
    status = "running",
    timestamp = DateTime.UtcNow,
    endpoints = new
    {
        health = "/health",
        metrics = "/metrics",
        swagger = enableSwagger ? "/swagger" : "disabled"
    }
}));

app.Run();
