using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Text;
using YunTianYou.Application.Services;
using YunTianYou.Infrastructure.Data;

var builder = WebApplication.CreateBuilder(args);

// ========== 服务配置 ==========

// JWT配置
var jwtKey = builder.Configuration["Jwt:Key"] ?? "YunTianYou_Secret_Key_2026_Very_Long_Key_For_Security";
var jwtIssuer = builder.Configuration["Jwt:Issuer"] ?? "YunTianYou";
var jwtAudience = builder.Configuration["Jwt:Audience"] ?? "YunTianYou";

// 添加认证
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidateLifetime = true,
        ValidateIssuerSigningKey = true,
        ValidIssuer = jwtIssuer,
        ValidAudience = jwtAudience,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
    };
});

// 添加授权
builder.Services.AddAuthorization();

// 添加数据库
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection") 
    ?? "Host=localhost;Database=yty_db;Username=yty;Password=yty123456";

builder.Services.AddDbContext<YunTianYouDbContext>(options =>
    options.UseNpgsql(connectionString));

// 注册服务
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<FormService>();
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<WorkflowService>();
builder.Services.AddScoped<CodeGeneratorService>();

// 添加控制器
builder.Services.AddControllers();

// 添加Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo 
    { 
        Title = "云天佑低代码平台 API", 
        Version = "v1",
        Description = "企业级低代码开发平台"
    });
    
    // JWT认证配置
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT认证，格式：Bearer {token}",
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

// CORS配置
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// ========== 中间件配置 ==========

// 开发环境配置
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "云天佑 API v1");
        c.RoutePrefix = "swagger";
    });
}

// CORS
app.UseCors();

// 认证授权
app.UseAuthentication();
app.UseAuthorization();

// 路由
app.MapControllers();

// ========== 健康检查端点 ==========

app.MapGet("/health", () => Results.Ok(new
{
    status = "ok",
    timestamp = DateTime.UtcNow,
    service = "YunTianYou API",
    version = "1.0.0"
}));

// ========== API信息端点 ==========

app.MapGet("/api", () => Results.Ok(new
{
    name = "云天佑低代码平台",
    version = "1.0.0",
    description = "企业级低代码开发平台",
    features = new[]
    {
        "表单设计器",
        "数据模型编辑",
        "工作流引擎",
        "代码生成器",
        "用户认证"
    },
    endpoints = new
    {
        auth = "/api/auth",
        forms = "/api/forms",
        workflows = "/api/workflows",
        codeGenerator = "/api/codegenerator",
        health = "/health"
    }
}));

// ========== 数据库初始化 ==========

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<YunTianYouDbContext>();
    try
    {
        // 自动迁移（开发环境）
        // db.Database.Migrate();
        Console.WriteLine("✅ 数据库连接成功");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"⚠️ 数据库连接失败: {ex.Message}");
    }
}

Console.WriteLine("🚀 云天佑低代码平台已启动");
Console.WriteLine("📖 API文档: http://localhost:5000/swagger");
Console.WriteLine("❤️ 健康检查: http://localhost:5000/health");

app.Run();
