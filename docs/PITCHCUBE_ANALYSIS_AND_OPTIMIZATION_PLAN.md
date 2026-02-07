# PitchCube 项目现状分析与优化方案

> 文档生成日期：2026-02-01
> 分析范围：前端、后端、数据库、AI服务、部署运维

---

## 📊 一、项目现状概览

### 1.1 架构概述

PitchCube 采用前后端分离的微服务架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Next.js)                       │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│   首页      │  生成器     │   仪表盘    │    登录/注册       │
│  (Landing)  │  (Generate) │ (Dashboard) │   (Auth)          │
└─────────────┴─────────────┴─────────────┴───────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     API 网关 (FastAPI)                        │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  /auth   │ /users   │/products │ /posters │   /videos       │
│  认证    │  用户    │  产品    │  海报    │   视频          │
└──────────┴──────────┴──────────┴──────────┴─────────────────┘
                              │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   MongoDB   │    │    Redis    │    │  AI Services│
   │  (主数据库)  │    │  (缓存/队列) │    │ (可选增强)   │
   └─────────────┘    └─────────────┘    └─────────────┘
```

### 1.2 技术栈清单

| 层级 | 技术选型 | 版本 | 状态 |
|------|----------|------|------|
| 前端框架 | Next.js | 15.x | ✅ 已配置 |
| 前端语言 | TypeScript | 5.x | ✅ 已配置 |
| UI 样式 | Tailwind CSS | 3.x | ✅ 已配置 |
| 动画库 | Framer Motion | - | ✅ 已配置 |
| 图标库 | Lucide React | - | ✅ 已配置 |
| 后端框架 | FastAPI | 0.115+ | ✅ 已配置 |
| 后端语言 | Python | 3.11+ | ✅ 已配置 |
| 数据库 | MongoDB | 6.0+ | ⚠️ 仅连接配置 |
| 缓存 | Redis | 7.0+ | ⚠️ 仅连接配置 |
| 部署 | Docker + Compose | - | ✅ 已配置 |

---

## 📋 二、功能模块详细分析

### 2.1 六大魔方模块状态

```
┌────────────────────────────────────────────────────────────┐
│                    PitchCube 功能矩阵                        │
├──────────────┬──────────────┬──────────────┬───────────────┤
│    模块      │    前端UI    │   后端API    │   实际功能    │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ 🎨 海报工坊   │     ✅       │     ⚠️       │     ⚠️        │
│ 🎬 视频演播室 │     ✅       │     ⚠️       │     ⚠️        │
│ 🖨️ IP铸造厂   │     ✅       │     ❌       │     ❌        │
│ 🎤 语音解说员 │     ✅       │     ❌       │     ❌        │
│ 👥 协作空间   │     ❌       │     ❌       │     ❌        │
│ 📊 数据魔镜   │     ❌       │     ❌       │     ❌        │
└──────────────┴──────────────┴──────────────┴───────────────┘

图例: ✅ 完成  ⚠️ 部分完成/模拟实现  ❌ 未开始
```

### 2.2 各模块详细分析

#### 🎨 海报工坊 (Poster Workshop)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| 模板选择界面 | ✅ 完成 | 4种预设模板展示（科技现代、创业宣言、极简主义、创意渐变）|
| 产品信息表单 | ✅ 完成 | 名称、描述、功能、受众输入 |
| 生成流程UI | ✅ 完成 | 三步流程（选择→输入→结果）|
| 后端生成API | ⚠️ Mock | POST /posters/generate 仅返回模拟数据 |
| 状态查询API | ⚠️ Mock | GET /posters/generations/{id} 返回固定数据 |
| 真实AI生成 | ❌ 未实现 | 需要接入 Stability AI / DALL-E |
| 图片渲染引擎 | ❌ 未实现 | 需要实现 HTML→图片→PDF 转换 |
| 模板管理系统 | ❌ 未实现 | 模板CRUD、动态添加 |

**当前代码分析** (`backend/app/services/poster_generator.py`):
```python
# 当前仅实现 Mock 生成
async def generate_mock(self, request) -> dict:
    # 仅随机选择模板，无实际渲染
    template_id = request.template_id or random.choice(self.templates)
    await asyncio.sleep(2)  # 模拟处理时间
    return {
        "preview_url": f"/generated/{generation_id}_preview.png",  # 不存在
        # ... 模拟数据
    }
