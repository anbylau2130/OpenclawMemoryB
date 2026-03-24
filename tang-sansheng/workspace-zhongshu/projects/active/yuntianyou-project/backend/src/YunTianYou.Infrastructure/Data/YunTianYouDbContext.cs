using Microsoft.EntityFrameworkCore;
using YunTianYou.Domain.Entities;

namespace YunTianYou.Infrastructure.Data;

/// <summary>
/// 云天佑数据库上下文 - PostgreSQL
/// </summary>
public class YunTianYouDbContext : DbContext
{
    public YunTianYouDbContext(DbContextOptions<YunTianYouDbContext> options) : base(options)
    {
    }
    
    // DbSets
    public DbSet<User> Users => Set<User>();
    public DbSet<Form> Forms => Set<Form>();
    public DbSet<FormInstance> FormInstances => Set<FormInstance>();
    public DbSet<Workflow> Workflows => Set<Workflow>();
    public DbSet<WorkflowInstance> WorkflowInstances => Set<WorkflowInstance>();
    public DbSet<WorkflowHistory> WorkflowHistories => Set<WorkflowHistory>();
    public DbSet<Plugin> Plugins => Set<Plugin>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        
        // User配置
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Username).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Username).IsRequired().HasMaxLength(50);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(100);
            entity.Property(e => e.PasswordHash).IsRequired().HasMaxLength(255);
        });
        
        // Form配置
        modelBuilder.Entity<Form>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Schema).HasColumnType("jsonb");
            entity.Property(e => e.Fields).HasColumnType("jsonb");
            
            entity.HasOne(e => e.CreatedByUser)
                  .WithMany(u => u.Forms)
                  .HasForeignKey(e => e.CreatedByUserId)
                  .OnDelete(DeleteBehavior.Restrict);
        });
        
        // FormInstance配置
        modelBuilder.Entity<FormInstance>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Data).HasColumnType("jsonb");
            entity.Property(e => e.Status).HasMaxLength(20);
            
            entity.HasOne(e => e.Form)
                  .WithMany(f => f.Instances)
                  .HasForeignKey(e => e.FormId)
                  .OnDelete(DeleteBehavior.Cascade);
                  
            entity.HasOne(e => e.SubmittedByUser)
                  .WithMany(u => u.FormInstances)
                  .HasForeignKey(e => e.SubmittedByUserId)
                  .OnDelete(DeleteBehavior.Restrict);
        });
    }
}
