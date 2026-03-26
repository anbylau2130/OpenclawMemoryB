using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using Tianyou.Web;
using Tianyou.Web.Services;

var builder = WebAssemblyHostBuilder.CreateDefault(args);

// ==================== 根组件配置 ====================
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// ==================== HTTP 客户端配置 ====================
builder.Services.AddScoped(sp => 
{
    var config = sp.GetRequiredService<IConfiguration>();
    var apiBaseUrl = config["ApiBaseUrl"] ?? builder.HostEnvironment.BaseAddress;
    return new HttpClient
    {
        BaseAddress = new Uri(apiBaseUrl),
        Timeout = TimeSpan.FromSeconds(30)
    };
});

// ==================== 服务注册 ====================
// 注册认证服务
builder.Services.AddScoped<AuthService>();

// ==================== 启动优化配置 ====================
// 启用延迟加载
builder.Services.AddOptions();
builder.Services.AddLogging();

// 配置组件程序集延迟加载
builder.Services.AddComponents();

// ==================== 构建并运行 ====================
var host = builder.Build();

// 启动性能日志
#if DEBUG
Console.WriteLine($"[Performance] Application started at {DateTime.UtcNow:yyyy-MM-dd HH:mm:ss.fff}");
#endif

await host.RunAsync();