```

#### 🎬 视频演播室 (Video Studio)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| 视频脚本生成UI | ✅ 完成 | 时长、风格、平台选择 |
| 脚本生成API | ⚠️ Mock | 返回固定场景模板 |
| 真实视频生成 | ❌ 未实现 | 需要接入 RunwayML / Pika Labs |
| 语音合成 | ❌ 未实现 | Azure Speech 待接入 |
| 字幕生成 | ❌ 未实现 | 需要实现字幕时间轴 |
| 视频渲染引擎 | ❌ 未实现 | FFmpeg 视频合成 |

**当前代码分析** (`backend/app/api/v1/videos.py`):
```python
# 脚本生成仅返回固定模板
scene_templates = [
    {"visual": "开场画面：产品Logo动画...", "narration": "想象一下...", ...},
    # 固定5个场景，无AI生成
]
```

#### 🖨️ IP铸造厂 (IP Foundry)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| UI界面 | ✅ 完成 | 生成器页面包含选项 |
| 后端API | ❌ 未实现 | 无相关路由 |
| 3D模型生成 | ❌ 未实现 | 需要接入 Tripo3D / Meshy |
| STL/OBJ导出 | ❌ 未实现 | 3D文件格式处理 |
| 打印服务对接 | ❌ 未实现 | 在线3D打印API |

#### 🎤 语音解说员 (Voice Narrator)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| UI界面 | ✅ 完成 | 生成器页面包含选项 |
| 后端API | ❌ 未实现 | 无相关路由 |
| 语音合成 | ❌ 未实现 | Azure Speech / ElevenLabs |
| 多语言支持 | ❌ 未实现 | 中英文语音 |
| 风格切换 | ❌ 未实现 | 专业/活泼/沉稳等风格 |

#### 👥 协作空间 (Collaboration Space)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| UI界面 | ❌ 未实现 | 规划中 |
| 后端API | ❌ 未实现 | 需要WebSocket支持 |
| 实时协作 | ❌ 未实现 | Yjs / Socket.io |
| 版本管理 | ❌ 未实现 | Git-like版本控制 |
| 权限系统 | ❌ 未实现 | RBAC权限模型 |

#### 📊 数据魔镜 (Data Mirror)

| 功能点 | 实现状态 | 详细说明 |
|--------|----------|----------|
| UI界面 | ❌ 未实现 | 规划中 |
| 后端API | ❌ 未实现 | 数据分析接口 |
| A/B测试 | ❌ 未实现 | 对比实验系统 |
| 数据可视化 | ❌ 未实现 | 图表展示 |
| 优化建议 | ❌ 未实现 | AI分析建议 |

---

## 🔧 三、后端API实现状态

### 3.1 API路由清单

```
/api/v1
├── /health                 ✅ 完成 - 健康检查
├── /auth
│   ├── POST /register      ✅ 完成 - 用户注册（Mock）
│   ├── POST /token         ✅ 完成 - OAuth2登录（固定账号）
│   ├── POST /login         ✅ 完成 - JSON登录（固定账号）
│   ├── POST /refresh       ✅ 完成 - Token刷新
│   └── POST /logout        ✅ 完成 - 登出
├── /users
│   ├── GET /me             ✅ 完成 - 获取当前用户（Mock）
│   ├── PUT /me             ✅ 完成 - 更新用户信息（Mock）
│   └── GET /me/stats       ✅ 完成 - 用户统计（Mock）
├── /products
│   ├── POST /              ✅ 完成 - 创建产品（无持久化）
│   ├── GET /               ⚠️ 完成 - 返回空数组
│   ├── GET /{id}           ⚠️ 完成 - 返回404
│   ├── PUT /{id}           ⚠️ 完成 - 返回404
│   ├── DELETE /{id}        ⚠️ 完成 - 空操作
│   ├── POST /{id}/analyze  ✅ 完成 - 返回固定分析结果
│   └── GET /{id}/suggestions ✅ 完成 - 返回固定建议
├── /posters
│   ├── GET /templates      ✅ 完成 - 返回4个固定模板
│   ├── GET /templates/{id} ✅ 完成 - 返回指定模板
│   ├── POST /generate      ⚠️ 完成 - 异步Mock生成
│   ├── GET /generations    ⚠️ 完成 - 返回空数组
│   └── GET /generations/{id} ⚠️ 完成 - 返回固定数据
└── /videos
    ├── GET /templates      ✅ 完成 - 返回3个固定模板
    ├── POST /generate-script ⚠️ 完成 - 返回固定脚本
    ├── POST /generate      ⚠️ 完成 - 返回processing状态
    └── GET /generations/{id} ⚠️ 完成 - 返回固定数据

