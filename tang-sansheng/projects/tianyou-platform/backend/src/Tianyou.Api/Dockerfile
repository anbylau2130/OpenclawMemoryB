# 使用.NET 8 SDK镜像进行构建
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# 复制项目文件
COPY ["Tianyou.sln", "./"]
COPY ["src/Tianyou.Api/Tianyou.Api.csproj", "./src/Tianyou.Api/"]
COPY ["src/Tianyou.Application/Tianyou.Application.csproj", "./src/Tianyou.Application/"]
COPY ["src/Tianyou.Domain/Tianyou.Domain.csproj", "./src/Tianyou.Domain/"]
COPY ["src/Tianyou.Infrastructure/Tianyou.Infrastructure.csproj", "./src/Tianyou.Infrastructure/"]

# 还原依赖
RUN dotnet restore

# 复制源代码
COPY src/Tianyou.Api/. ./src/Tianyou.Api/
COPY src/Tianyou.Application/. ./src/Tianyou.Application/
COPY src/Tianyou.Domain/. ./src/Tianyou.Domain/
COPY src/Tianyou.Infrastructure/. ./src/Tianyou.Infrastructure/

# 构建项目
RUN dotnet publish "src/Tianyou.Api/Tianyou.Api.csproj" -c Release -o /app/publish

# 使用.NET 8 Runtime镜像运行
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
EXPOSE 80
EXPOSE 443

# 复制构建产物
COPY --from=build /app/publish .

# 启动应用
ENTRYPOINT ["dotnet", "Tianyou.Api.dll"]