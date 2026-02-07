# PitchCube API 文档

完整的 RESTful API 参考文档。

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **API 版本**: v1
- **内容类型**: `application/json`
- **认证方式**: Bearer Token (JWT)

## 认证

### 获取 Token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=demo@example.com&password=password
```

**响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 使用 Token

在请求头中添加：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## 接口列表

### 健康检查

#### 基础健康检查
```http
GET /health
```

**响应:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "pitchcube-api"
}
```

#### 详细健康检查
```http
GET /health/detailed
```

---

### 用户管理

#### 注册用户
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "securepassword",
  "full_name": "Full Name"
}
```

#### 获取当前用户
```http
GET /users/me
Authorization: Bearer <token>
```

**响应:**
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "bio": null,
  "company": null,
  "website": null,
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 更新用户信息
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "New Name",
  "bio": "My bio",
  "company": "Company Inc."
}
```

#### 获取用户统计
```http
GET /users/me/stats
Authorization: Bearer <token>
```

**响应:**
```json
{
  "total_products": 5,
  "total_generations": 23,
  "poster_generations": 15,
  "video_generations": 8,
  "storage_used_mb": 45.2
}
```

---

### 产品管理

#### 创建产品
```http
POST /products
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "PitchCube",
  "description": "AI驱动的路演展示自动化平台",
  "tagline": "10秒生成专业路演物料",
  "key_features": [
    "智能海报生成",
    "视频脚本创作",
    "3D IP形象设计"
  ],
  "target_audience": "黑客松团队、初创公司",
  "website_url": "https://pitchcube.app",
  "github_url": "https://github.com/pitchcube"
}
```