缺失路由:
├── /posters/batch          ❌ 未实现 - 批量生成
├── /ip                     ❌ 未实现 - IP形象生成
├── /voice                  ❌ 未实现 - 语音生成
├── /collaboration          ❌ 未实现 - 协作功能
├── /analytics              ❌ 未实现 - 数据分析
└── /payments               ❌ 未实现 - 支付订阅
```

### 3.2 数据库实现状态

| 组件 | 实现状态 | 说明 |
|------|----------|------|
| MongoDB连接 | ✅ 完成 | motor异步驱动 |
| 索引创建 | ✅ 完成 | users, products, poster_generations |
| 数据模型 | ❌ 未实现 | 无Pydantic模型 |
| CRUD操作 | ❌ 未实现 | 所有API未实际读写数据库 |
| 数据迁移 | ❌ 未实现 | 无迁移脚本 |

---

## ⚠️ 四、核心问题识别

### 4.1 关键问题列表

| 优先级 | 问题 | 影响 | 解决难度 |
|--------|------|------|----------|
| P0 | 数据库未实际使用 | 数据无法持久化 | 中 |
| P0 | 海报无真实生成 | 核心业务不可用 | 高 |
| P0 | 视频无真实生成 | 核心业务不可用 | 高 |
| P1 | 前端未对接真实API | 界面与数据分离 | 低 |
| P1 | 缺少IP/语音后端 | 功能不完整 | 中 |
| P2 | 缺少支付系统 | 无法商业化 | 中 |
| P2 | 缺少协作功能 | 竞争力不足 | 高 |
| P3 | 缺少数据分析 | 无法优化 | 中 |

### 4.2 技术债务

```
1. Mock数据过多
   ├── 所有API返回固定/随机数据
   ├── 无法测试真实业务场景
   └── 用户无法看到实际效果

2. 前端硬编码
   ├── 仪表盘数据写死
   ├── 生成结果仅为占位图
   └── 无实际API调用

3. 缺少错误处理
   ├── API无完善的错误响应
   ├── 前端无错误边界
   └── 无重试机制

4. 安全待加强
   ├── JWT Secret使用默认值
   ├── 无API限流实现
   └── 无输入验证强化

5. 测试缺失
   ├── 无单元测试
   ├── 无集成测试
   └── 无E2E测试
```

---

## 🚀 五、详细优化方案

### 5.1 阶段一：核心功能落地（预计4-6周）

#### 任务1.1：数据库层完善

**目标**：实现真实的数据持久化

**工作内容**：
```python
# 1. 创建数据模型文件 backend/app/models/
- user.py          # 用户模型
- product.py       # 产品模型  
- poster.py        # 海报生成记录
- video.py         # 视频生成记录
- generation.py    # 生成任务基类

# 2. 实现 Repository 模式
- backend/app/repositories/base.py
- backend/app/repositories/user_repo.py
- backend/app/repositories/product_repo.py
- backend/app/repositories/poster_repo.py

# 3. 更新所有API使用真实数据库
- 修改所有"In production"注释的代码
- 实现完整的CRUD
```

**代码示例**：
```python
# backend/app/models/user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

# backend/app/repositories/user_repo.py
from app.db.mongodb import db
from app.models.user import User

