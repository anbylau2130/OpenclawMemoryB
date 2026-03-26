using Microsoft.EntityFrameworkCore;
using Tianyou.Domain.Entities;

namespace Tianyou.Infrastructure.Data;

/// <summary>
/// Tianyou数据库上下文（SQLite）
/// </summary>
public class TianyouDbContext : DbContext
{
    public TianyouDbContext(DbContextOptions<TianyouDbContext> options) : base(options)
    {
    }
    
    // DbSet
    public DbSet<User> Users => Set<User>();
    public DbSet<Role> Roles => Set<Role>();
    public DbSet<Permission> Permissions => Set<Permission>();
    public DbSet<EntityDefinition> EntityDefinitions => Set<EntityDefinition>();
    public DbSet<FieldDefinition> FieldDefinitions => Set<FieldDefinition>();
    public DbSet<DynamicData> DynamicData => Set<DynamicData>();
    public DbSet<FormDefinition> FormDefinitions => Set<FormDefinition>();
    public DbSet<FormField> FormFields => Set<FormField>();
    public DbSet<WorkflowDefinition> WorkflowDefinitions => Set<WorkflowDefinition>();
    public DbSet<WorkflowInstance> WorkflowInstances => Set<WorkflowInstance>();
    public DbSet<WorkflowTask> WorkflowTasks => Set<WorkflowTask>();
    public DbSet<PluginDefinition> PluginDefinitions => Set<PluginDefinition>();
    public DbSet<CodeTemplate> CodeTemplates => Set<CodeTemplate>();
    public DbSet<ReportDefinition> ReportDefinitions => Set<ReportDefinition>();
    public DbSet<Notification> Notifications => Set<Notification>();
    public DbSet<Tenant> Tenants => Set<Tenant>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // 配置User实体
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Username).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PasswordHash).IsRequired();
            entity.Property(e => e.Status).HasDefaultValue("active");
            
            // 软删除查询过滤器
            entity.HasQueryFilter(e => !e.IsDeleted);
        });
        
        // 配置Role实体
        modelBuilder.Entity<Role>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.RoleName).IsUnique();
            entity.HasIndex(e => e.RoleCode).IsUnique();
            entity.Property(e => e.RoleName).IsRequired().HasMaxLength(50);
            entity.Property(e => e.RoleCode).IsRequired().HasMaxLength(50);
        });
        
        // 配置Permission实体
        modelBuilder.Entity<Permission>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.PermissionName).IsUnique();
            entity.HasIndex(e => e.PermissionCode).IsUnique();
            entity.Property(e => e.PermissionName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PermissionCode).IsRequired().HasMaxLength(100);
        });
        
        // 配置多对多关系：User-Role
        modelBuilder.Entity<User>()
            .HasMany(u => u.Roles)
            .WithMany(r => r.Users);
        
        // 配置多对多关系：Role-Permission
        modelBuilder.Entity<Role>()
            .HasMany(r => r.Permissions)
            .WithMany(p => p.Roles);
        
        // 配置EntityDefinition实体
        modelBuilder.Entity<EntityDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.EntityName).IsUnique();
            entity.HasIndex(e => e.TableName).IsUnique();
            entity.Property(e => e.EntityName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.TableName).IsRequired().HasMaxLength(100);
        });
        
        // 配置FieldDefinition实体
        modelBuilder.Entity<FieldDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => new { e.EntityDefinitionId, e.FieldName }).IsUnique();
            entity.Property(e => e.FieldName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.FieldType).IsRequired().HasMaxLength(50);
            entity.HasOne(e => e.Entity)
                  .WithMany(e => e.Fields)
                  .HasForeignKey(e => e.EntityDefinitionId);
        });
        
        // 配置DynamicData实体
        modelBuilder.Entity<DynamicData>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasOne(e => e.Entity)
                  .WithMany()
                  .HasForeignKey(e => e.EntityDefinitionId);
            
            // 软删除查询过滤器
            entity.HasQueryFilter(e => !e.IsDeleted);
        });
        
        // 配置FormDefinition实体
        modelBuilder.Entity<FormDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.FormName).IsUnique();
            entity.Property(e => e.FormName).IsRequired().HasMaxLength(100);
        });
        
        // 配置FormField实体
        modelBuilder.Entity<FormField>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasOne(e => e.Form)
                  .WithMany(f => f.Fields)
                  .HasForeignKey(e => e.FormDefinitionId);
        });
        
        // 配置WorkflowDefinition实体
        modelBuilder.Entity<WorkflowDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.WorkflowName).IsUnique();
            entity.Property(e => e.WorkflowName).IsRequired().HasMaxLength(100);
        });
        
        // 配置WorkflowInstance实体
        modelBuilder.Entity<WorkflowInstance>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Status).IsRequired().HasMaxLength(50);
            entity.HasOne(e => e.Workflow)
                  .WithMany(w => w.Instances)
                  .HasForeignKey(e => e.WorkflowDefinitionId);
        });
        
        // 配置WorkflowTask实体
        modelBuilder.Entity<WorkflowTask>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Status).IsRequired().HasMaxLength(50);
            entity.HasOne(e => e.Instance)
                  .WithMany(i => i.Tasks)
                  .HasForeignKey(e => e.WorkflowInstanceId);
        });
        
        // 配置PluginDefinition实体
        modelBuilder.Entity<PluginDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.PluginCode).IsUnique();
            entity.Property(e => e.PluginName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PluginCode).IsRequired().HasMaxLength(100);
        });
        
        // 配置CodeTemplate实体
        modelBuilder.Entity<CodeTemplate>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.TemplateName).IsUnique();
            entity.Property(e => e.TemplateName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.TemplateType).IsRequired().HasMaxLength(50);
        });
        
        // 配置ReportDefinition实体
        modelBuilder.Entity<ReportDefinition>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.ReportName).IsUnique();
            entity.Property(e => e.ReportName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.ReportType).IsRequired().HasMaxLength(50);
        });
        
        // 配置Notification实体
        modelBuilder.Entity<Notification>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Title).IsRequired().HasMaxLength(200);
            entity.Property(e => e.NotificationType).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Channel).IsRequired().HasMaxLength(50);
        });
        
        // 配置Tenant实体
        modelBuilder.Entity<Tenant>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.TenantCode).IsUnique();
            entity.Property(e => e.TenantName).IsRequired().HasMaxLength(100);
            entity.Property(e => e.TenantCode).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Status).IsRequired().HasMaxLength(20);
            
            // 软删除查询过滤器
            entity.HasQueryFilter(e => !e.IsDeleted);
        });
        
        // 种子数据
        SeedData(modelBuilder);
    }
    
    private void SeedData(ModelBuilder modelBuilder)
    {
        // 默认角色
        modelBuilder.Entity<Role>().HasData(
            new Role
            {
                Id = Guid.Parse("11111111-1111-1111-1111-111111111111"),
                RoleName = "超级管理员",
                RoleCode = "super_admin",
                Description = "系统超级管理员",
                CreatedAt = DateTime.UtcNow
            },
            new Role
            {
                Id = Guid.Parse("22222222-2222-2222-2222-222222222222"),
                RoleName = "管理员",
                RoleCode = "admin",
                Description = "系统管理员",
                CreatedAt = DateTime.UtcNow
            },
            new Role
            {
                Id = Guid.Parse("33333333-3333-3333-3333-333333333333"),
                RoleName = "开发者",
                RoleCode = "developer",
                Description = "开发者",
                CreatedAt = DateTime.UtcNow
            },
            new Role
            {
                Id = Guid.Parse("44444444-4444-4444-4444-444444444444"),
                RoleName = "普通用户",
                RoleCode = "user",
                Description = "普通用户",
                CreatedAt = DateTime.UtcNow
            }
        );
        
        // 默认权限
        modelBuilder.Entity<Permission>().HasData(
            new Permission
            {
                Id = Guid.Parse("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                PermissionName = "用户创建",
                PermissionCode = "user:create",
                Resource = "user",
                Action = "create",
                Description = "创建用户",
                CreatedAt = DateTime.UtcNow
            },
            new Permission
            {
                Id = Guid.Parse("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                PermissionName = "用户查看",
                PermissionCode = "user:read",
                Resource = "user",
                Action = "read",
                Description = "查看用户",
                CreatedAt = DateTime.UtcNow
            },
            new Permission
            {
                Id = Guid.Parse("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                PermissionName = "用户更新",
                PermissionCode = "user:update",
                Resource = "user",
                Action = "update",
                Description = "更新用户",
                CreatedAt = DateTime.UtcNow
            },
            new Permission
            {
                Id = Guid.Parse("dddddddd-dddd-dddd-dddd-dddddddddddd"),
                PermissionName = "用户删除",
                PermissionCode = "user:delete",
                Resource = "user",
                Action = "delete",
                Description = "删除用户",
                CreatedAt = DateTime.UtcNow
            }
        );
    }
}