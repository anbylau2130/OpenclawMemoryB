# 金蝶云苍穹文件上传API文档

**版本**: 金蝶云苍穹 v8.x  
**文档ID**: JJC-20260320-004-api1  
**创建时间**: 2026-03-20

---

## 📋 概述

本文档详细说明金蝶云苍穹系统的文件上传API，包括普通上传、大文件分片上传、断点续传、进度监控等功能。

---

## 📤 1. 普通文件上传

### 1.1 单文件上传

**接口地址**: `POST /api/v1/files/upload`

**请求头**:
```
Content-Type: multipart/form-data
Authorization: Bearer {access_token}
```

**请求参数**:
```
file: (binary) - 要上传的文件
type: (string) - 文件类型（image/document/video/audio）
module: (string) - 业务模块（bill/report/attachment）
billId: (string) - 关联单据ID（可选）
```

**C# 示例**:
```csharp
public class FileUploadService
{
    private readonly HttpClient _httpClient;
    
    public async Task<UploadResult> UploadFileAsync(string filePath, string module)
    {
        var url = "https://k3cloud.yourdomain.com/api/v1/files/upload";
        
        using var formData = new MultipartFormDataContent();
        using var fileContent = new ByteArrayContent(await File.ReadAllBytesAsync(filePath));
        
        fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("image/jpeg");
        
        formData.Add(fileContent, "file", Path.GetFileName(filePath));
        formData.Add(new StringContent("image"), "type");
        formData.Add(new StringContent(module), "module");
        
        var response = await _httpClient.PostAsync(url, formData);
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<UploadResult>();
    }
}

public class UploadResult
{
    public string FileId { get; set; }
    public string FileName { get; set; }
    public string FileUrl { get; set; }
    public long FileSize { get; set; }
    public string MimeType { get; set; }
    public DateTime UploadTime { get; set; }
}
```

**JSON 响应**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "fileId": "FILE_20260320_001",
    "fileName": "invoice.jpg",
    "fileUrl": "https://cdn.k3cloud.com/files/2026/03/20/FILE_20260320_001.jpg",
    "fileSize": 524288,
    "mimeType": "image/jpeg",
    "uploadTime": "2026-03-20T10:30:00Z"
  }
}
```

---

## 📦 2. 大文件分片上传

### 2.1 分片上传流程

```
1. 初始化上传 → 获取 uploadId
2. 分片上传 → 逐个上传分片
3. 完成上传 → 合并分片
```

### 2.2 初始化分片上传

**接口地址**: `POST /api/v1/files/multipart/init`

**C# 示例**:
```csharp
public class MultipartUploadService
{
    public async Task<MultipartInitResult> InitMultipartUploadAsync(
        string fileName, long fileSize, string module)
    {
        var request = new
        {
            fileName = fileName,
            fileSize = fileSize,
            chunkSize = 5 * 1024 * 1024, // 5MB per chunk
            module = module
        };
        
        var response = await _httpClient.PostAsJsonAsync(
            "https://k3cloud.yourdomain.com/api/v1/files/multipart/init", 
            request);
        
        return await response.Content.ReadFromJsonAsync<MultipartInitResult>();
    }
}