class UserRepository:
    collection_name = "users"
    
    async def create(self, user: User) -> User:
        result = await db.db[self.collection_name].insert_one(
            user.model_dump(by_alias=True)
        )
        user.id = str(result.inserted_id)
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await db.db[self.collection_name].find_one({"email": email})
        return User(**doc) if doc else None
    
    # ... 其他CRUD方法
```

#### 任务1.2：海报生成引擎

**目标**：实现真实的海报图片生成

**技术选型**：
- 方案A：HTML→图片 (推荐第一阶段使用)
  - Playwright + html-to-image
  - 灵活可控，无需AI服务
  - 适合模板化生成
  
- 方案B：AI图像生成 (可选增强)
  - Stability AI API
  - DALL-E 3
  - 成本高，质量不稳定

**实现方案**：
```python
# backend/app/services/poster_renderer.py
from playwright.async_api import async_playwright
from jinja2 import Template
import aiofiles

class PosterRenderer:
    """HTML模板渲染引擎"""
    
    TEMPLATE_DIR = "templates/posters"
    
    async def render_poster(self, request: PosterRequest) -> bytes:
        # 1. 加载HTML模板
        template = await self._load_template(request.template_id)
        
        # 2. 渲染数据到HTML
        html_content = template.render(
            product_name=request.product_name,
            description=request.product_description,
            features=request.key_features,
            colors=self._get_template_colors(request.template_id),
            primary_color=request.primary_color or "#0ea5e9"
        )
        
        # 3. 使用Playwright截图
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(html_content)
            await page.set_viewport_size({"width": 1200, "height": 1600})
            
            screenshot = await page.screenshot(
                type="png",
                full_page=False
            )
            
            await browser.close()
            return screenshot
    
    async def convert_to_pdf(self, png_bytes: bytes) -> bytes:
        """PNG转PDF"""
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(png_bytes))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        pdf_buffer = io.BytesIO()
        image.save(pdf_buffer, format='PDF', resolution=300)
        return pdf_buffer.getvalue()

