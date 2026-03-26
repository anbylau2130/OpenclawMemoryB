# ========================================
# 阶段1: 构建阶段
# ========================================
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# 复制解决方案文件和所有项目文件（利用Docker层缓存）
COPY ["Tianyou.sln", "./"]
COPY ["src/Tianyou.Api/Tianyou.Api.csproj", "src/Tianyou.Api/"]
COPY ["src/Tianyou.Application/Tianyou.Application.csproj", "src/Tianyou.Application/"]
COPY ["src/Tianyou.Domain/Tianyou.Domain.csproj", "src/Tianyou.Domain/"]
COPY ["src/Tianyou.Infrastructure/Tianyou.Infrastructure.csproj", "src/Tianyou.Infrastructure/"]

# 还原依赖（这一层会被缓存，除非项目文件改变）
RUN dotnet restore "src/Tianyou.Api/Tianyou.Api.csproj"

# 复制所有源代码
COPY ["src/Tianyou.Api/", "src/Tianyou.Api/"]
COPY ["src/Tianyou.Application/", "src/Tianyou.Application/"]
COPY ["src/Tianyou.Domain/", "src/Tianyou.Domain/"]
COPY ["src/Tianyou.Infrastructure/", "src/Tianyou.Infrastructure/"]

# 构建并发布项目
RUN dotnet publish "src/Tianyou.Api/Tianyou.Api.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore \
    /p:PublishTrimmed=true \
    /p:PublishSingleFile=false

# ========================================
# 阶段2: 运行时阶段
# ========================================
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app

# 安装常用工具（用于健康检查和调试）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN adduser --disabled-password --gecos '' appuser

# 暴露端口
EXPOSE 80
EXPOSE 443

# 设置环境变量
ENV ASPNETCORE_URLS=http://+:80
ENV ASPNETCORE_ENVIRONMENT=Production
ENV TZ=Asia/Shanghai

# 复制构建产物
COPY --from=build /app/publish .

# 修改文件所有者
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# 启动应用
ENTRYPOINT ["dotnet", "Tianyou.Api.dll"]
