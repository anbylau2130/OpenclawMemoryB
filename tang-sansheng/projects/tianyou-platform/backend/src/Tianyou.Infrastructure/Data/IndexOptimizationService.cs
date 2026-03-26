using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace Tianyou.Infrastructure.Data;

/// <summary>
/// 数据库索引优化服务
/// </summary>
public class IndexOptimizationService
{
    private readonly TianyouDbContext _context;
    private readonly ILogger<IndexOptimizationService> _logger;

    public IndexOptimizationService(TianyouDbContext context, ILogger<IndexOptimizationService> logger)
    {
        _context = context;
        _logger = logger;
    }

    /// <summary>
    /// 创建性能优化索引
    /// </summary>
    public async Task CreatePerformanceIndexesAsync()
    {
        _logger.LogInformation("开始创建性能优化索引...");

        try
        {
            var connection = _context.Database.GetDbConnection();
            await connection.OpenAsync();

            using var command = connection.CreateCommand();
            
            // Users表索引
            await CreateIndexAsync(command, "IX_Users_Status", "Users", "Status");
            await CreateIndexAsync(command, "IX_Users_IsDeleted", "Users", "IsDeleted");
            await CreateIndexAsync(command, "IX_Users_TenantId", "Users", "TenantId");
            await CreateIndexAsync(command, "IX_Users_CreatedAt", "Users", "CreatedAt DESC");
            await CreateIndexAsync(command, "IX_Users_LastLoginAt", "Users", "LastLoginAt DESC");

            // EntityDefinitions表索引
            await CreateIndexAsync(command, "IX_EntityDefinitions_IsActive", "EntityDefinitions", "IsActive");
            await CreateIndexAsync(command, "IX_EntityDefinitions_IsSystem", "EntityDefinitions", "IsSystem");
            await CreateIndexAsync(command, "IX_EntityDefinitions_CreatedAt", "EntityDefinitions", "CreatedAt");

            // FieldDefinitions表索引
            await CreateIndexAsync(command, "IX_FieldDefinitions_DisplayOrder", "FieldDefinitions", "EntityDefinitionId, DisplayOrder");

            // DynamicData表索引
            await CreateIndexAsync(command, "IX_DynamicData_EntityDefinitionId", "DynamicData", "EntityDefinitionId");
            await CreateIndexAsync(command, "IX_DynamicData_IsDeleted", "DynamicData", "IsDeleted");
            await CreateIndexAsync(command, "IX_DynamicData_CreatedAt", "DynamicData", "CreatedAt DESC");
            await CreateIndexAsync(command, "IX_DynamicData_CreatedBy", "DynamicData", "CreatedBy");
            await CreateIndexAsync(command, "IX_DynamicData_Entity_CreatedAt", "DynamicData", "EntityDefinitionId, CreatedAt DESC");

            // FormDefinitions表索引
            await CreateIndexAsync(command, "IX_FormDefinitions_IsActive", "FormDefinitions", "IsActive");
            await CreateIndexAsync(command, "IX_FormDefinitions_CreatedAt", "FormDefinitions", "CreatedAt");

            // WorkflowInstance表索引
            await CreateIndexAsync(command, "IX_WorkflowInstances_WorkflowDefinitionId", "WorkflowInstances", "WorkflowDefinitionId");
            await CreateIndexAsync(command, "IX_WorkflowInstances_Status", "WorkflowInstances", "Status");
            await CreateIndexAsync(command, "IX_WorkflowInstances_CreatedAt", "WorkflowInstances", "CreatedAt DESC");
            await CreateIndexAsync(command, "IX_WorkflowInstances_Workflow_Status", "WorkflowInstances", "WorkflowDefinitionId, Status");

            // WorkflowTask表索引
            await CreateIndexAsync(command, "IX_WorkflowTasks_WorkflowInstanceId", "WorkflowTasks", "WorkflowInstanceId");
            await CreateIndexAsync(command, "IX_WorkflowTasks_Status", "WorkflowTasks", "Status");
            await CreateIndexAsync(command, "IX_WorkflowTasks_AssignedTo", "WorkflowTasks", "AssignedTo");
            await CreateIndexAsync(command, "IX_WorkflowTasks_Instance_Status", "WorkflowTasks", "WorkflowInstanceId, Status");

            // Notifications表索引
            await CreateIndexAsync(command, "IX_Notifications_UserId", "Notifications", "UserId");
            await CreateIndexAsync(command, "IX_Notifications_IsRead", "Notifications", "IsRead");
            await CreateIndexAsync(command, "IX_Notifications_CreatedAt", "Notifications", "CreatedAt DESC");
            await CreateIndexAsync(command, "IX_Notifications_User_IsRead", "Notifications", "UserId, IsRead");

            // Tenant表索引
            await CreateIndexAsync(command, "IX_Tenants_Status", "Tenants", "Status");
            await CreateIndexAsync(command, "IX_Tenants_IsDeleted", "Tenants", "IsDeleted");
            await CreateIndexAsync(command, "IX_Tenants_CreatedAt", "Tenants", "CreatedAt DESC");

            // 更新统计信息
            _logger.LogInformation("更新数据库统计信息...");
            command.CommandText = "ANALYZE";
            await command.ExecuteNonQueryAsync();

            await connection.CloseAsync();

            _logger.LogInformation("✅ 性能优化索引创建完成");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "创建性能优化索引失败");
            throw;
        }
    }

    /// <summary>
    /// 创建单个索引
    /// </summary>
    private async Task CreateIndexAsync(System.Data.Common.DbCommand command, string indexName, string tableName, string columns)
    {
        try
        {
            command.CommandText = $"CREATE INDEX IF NOT EXISTS {indexName} ON {tableName}({columns})";
            await command.ExecuteNonQueryAsync();
            _logger.LogDebug("索引创建成功 - {IndexName} ON {TableName}({Columns})", indexName, tableName, columns);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "索引创建失败或已存在 - {IndexName}", indexName);
        }
    }

    /// <summary>
    /// 验证索引是否存在
    /// </summary>
    public async Task<bool> VerifyIndexExistsAsync(string indexName)
    {
        var connection = _context.Database.GetDbConnection();
        await connection.OpenAsync();

        using var command = connection.CreateCommand();
        command.CommandText = @"
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'index'
                AND name = @indexName";

        var parameter = command.CreateParameter();
        parameter.ParameterName = "@indexName";
        parameter.Value = indexName;
        command.Parameters.Add(parameter);

        var count = Convert.ToInt32(await command.ExecuteScalarAsync());
        await connection.CloseAsync();

        return count > 0;
    }

    /// <summary>
    /// 获取所有性能优化索引
    /// </summary>
    public async Task<List<IndexInfo>> GetPerformanceIndexesAsync()
    {
        var connection = _context.Database.GetDbConnection();
        await connection.OpenAsync();

        using var command = connection.CreateCommand();
        command.CommandText = @"
            SELECT 
                name AS IndexName,
                tbl_name AS TableName,
                sql AS IndexDefinition
            FROM sqlite_master
            WHERE type = 'index'
                AND name LIKE 'IX_%'
            ORDER BY tbl_name, name";

        var indexes = new List<IndexInfo>();
        using var reader = await command.ExecuteReaderAsync();
        
        while (await reader.ReadAsync())
        {
            indexes.Add(new IndexInfo
            {
                IndexName = reader.GetString(0),
                TableName = reader.GetString(1),
                IndexDefinition = reader.GetString(2)
            });
        }

        await connection.CloseAsync();
        return indexes;
    }
}

/// <summary>
/// 索引信息
/// </summary>
public class IndexInfo
{
    public string IndexName { get; set; } = string.Empty;
    public string TableName { get; set; } = string.Empty;
    public string IndexDefinition { get; set; } = string.Empty;
}