# 模板示例 templates/posters/tech-modern.html
"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            width: 1200px;
            height: 1600px;
            background: linear-gradient(135deg, {{ colors[0] }}, {{ colors[1] }});
            font-family: 'Inter', sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            padding: 80px;
            box-sizing: border-box;
        }
        .product-name {
            font-size: 72px;
            font-weight: bold;
            margin-bottom: 40px;
            text-align: center;
        }
        .description {
            font-size: 32px;
            text-align: center;
            line-height: 1.6;
            opacity: 0.9;
        }
        .features {
            margin-top: 60px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .feature-tag {
            background: rgba(255,255,255,0.2);
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 24px;
        }
    </style>
</head>
<body>
    <div class="product-name">{{ product_name }}</div>
    <div class="description">{{ description }}</div>
    <div class="features">
        {% for feature in features %}
        <span class="feature-tag">{{ feature }}</span>
        {% endfor %}
    </div>
</body>
</html>
"""
```

#### 任务1.3：前端API对接

**目标**：前端调用真实后端API

**实现内容**：
```typescript
// frontend/lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private token: string | null = null;
  
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text());
    }
    
    return response.json();
  }
  
  // 海报生成
  async generatePoster(data: PosterGenerationRequest): Promise<GenerationResponse> {
    return this.request('/posters/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  async getGenerationStatus(id: string): Promise<GenerationResponse> {
    return this.request(`/posters/generations/${id}`);
  }
  
  // 轮询状态
  async pollGenerationStatus(
    id: string, 
    onUpdate: (status: GenerationResponse) => void,
    interval = 2000
  ): Promise<void> {
    const poll = async () => {
      const status = await this.getGenerationStatus(id);
      onUpdate(status);
      
      if (status.status === 'processing') {
        setTimeout(poll, interval);
      }
    };
    await poll();
  }
}

// 使用 React Query 管理状态
// frontend/hooks/usePosterGeneration.ts
import { useMutation, useQuery } from '@tanstack/react-query';

export function usePosterGeneration() {
  const generateMutation = useMutation({
    mutationFn: apiClient.generatePoster.bind(apiClient),
  });
  
  const useGenerationStatus = (id: string | null) => {
    return useQuery({
      queryKey: ['generation', id],
      queryFn: () => apiClient.getGenerationStatus(id!),
      enabled: !!id,
      refetchInterval: (data) => 
        data?.status === 'processing' ? 2000 : false,
    });
  };
  
  return { generateMutation, useGenerationStatus };
}
```

### 5.2 阶段二：功能扩展（预计3-4周）

#### 任务2.1：IP铸造厂后端

```python
# backend/app/api/v1/ip.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class IPGenerationRequest(BaseModel):
    product_name: str
    product_description: str
    style: str = "cute"  # cute, tech, professional
    format: str = "stl"  # stl, obj, glb

@router.post("/generate")
async def generate_ip(request: IPGenerationRequest):
    """
    生成3D IP形象
    可接入 Tripo3D / Meshy API
    """
    # 方案1: 使用 Tripo3D API
    # 方案2: 使用 Meshy API
    # 方案3: 本地 Stable Diffusion + 3D生成
    pass

@router.get("/models/{model_id}/download")
async def download_model(model_id: str, format: str = "stl"):
    """下载3D模型文件"""
    pass
```

**推荐的3D生成服务**：
| 服务 | 价格 | 质量 | 集成难度 |
|------|------|------|----------|
| Tripo3D | $$$ | ⭐⭐⭐⭐⭐ | 低 |
| Meshy | $$ | ⭐⭐⭐⭐ | 低 |
| CSM.ai | $$ | ⭐⭐⭐⭐ | 中 |
| 本地Stable Zero123 | 免费 | ⭐⭐⭐ | 高 |

#### 任务2.2：语音解说员后端

```python
# backend/app/api/v1/voice.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class VoiceGenerationRequest(BaseModel):
    text: str
    voice_style: str = "professional"  # professional, casual, energetic
    language: str = "zh-CN"
    speed: float = 1.0

@router.post("/generate")
async def generate_voice(request: VoiceGenerationRequest):
    """
    语音合成
    可接入 Azure Speech / ElevenLabs
    """
    if settings.AZURE_SPEECH_KEY:
        return await generate_with_azure(request)
    elif settings.ELEVENLABS_API_KEY:
        return await generate_with_elevenlabs(request)
    else:
        return await generate_mock(request)

async def generate_with_azure(request: VoiceGenerationRequest) -> dict:
    import azure.cognitiveservices.speech as speechsdk
    
    speech_config = speechsdk.SpeechConfig(
        subscription=settings.AZURE_SPEECH_KEY,
        region=settings.AZURE_SPEECH_REGION
    )
    
    # 选择音色
    voice_map = {
        "professional": "zh-CN-YunxiNeural",
        "casual": "zh-CN-XiaoxiaoNeural",
        "energetic": "zh-CN-YunyeNeural"
    }
    speech_config.speech_synthesis_voice_name = voice_map.get(
        request.voice_style, "zh-CN-YunxiNeural"
    )
    
    # 生成语音
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(request.text).get()
    
    # 保存音频文件
    audio_path = f"generated/voice_{uuid.uuid4()}.mp3"
    with open(audio_path, "wb") as f:
        f.write(result.audio_data)
    
    return {
        "id": generation_id,
        "audio_url": f"/download/{audio_path}",
        "duration": len(request.text) * 0.3,  # 估算时长
        "voice_style": request.voice_style
    }
```

#### 任务2.3：视频生成增强

```python
# backend/app/services/video_generator.py
class VideoGenerator:
    """视频生成服务"""
    
    async def generate_video(self, script: VideoScript, product: Product) -> str:
        """
        生成完整视频
        1. 根据脚本生成各场景图片 (AI生成或模板)
        2. 生成语音旁白
        3. 合成视频 (FFmpeg)
        4. 添加字幕
        5. 添加背景音乐
        """
        scenes = []
        
        for scene in script.scenes:
            # 生成场景图片
            image_path = await self.generate_scene_image(
                scene.visual_description
            )
            
            # 生成语音
            audio_path = await self.generate_narration(
                scene.narration,
                scene.duration
            )
            
            scenes.append({
                "image": image_path,
                "audio": audio_path,
                "duration": scene.duration,
                "subtitle": scene.subtitle
            })
        
        # 使用FFmpeg合成视频
        video_path = await self.compose_video(scenes)
        
        return video_path
    
    async def compose_video(self, scenes: list) -> str:
        """使用FFmpeg合成视频"""
        import ffmpeg
        
        # 构建FFmpeg命令
        # ffmpeg -i scene1.mp4 -i scene2.mp4 ... -filter_complex concat...
        pass
```

### 5.3 阶段三：商业化与高级功能（预计4-6周）

#### 任务3.1：支付订阅系统

```python
# backend/app/api/v1/payments.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: int  # 分
    price_yearly: int
    features: list
    limits: dict  # 生成次数限制

PLANS = [
    {
        "id": "free",
        "name": "免费版",
        "price_monthly": 0,
        "limits": {
            "posters_per_month": 5,
            "videos_per_month": 1,
            "max_resolution": "1080p"
        }
    },
    {
        "id": "pro",
        "name": "专业版",
        "price_monthly": 2990,  # ¥29.90
        "limits": {
            "posters_per_month": 100,
            "videos_per_month": 20,
            "max_resolution": "4K",
            "remove_watermark": True
        }
    },
    {
        "id": "team",
        "name": "团队版",
        "price_monthly": 9990,  # ¥99.90
        "limits": {
            "posters_per_month": -1,  # 无限
            "videos_per_month": -1,
            "team_members": 5,
            "api_access": True
        }
    }
]

# 集成 Stripe / Paddle / 支付宝 / 微信支付
```

#### 任务3.2：用户权限与团队协作

```python
# backend/app/models/team.py
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class TeamMember(BaseModel):
    user_id: str
    team_id: str
    role: Role
    joined_at: datetime
    invited_by: str

class Team(BaseModel):
    id: str
    name: str
    owner_id: str
    members: list[TeamMember]
    plan_id: str
    created_at: datetime

# Permission decorators
from functools import wraps
from fastapi import HTTPException, status

def require_role(min_role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            # 检查用户权限
            member = await get_team_member(current_user.id, kwargs.get('team_id'))
            if not member or ROLE_HIERARCHY[member.role] < ROLE_HIERARCHY[min_role]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
```

#### 任务3.3：协作空间 (WebSocket)

```python
# backend/app/websocket/collaboration.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
from ypy_websocket import YDoc, WebsocketProvider

class CollaborationManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.docs: Dict[str, YDoc] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user: User):
        await websocket.accept()
        
        if room_id not in self.rooms:
            self.rooms[room_id] = []
            self.docs[room_id] = YDoc()
        
        self.rooms[room_id].append(websocket)
        
        # 发送当前文档状态
        await websocket.send_json({
            "type": "init",
            "data": self.docs[room_id].get_state()
        })
        
        # 广播用户加入
        await self.broadcast(room_id, {
            "type": "user_joined",
            "user": user.username
        }, exclude=websocket)
    
    async def handle_message(self, websocket: WebSocket, room_id: str, message: dict):
        """处理协作消息"""
        msg_type = message.get("type")
        
        if msg_type == "update":
            # 更新文档
            update = message.get("update")
            self.docs[room_id].apply_update(update)
            
            # 广播给其他用户
            await self.broadcast(room_id, {
                "type": "update",
                "update": update,
                "user_id": message.get("user_id")
            }, exclude=websocket)
        
        elif msg_type == "cursor":
            # 光标位置
            await self.broadcast(room_id, {
                "type": "cursor",
                "position": message.get("position"),
                "user_id": message.get("user_id")
            }, exclude=websocket)
    
    async def broadcast(self, room_id: str, message: dict, exclude: WebSocket = None):
        for conn in self.rooms.get(room_id, []):
            if conn != exclude:
                await conn.send_json(message)

collab_manager = CollaborationManager()

@router.websocket("/ws/collab/{room_id}")
async def collaboration_endpoint(websocket: WebSocket, room_id: str):
    user = await authenticate_ws(websocket)
    await collab_manager.connect(websocket, room_id, user)
    
    try:
        while True:
            data = await websocket.receive_json()
            await collab_manager.handle_message(websocket, room_id, data)
    except WebSocketDisconnect:
        await collab_manager.disconnect(websocket, room_id, user)
```

#### 任务3.4：数据魔镜 (分析系统)

```python
# backend/app/services/analytics.py
class AnalyticsService:
    """数据分析服务"""
    
    async def track_generation(self, user_id: str, generation_type: str, metadata: dict):
        """追踪生成事件"""
        await db.analytics.insert_one({
            "event_type": "generation",
            "user_id": user_id,
            "generation_type": generation_type,
            "metadata": metadata,
            "timestamp": datetime.utcnow()
        })
    
    async def get_user_insights(self, user_id: str) -> dict:
        """获取用户洞察"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$generation_type",
                "count": {"$sum": 1},
                "avg_generation_time": {"$avg": "$metadata.generation_time"}
            }}
        ]
        
        results = await db.analytics.aggregate(pipeline).to_list(None)
        
        return {
            "total_generations": sum(r["count"] for r in results),
            "breakdown_by_type": results,
            "most_active_day": await self.get_most_active_day(user_id),
            "usage_trend": await self.get_usage_trend(user_id)
        }
    
    async def ab_test_analysis(self, test_id: str) -> dict:
        """A/B测试结果分析"""
        # 比较两个版本的海报/视频的点击率、转化率
        pass
