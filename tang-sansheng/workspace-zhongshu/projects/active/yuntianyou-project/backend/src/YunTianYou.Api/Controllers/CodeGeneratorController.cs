using Microsoft.AspNetCore.Mvc;
using YunTianYou.Application.Services;

namespace YunTianYou.Api.Controllers;

/// <summary>
/// 代码生成器控制器
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class CodeGeneratorController : ControllerBase
{
    private readonly CodeGeneratorService _codeGenerator;
    
    public CodeGeneratorController(CodeGeneratorService codeGenerator)
    {
        _codeGenerator = codeGenerator;
    }
    
    /// <summary>
    /// 获取数据模型列表
    /// </summary>
    [HttpGet("models")]
    public async Task<ActionResult> GetDataModels()
    {
        var models = await _codeGenerator.GetDataModelsAsync();
        return Ok(models);
    }
    
    /// <summary>
    /// 创建数据模型
    /// </summary>
    [HttpPost("models")]
    public async Task<ActionResult> CreateDataModel([FromBody] CreateDataModelRequest request)
    {
        var model = await _codeGenerator.CreateDataModelAsync(
            request.Name, request.Description ?? "", request.Schema, request.CreatedByUserId);
        return Ok(model);
    }
    
    /// <summary>
    /// 生成代码
    /// </summary>
    [HttpPost("models/{id}/generate")]
    public async Task<ActionResult> GenerateCode(Guid id)
    {
        try
        {
            var codes = await _codeGenerator.GenerateAllCodeAsync(id);
            return Ok(new { 
                message = "代码生成成功",
                files = codes.Count,
                codes = codes
            });
        }
        catch (ArgumentException ex)
        {
            return NotFound(new { error = ex.Message });
        }
    }
    
    /// <summary>
    /// 获取生成的代码
    /// </summary>
    [HttpGet("models/{id}/codes")]
    public async Task<ActionResult> GetGeneratedCodes(Guid id)
    {
        var codes = await _codeGenerator.GetGeneratedCodesAsync(id);
        return Ok(codes);
    }
}

// DTOs
public class CreateDataModelRequest
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public string Schema { get; set; } = "{}";
    public Guid CreatedByUserId { get; set; }
}
