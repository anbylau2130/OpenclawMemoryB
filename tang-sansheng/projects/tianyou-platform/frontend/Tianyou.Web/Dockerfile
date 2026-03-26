# ========================================
# 阶段1: 构建阶段
# ========================================
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# 复制项目文件
COPY ["Tianyou.Web.csproj", "./"]

# 还原依赖（利用Docker层缓存）
RUN dotnet restore "Tianyou.Web.csproj"

# 复制所有源代码
COPY . .

# 构建并发布Blazor WebAssembly应用
RUN dotnet publish "Tianyou.Web.csproj" \
    -c Release \
    -o /app/publish \
    --no-restore

# ========================================
# 阶段2: 运行时阶段（使用Nginx提供静态文件）
# ========================================
FROM nginx:1.25-alpine AS final
WORKDIR /usr/share/nginx/html

# 安装curl（用于健康检查）
RUN apk add --no-cache curl tzdata

# 设置时区
ENV TZ=Asia/Shanghai

# 复制自定义Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制Blazor WebAssembly构建产物
COPY --from=build /app/publish/wwwroot .

# 创建日志目录
RUN mkdir -p /var/log/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/log/nginx

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