```

### 5.4 阶段四：性能优化与运维（持续）

#### 任务4.1：缓存策略

```python
# backend/app/core/cache.py
from functools import wraps
import pickle
import hashlib

class CacheService:
    def __init__(self):
        self.redis = redis_client
    
    async def get(self, key: str) -> any:
        data = await self.redis.get(key)
        return pickle.loads(data) if data else None
    
    async def set(self, key: str, value: any, ttl: int = 3600):
        await self.redis.setex(
            key, 
            ttl, 
            pickle.dumps(value)
        )
    
    def cached(self, ttl: int = 3600, key_prefix: str = ""):
        """缓存装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存key
                cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(str(args).encode()).hexdigest()}"
                
                # 尝试获取缓存
                cached = await self.get(cache_key)
                if cached:
                    return cached
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 写入缓存
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator

cache = CacheService()

# 使用示例
@cache.cached(ttl=3600, key_prefix="templates")
async def get_templates():
    return await db.templates.find().to_list(None)
```

#### 任务4.2：任务队列

```python
# backend/app/worker/celery_app.py
from celery import Celery
from celery.signals import task_postrun

celery_app = Celery(
    "pitchcube",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2"
)

@celery_app.task(bind=True, max_retries=3)
def generate_poster_task(self, generation_id: str, request_data: dict):
    """异步海报生成任务"""
    try:
        # 更新状态为 processing
        update_generation_status(generation_id, "processing")
        
        # 生成海报
        generator = PosterRenderer()
        result = generator.render_poster(request_data)
        
        # 保存文件
        file_path = save_generated_file(generation_id, result)
        
        # 更新状态为 completed
        update_generation_status(
            generation_id, 
            "completed",
            file_path=file_path
        )
        
        return {"status": "success", "file_path": file_path}
        
    except Exception as exc:
        # 更新状态为 failed
        update_generation_status(generation_id, "failed", error=str(exc))
        
        # 重试
        raise self.retry(exc=exc, countdown=60)

# 进度回调
@task_postrun.connect
def task_postrun_handler(task_id, task, retval, state):
    # WebSocket通知前端任务完成
    asyncio.create_task(notify_task_complete(task_id, state))
```

#### 任务4.3：监控与日志

```python
# backend/app/core/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# 指标定义
GENERATION_COUNTER = Counter(
    'poster_generations_total',
    'Total poster generations',
    ['status', 'template_id']
)

GENERATION_DURATION = Histogram(
    'poster_generation_duration_seconds',
    'Time spent generating posters',
    ['template_id']
)

ACTIVE_GENERATIONS = Gauge(
    'active_generations',
    'Number of generations in progress'
)

# 监控装饰器
def monitor_generation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        template_id = kwargs.get('template_id', 'unknown')
        
        ACTIVE_GENERATIONS.inc()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            GENERATION_COUNTER.labels(
                status='success',
                template_id=template_id
            ).inc()
            return result
        except Exception as e:
            GENERATION_COUNTER.labels(
                status='failed',
                template_id=template_id
            ).inc()
            raise
        finally:
            ACTIVE_GENERATIONS.dec()
            GENERATION_DURATION.labels(
                template_id=template_id
            ).observe(time.time() - start_time)
    
    return wrapper
```

---

## 📅 六、实施路线图

```
月份:    第1月        第2月        第3月        第4月
         ├───────────┼───────────┼───────────┼───────────┤
阶段一:  ████████████████████
        数据库完善   海报引擎     API对接

阶段二:              ████████████████████
                    IP后端      语音后端     视频增强

阶段三:                          ████████████████████
                                支付系统     协作空间     数据分析

阶段四:                                      ████████████████████
                                            性能优化     监控运维     测试上线

里程碑:  M1          M2          M3          M4
        MVP可用     功能完整    商业化      正式发布
```

### 里程碑定义

| 里程碑 | 日期 | 目标 | 验收标准 |
|--------|------|------|----------|
| M1 | 第4周末 | MVP可用 | 数据库持久化 + 真实海报生成 |
| M2 | 第8周末 | 功能完整 | 六大模块全部可用 |
| M3 | 第12周末 | 商业化 | 支付系统 + 订阅管理 |
| M4 | 第16周末 | 正式发布 | 性能优化 + 完整测试 |

---

## 💰 七、成本估算

### 7.1 开发成本

| 角色 | 人数 | 时间 | 月成本 | 总成本 |
|------|------|------|--------|--------|
| 全栈工程师 | 1 | 4个月 | ¥25,000 | ¥100,000 |
| 前端工程师 | 1 | 3个月 | ¥20,000 | ¥60,000 |
| UI/UX设计师 | 0.5 | 2个月 | ¥15,000 | ¥15,000 |
| **合计** | | | | **¥175,000** |

### 7.2 运营成本（月度）

| 项目 | 配置 | 月费用 |
|------|------|--------|
| 服务器 | 4核8GB x 2 | ¥400 |
| MongoDB Atlas | M10集群 | ¥500 |
| Redis Cloud | 5GB | ¥200 |
| 对象存储 | 100GB | ¥100 |
| CDN | 1TB流量 | ¥200 |
| AI服务 | 按需 | ¥500-2000 |
| **合计** | | **¥1900-3400/月** |

### 7.3 AI服务成本估算

| 服务 | 单价 | 预估月用量 | 月费用 |
|------|------|------------|--------|
| OpenAI GPT-4 | $0.03/1K tokens | 500K tokens | $15 |
| Stability AI | $0.2/图像 | 500张 | $100 |
| Azure Speech | $16/百万字符 | 100万字符 | $16 |
| Tripo3D | $0.5/模型 | 100个 | $50 |
| **合计** | | | **~$180/月** |

---

## 🎯 八、优先级建议

### 高优先级（立即开始）

1. **数据库持久化** - 所有数据当前是Mock，必须优先解决
2. **海报真实生成** - 核心业务，使用HTML渲染方案快速实现
3. **前端API对接** - 连接前后端，实现完整用户流程

### 中优先级（第2个月）

4. **IP/语音后端** - 完善产品功能矩阵
5. **视频增强** - 从脚本到完整视频的生成
6. **模板管理系统** - 支持动态添加模板

### 低优先级（第3-4个月）

7. **支付订阅** - 商业化准备
8. **协作空间** - 差异化竞争
9. **数据分析** - 优化产品体验

---

## ✅ 九、检查清单

### 发布前检查

- [ ] 所有API使用真实数据库
- [ ] 海报生成返回真实图片
- [ ] 前端正确调用后端API
- [ ] 用户认证流程完整
- [ ] 文件上传/下载正常
- [ ] 错误处理完善
- [ ] 性能测试通过
- [ ] 安全审计通过
- [ ] 文档完整
- [ ] 监控告警配置

---

**文档版本**: v1.0  
**最后更新**: 2026-02-01  
**作者**: AI Assistant
