using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Text;
using Tianyou.Application.Services;
using Tianyou.Infrastructure.Data;

var builder = WebApplication.CreateBuilder(args);

// 添加数据库上下文（SQLite）
builder.Services.AddDbContext<TianyouDbContext>(options =>
    options.UseSqlite(builder.Configuration.GetConnectionString("DefaultConnection")));

// 添加服务
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<EntityService>();
builder.Services.AddScoped<FormService>();
builder.Services.AddScoped<WorkflowService>();
builder.Services.AddScoped<PluginService>();
builder.Services.AddScoped<CodeGeneratorService>();
builder.Services.AddScoped<ReportService>();
builder.Services.AddScoped<NotificationService>();
builder.Services.AddScoped<TenantService>();

// 配置JWT认证
var jwtSettings = builder.Configuration.GetSection("Jwt");
// 从环境变量读取JWT密钥，如果不存在则使用配置文件中的值
var jwtKey = Environment.GetEnvironmentVariable("JWT_SECRET_KEY")
    ?? jwtSettings["Key"]
    ?? throw new InvalidOperationException("JWT密钥未配置！请设置环境变量JWT_SECRET_KEY或在appsettings.json中配置");
var key = Encoding.UTF8.GetBytes(jwtKey);

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
        ValidIssuer = jwtSettings["Issuer"],
        ValidAudience = jwtSettings["Audience"],
        IssuerSigningKey = new SymmetricSecurityKey(key),
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// 配置Swagger
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Tianyou API",
        Version = "v1",
        Description = "Tianyou低代码平台API",
        Contact = new OpenApiContact
        {
            Name = "Tianyou Team",
            Email = "support@tianyou.com"
        }
    });
    
    // 添加JWT认证
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

// 配置CORS - 限制为特定域名
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

// 自动运行数据库迁移和种子数据
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<TianyouDbContext>();
    context.Database.EnsureCreated();
    Console.WriteLine("✅ SQLite数据库已创建");
}

// 开发环境启用Swagger
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Tianyou API v1");
        c.RoutePrefix = "swagger";
    });
}

app.UseHttpsRedirection();
app.UseCors("AllowSpecificOrigins");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

// 健康检查
app.MapGet("/health", () => Results.Ok("Healthy"));
app.MapGet("/", () => Results.Ok("Tianyou API is running!"));

app.Run();