public class MultipartInitResult
{
    public string UploadId { get; set; }
    public string FileId { get; set; }
    public int TotalChunks { get; set; }
    public int ChunkSize { get; set; }
    public List<int> ChunkNumbers { get; set; }
}
```

**JSON 响应**:
```json
{
  "code": 200,
  "message": "初始化成功",
  "data": {
    "uploadId": "UPLOAD_20260320_123456",
    "fileId": "FILE_20260320_002",
    "totalChunks": 10,
    "chunkSize": 5242880,
    "chunkNumbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  }
}
```

### 2.3 上传分片

**接口地址**: `POST /api/v1/files/multipart/upload`

**C# 示例**:
```csharp
public async Task<ChunkUploadResult> UploadChunkAsync(
    string uploadId, int chunkNumber, byte[] chunkData)
{
    var url = $"https://k3cloud.yourdomain.com/api/v1/files/multipart/upload";
    
    using var formData = new MultipartFormDataContent();
    using var chunkContent = new ByteArrayContent(chunkData);
    
    formData.Add(chunkContent, "chunk", $"chunk_{chunkNumber}.tmp");
    formData.Add(new StringContent(uploadId), "uploadId");
    formData.Add(new StringContent(chunkNumber.ToString()), "chunkNumber");
    
    var response = await _httpClient.PostAsync(url, formData);
    return await response.Content.ReadFromJsonAsync<ChunkUploadResult>();
}

public class ChunkUploadResult
{
    public string UploadId { get; set; }
    public int ChunkNumber { get; set; }
    public string ETag { get; set; }
    public bool Success { get; set; }
}
```

### 2.4 完成分片上传

**接口地址**: `POST /api/v1/files/multipart/complete`

**C# 示例**:
```csharp
public async Task<UploadResult> CompleteMultipartUploadAsync(
    string uploadId, List<ChunkInfo> chunks)
{
    var request = new
    {
        uploadId = uploadId,
        chunks = chunks.Select(c => new {
            chunkNumber = c.ChunkNumber,
            etag = c.ETag
        }).ToList()
    };
    
    var response = await _httpClient.PostAsJsonAsync(
        "https://k3cloud.yourdomain.com/api/v1/files/multipart/complete", 
        request);
    
    return await response.Content.ReadFromJsonAsync<UploadResult>();
}

public class ChunkInfo
{
    public int ChunkNumber { get; set; }
    public string ETag { get; set; }
}
```

**完整分片上传示例**:
```csharp
public async Task<UploadResult> UploadLargeFileAsync(
    string filePath, string module, IProgress<int> progress = null)
{
    var fileInfo = new FileInfo(filePath);
    
    // 1. 初始化
    var initResult = await InitMultipartUploadAsync(
        fileInfo.Name, fileInfo.Length, module);
    
    var chunks = new List<ChunkInfo>();
    var chunkSize = initResult.ChunkSize;
    var totalChunks = initResult.TotalChunks;
    
    // 2. 分片上传
    using var fileStream = File.OpenRead(filePath);
    for (int i = 1; i <= totalChunks; i++)
    {
        var chunkData = new byte[chunkSize];
        var bytesRead = await fileStream.ReadAsync(
            chunkData, 0, chunkSize);
        
        if (bytesRead < chunkSize)
        {
            Array.Resize(ref chunkData, bytesRead);
        }
        
        var chunkResult = await UploadChunkAsync(
            initResult.UploadId, i, chunkData);
        
        chunks.Add(new ChunkInfo
        {
            ChunkNumber = i,
            ETag = chunkResult.ETag
        });
        
        // 上报进度
        progress?.Report((i * 100) / totalChunks);
    }
    
    // 3. 完成上传
    return await CompleteMultipartUploadAsync(
        initResult.UploadId, chunks);
}
```

---

## 🔄 3. 断点续传

### 3.1 查询已上传分片

**接口地址**: `GET /api/v1/files/multipart/parts`

**C# 示例**:
```csharp
public async Task<UploadedPartsResult> GetUploadedPartsAsync(string uploadId)
{
    var url = $"https://k3cloud.yourdomain.com/api/v1/files/multipart/parts?uploadId={uploadId}";
    var response = await _httpClient.GetAsync(url);
    return await response.Content.ReadFromJsonAsync<UploadedPartsResult>();
}

public class UploadedPartsResult
{
    public string UploadId { get; set; }
    public List<int> UploadedChunks { get; set; }
    public int TotalChunks { get; set; }
}
```

### 3.2 断点续传实现

```csharp
public async Task<UploadResult> ResumeUploadAsync(
    string filePath, string uploadId, IProgress<int> progress = null)
{
    var fileInfo = new FileInfo(filePath);
    
    // 1. 查询已上传的分片
    var uploadedParts = await GetUploadedPartsAsync(uploadId);
    var uploadedSet = new HashSet<int>(uploadedParts.UploadedChunks);
    
    var chunks = new List<ChunkInfo>();
    var chunkSize = 5 * 1024 * 1024; // 5MB
    var totalChunks = (int)Math.Ceiling((double)fileInfo.Length / chunkSize);
    
    // 2. 只上传未完成的分片
    using var fileStream = File.OpenRead(filePath);
    for (int i = 1; i <= totalChunks; i++)
    {
        if (uploadedSet.Contains(i))
        {
            // 跳过已上传的分片
            continue;
        }
        
        fileStream.Position = (i - 1) * chunkSize;
        var chunkData = new byte[chunkSize];
        var bytesRead = await fileStream.ReadAsync(chunkData, 0, chunkSize);
        
        if (bytesRead < chunkSize)
        {
            Array.Resize(ref chunkData, bytesRead);
        }
        
        var chunkResult = await UploadChunkAsync(uploadId, i, chunkData);
        
        chunks.Add(new ChunkInfo
        {
            ChunkNumber = i,
            ETag = chunkResult.ETag
        });
        
        progress?.Report((i * 100) / totalChunks);
    }
    
    // 3. 完成上传
    return await CompleteMultipartUploadAsync(uploadId, chunks);
}
```

---

## 📊 4. 上传进度监控

### 4.1 WebSocket实时进度

**连接地址**: `ws://k3cloud.yourdomain.com/ws/upload`

**C# 示例**:
```csharp
public class UploadProgressMonitor
{
    private readonly ClientWebSocket _webSocket;
    
    public async Task ConnectAsync(string uploadId)
    {
        await _webSocket.ConnectAsync(
            new Uri($"ws://k3cloud.yourdomain.com/ws/upload?uploadId={uploadId}"), 
            CancellationToken.None);
        
        _ = Task.Run(ReceiveProgressAsync);
    }
    
    private async Task ReceiveProgressAsync()
    {
        var buffer = new byte[1024];
        
        while (_webSocket.State == WebSocketState.Open)
        {
            var result = await _webSocket.ReceiveAsync(
                new ArraySegment<byte>(buffer), 
                CancellationToken.None);
            
            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                var progress = JsonSerializer.Deserialize<UploadProgress>(message);
                
                OnProgressChanged?.Invoke(this, progress);
            }
        }
    }
    
    public event EventHandler<UploadProgress> OnProgressChanged;
}

public class UploadProgress
{
    public string UploadId { get; set; }
    public int TotalChunks { get; set; }
    public int UploadedChunks { get; set; }
    public int Percentage { get; set; }
    public long UploadedBytes { get; set; }
    public long TotalBytes { get; set; }
    public double Speed { get; set; } // KB/s
    public TimeSpan? RemainingTime { get; set; }
}
```

**JSON 进度消息**:
```json
{
  "uploadId": "UPLOAD_20260320_123456",
  "totalChunks": 10,
  "uploadedChunks": 7,
  "percentage": 70,
  "uploadedBytes": 36700160,
  "totalBytes": 52428800,
  "speed": 2048.5,
  "remainingTime": "00:00:05"
}
```

---

## 🗑️ 5. 文件删除

**接口地址**: `DELETE /api/v1/files/{fileId}`

**C# 示例**:
```csharp
public async Task<bool> DeleteFileAsync(string fileId)
{
    var url = $"https://k3cloud.yourdomain.com/api/v1/files/{fileId}";
    var response = await _httpClient.DeleteAsync(url);
    return response.IsSuccessStatusCode;
}
```

---

## 📋 6. 文件元数据查询

**接口地址**: `GET /api/v1/files/{fileId}/metadata`

**C# 示例**:
```csharp
public async Task<FileMetadata> GetFileMetadataAsync(string fileId)
{
    var url = $"https://k3cloud.yourdomain.com/api/v1/files/{fileId}/metadata";
    var response = await _httpClient.GetAsync(url);
    return await response.Content.ReadFromJsonAsync<FileMetadata>();
}

public class FileMetadata
{
    public string FileId { get; set; }
    public string FileName { get; set; }
    public string FileUrl { get; set; }
    public long FileSize { get; set; }
    public string MimeType { get; set; }
    public string Module { get; set; }
    public string BillId { get; set; }
    public DateTime UploadTime { get; set; }
    public string UploadedBy { get; set; }
    public string Checksum { get; set; }
}
```

---

## 🔒 7. 文件访问权限

### 7.1 临时访问链接

**接口地址**: `POST /api/v1/files/{fileId}/presign`

**C# 示例**:
```csharp
public async Task<PresignedUrl> GetPresignedUrlAsync(
    string fileId, int expiresIn = 3600)
{
    var request = new
    {
        fileId = fileId,
        expiresIn = expiresIn // 秒
    };
    
    var response = await _httpClient.PostAsJsonAsync(
        "https://k3cloud.yourdomain.com/api/v1/files/{fileId}/presign", 
        request);
    
    return await response.Content.ReadFromJsonAsync<PresignedUrl>();
}

public class PresignedUrl
{
    public string Url { get; set; }
    public DateTime ExpiresAt { get; set; }
}
```

---

## 📏 8. 文件大小限制

| 文件类型 | 单文件限制 | 总容量限制 |
|---------|-----------|-----------|
| 图片 (image) | 10 MB | 1 GB |
| 文档 (document) | 50 MB | 5 GB |
| 视频 (video) | 500 MB | 10 GB |
| 音频 (audio) | 50 MB | 2 GB |

---

## 🚫 9. 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 40001 | 文件大小超过限制 | 压缩文件或使用分片上传 |
| 40002 | 文件类型不支持 | 检查文件扩展名 |
| 40003 | 上传中断 | 使用断点续传 |
| 40004 | 文件不存在 | 检查文件ID |
| 40005 | 权限不足 | 检查访问权限 |

---

**文档版本**: v1.0  
**最后更新**: 2026-03-20  
**维护者**: 尚书省·工部