**响应:**
```json
{
  "id": "prod_123456",
  "name": "PitchCube",
  "description": "AI驱动的路演展示自动化平台",
  "tagline": "10秒生成专业路演物料",
  "key_features": [...],
  "target_audience": "黑客松团队、初创公司",
  "website_url": "https://pitchcube.app",
  "github_url": "https://github.com/pitchcube",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### 列出所有产品
```http
GET /products?skip=0&limit=100
Authorization: Bearer <token>
```

#### 获取单个产品
```http
GET /products/{product_id}
Authorization: Bearer <token>
```

#### 更新产品
```http
PUT /products/{product_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Name",
  "description": "Updated description"
}
```

#### 删除产品
```http
DELETE /products/{product_id}
Authorization: Bearer <token>
```

#### 分析产品
```http
POST /products/{product_id}/analyze
Authorization: Bearer <token>
```

**响应:**
```json
{
  "key_selling_points": [...],
  "target_audience_suggestions": [...],
  "tagline_suggestions": [...],
  "feature_highlights": [...],
  "tone_recommendation": "...",
  "poster_style_recommendation": "..."
}
```

---

### 海报生成

#### 获取模板列表
```http
GET /posters/templates?category=科技
```

**响应:**
```json
[
  {
    "id": "tech-modern",
    "name": "科技现代",
    "description": "简洁现代的科技感设计",
    "category": "科技",
    "preview_url": "/templates/tech-modern.png",
    "colors": ["#0ea5e9", "#6366f1", "#8b5cf6"]
  }
]
```

#### 生成海报
```http
POST /posters/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_name": "PitchCube",
  "product_description": "AI驱动的路演展示自动化平台",
  "tagline": "10秒生成专业路演物料",
  "key_features": ["智能海报", "视频脚本", "IP形象"],
  "target_audience": "初创公司",
  "template_id": "tech-modern",
  "style": "modern"
}
```

**响应:**
```json
{
  "id": "gen_20240101120000_1234",
  "status": "processing",
  "product_name": "PitchCube",
  "template_id": "tech-modern",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### 查询生成状态
```http
GET /posters/generations/{generation_id}
Authorization: Bearer <token>
```

**响应:**
```json
{
  "id": "gen_20240101120000_1234",
  "status": "completed",
  "product_name": "PitchCube",
  "template_id": "tech-modern",
  "preview_url": "/generated/poster_12345.png",
  "download_urls": {
    "png": "/download/poster_12345.png",
    "pdf": "/download/poster_12345.pdf"
  },
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:00:10Z"
}
```

#### 列出生成历史
```http
GET /posters/generations?limit=10&offset=0
Authorization: Bearer <token>
```

---

### 视频生成

#### 生成视频脚本
```http
POST /videos/generate-script?product_id=prod_123&style=professional&duration=60
Authorization: Bearer <token>
```

**响应:**
```json
{
  "title": "产品路演演示视频",
  "total_duration": 60,
  "target_platform": "youtube",
  "scenes": [
    {
      "scene_number": 1,
      "duration": 15,
      "visual_description": "开场画面：产品Logo动画",
      "narration": "想象一下...",
      "subtitle": "10秒完成数小时工作"
    }
  ],
  "background_music_suggestion": "科技感轻音乐"
}
```

#### 生成视频
```http
POST /videos/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "product_id": "prod_123",
  "script_style": "professional",
  "target_duration": 60,
  "target_platform": "youtube",
  "include_subtitles": true
}
```

#### 获取视频模板
```http
GET /videos/templates
```

**响应:**
```json
[
  {
    "id": "product-demo",
    "name": "产品演示",
    "description": "标准产品功能演示模板",
    "duration_range": "60-120秒"
  }
]
```

---

## 错误处理

### 错误响应格式

```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "validation_error"
}
```

### 常见错误码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 400 | 请求参数错误 | 检查请求体格式 |
| 401 | 未认证 | Token 无效或过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 资源不存在 | 检查 ID 是否正确 |
| 422 | 验证错误 | 参数不符合要求 |
| 429 | 请求过多 | 超出速率限制 |
| 500 | 服务器错误 | 联系管理员 |

---

## 速率限制

- 默认限制：60 请求/分钟
- 认证用户：120 请求/分钟
- 生成接口：10 请求/分钟

响应头中包含限制信息：
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1640995200
```

---

## SDK 示例

### Python

```python
import requests

class PitchCubeClient:
    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def login(self, email: str, password: str):
        response = requests.post(
            f"{self.base_url}/auth/token",
            data={"username": email, "password": password}
        )
        data = response.json()
        self.headers["Authorization"] = f"Bearer {data['access_token']}"
        return data
    
    def create_product(self, product_data: dict):
        response = requests.post(
            f"{self.base_url}/products",
            headers=self.headers,
            json=product_data
        )
        return response.json()
    
    def generate_poster(self, poster_data: dict):
        response = requests.post(
            f"{self.base_url}/posters/generate",
            headers=self.headers,
            json=poster_data
        )
        return response.json()

# 使用示例
client = PitchCubeClient("http://localhost:8000/api/v1")
client.login("demo@example.com", "password")
product = client.create_product({
    "name": "My Product",
    "description": "Product description"
})
```

### JavaScript/TypeScript

```typescript
class PitchCubeClient {
  constructor(private baseUrl: string, private token?: string) {}
  
  setToken(token: string) {
    this.token = token;
  }
  
  private async fetch(path: string, options: RequestInit = {}) {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
  }
  
  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const data = await this.fetch('/auth/token', {
      method: 'POST',
      body: formData,
      headers: {},
    });
    
    this.setToken(data.access_token);
    return data;
  }
  
  async generatePoster(data: any) {
    return this.fetch('/posters/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

// 使用示例
const client = new PitchCubeClient('http://localhost:8000/api/v1');
await client.login('demo@example.com', 'password');
const result = await client.generatePoster({...});
```

---

## 变更日志

### v1.0.0 (2024-01-01)

- 初始版本发布
- 支持海报生成、视频脚本
- 基础用户认证

---

**更多信息请查看:**
- [部署指南](./DEPLOYMENT.md)
- [使用指南](../usage/USER_GUIDE.md)
- [安全指南](../SECURITY.md)
