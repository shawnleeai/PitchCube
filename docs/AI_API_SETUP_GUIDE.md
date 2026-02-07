# PitchCube AI API 配置完全指南

本指南帮助你配置 PitchCube 的 AI API，启用文生图、文生视频、AI 角色扮演等高级功能。

## 📋 功能概览

| 功能 | 所需 API | 推荐提供商 | 成本 |
|------|----------|-----------|------|
| AI 对话/文案生成 | OpenAI / StepFun | OpenAI GPT-4 | $$ |
| 图像生成 | OpenAI / Stability AI | DALL-E 3 | $-$$ |
| 海报增强 | Stability AI | Stability Ultra | $$ |
| 视频生成 | Replicate / Runway | Replicate | $-$$$ |
| 语音合成 | StepFun / Azure | StepFun | $ |
| AI 角色扮演 | OpenAI | GPT-4 | $$ |

## 🚀 快速开始

### 1. 复制环境配置文件

```bash
cd pitchcube-new/backend
cp .env.example .env
```

### 2. 获取 API Key

根据你需要使用的功能，获取相应的 API Key：

#### OpenAI (推荐优先配置)
- 访问: https://platform.openai.com/api-keys
- 注册/登录账号
- 点击 "Create new secret key"
- 复制 Key 到 `.env` 文件

#### Stability AI (图像生成)
- 访问: https://platform.stability.ai/
- 注册账号
- 进入 Dashboard 获取 API Key

#### Replicate (视频生成)
- 访问: https://replicate.com/
- 使用 GitHub 账号登录
- 进入 Account Settings -> API Tokens
- 创建新的 Token

#### Runway ML (高级视频生成)
- 访问: https://runwayml.com/
- 注册账号
- 进入 Dashboard -> API Keys

#### StepFun 阶跃星辰 (国产服务)
- 访问: https://platform.stepfun.com/
- 注册账号
- 进入「API Keys」页面创建 Key

### 3. 编辑 .env 文件

```bash
# OpenAI (用于对话、图像生成、角色扮演)
OPENAI_API_KEY=sk-your-actual-key-here

# Stability AI (用于海报增强)
STABILITY_API_KEY=sk-your-actual-key-here

# Replicate (用于视频生成)
REPLICATE_API_TOKEN=r8-your-actual-token-here

# StepFun (用于语音合成)
STEPFUN_API_KEY=your-actual-key-here
```

### 4. 验证配置

启动后端服务后，访问健康检查端点：

```bash
# 检查所有 AI 服务状态
curl http://localhost:8001/api/v1/ai/images/health
curl http://localhost:8001/api/v1/ai/videos/health
curl http://localhost:8001/api/v1/ai/roleplay/health
```

## 📚 API 使用指南

### 1. 图像生成

#### 生成图像 (DALL-E 3)
```bash
curl -X POST http://localhost:8001/api/v1/ai/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic tech product showcase, neon lighting, sleek design, 4K quality",
    "provider": "openai",
    "model": "dall-e-3",
    "size": "1024x1024",
    "quality": "hd"
  }'
```

#### 生成海报背景 (Stability AI)
```bash
curl -X POST http://localhost:8001/api/v1/posters/enhanced/enhance \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "PitchCube",
    "product_description": "AI驱动的路演展示平台",
    "style": "modern tech",
    "color_scheme": "blue and purple"
  }'
```

### 2. 视频生成

#### 文生视频
```bash
curl -X POST http://localhost:8001/api/v1/ai/videos/text-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Futuristic product demo, sleek device rotating, holographic interface, cinematic lighting",
    "provider": "replicate",
    "duration": 5,
    "resolution": "720p"
  }'
```

#### 图生视频
```bash
curl -X POST http://localhost:8001/api/v1/ai/videos/image-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/product-image.png",
    "prompt": "product rotation, smooth camera movement",
    "duration": 5,
    "motion_strength": 150
  }'
```

### 3. AI 角色扮演

#### 获取可用角色
```bash
curl http://localhost:8001/api/v1/ai/roleplay/characters
```

#### 创建对话会话
```bash
curl -X POST http://localhost:8001/api/v1/ai/roleplay/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "character_id": "investor",
    "user_id": "user_123"
  }'
```

#### 发送消息
```bash
curl -X POST http://localhost:8001/api/v1/ai/roleplay/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_xxx",
    "message": "帮我分析一下我的路演PPT"
  }'
```

#### WebSocket 实时对话
```javascript
const ws = new WebSocket('ws://localhost:8001/api/v1/ai/roleplay/ws/chat/session_xxx');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'chunk') {
    console.log('收到:', data.content);
  }
};

ws.send(JSON.stringify({ message: '你好！' }));
```

### 4. 语音合成

```bash
curl -X POST http://localhost:8001/api/v1/voice/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 PitchCube，让路演更简单",
    "voice_style": "professional",
    "voice_gender": "female",
    "speed": 1.0
  }'
```

## 🎭 内置角色介绍

| 角色ID | 名称 | 特点 | 适用场景 |
|--------|------|------|----------|
| `investor` | 投资大佬 | 犀利、专业、经验丰富 | 路演前模拟问答 |
| `marketing_guru` | 营销鬼才 | 创意、热情、网感好 | 营销策划讨论 |
| `product_manager` | 产品军师 | 理性、细心、用户导向 | 产品规划咨询 |
| `storyteller` | 品牌故事家 | 感性、细腻、有想象力 | 品牌故事创作 |
| `sales_expert` | 销冠导师 | 自信、亲和、说服力 | 销售话术训练 |
| `tech_expert` | 技术极客 | 严谨、技术深度 | 技术方案讨论 |
| `startup_mentor` | 创业导师 | 务实、坚韧、经验丰富 | 创业指导 |
| `content_creator` | 内容创作者 | 创意、网感好 | 内容创作辅助 |

## 💰 成本参考

### 图像生成
- **DALL-E 3**: $0.04-0.08/张 (标准质量), $0.08-0.12/张 (高清)
- **Stability AI**: $0.01-0.03/张 (按使用量)

### 视频生成
- **Replicate**: $0.01-0.05/秒 (取决于模型)
- **Runway Gen-3**: $0.05-0.10/秒

### 文本生成
- **GPT-4o-mini**: $0.15/1M tokens (输入), $0.60/1M tokens (输出)
- **GPT-4o**: $5/1M tokens (输入), $15/1M tokens (输出)

### 语音合成
- **StepFun TTS**: 约 ¥0.015/千字

## 🔧 故障排查

### 问题：API 返回 401 Unauthorized
**解决方案：**
1. 检查 `.env` 文件中的 API Key 是否正确
2. 确认 API Key 没有过期或被撤销
3. 重启后端服务以加载新的环境变量

### 问题：图像生成返回 503 Service Unavailable
**解决方案：**
1. 检查对应服务的 API Key 是否配置
2. 查看服务健康检查端点确认状态
3. 检查账户余额是否充足

### 问题：视频生成任务一直 processing
**解决方案：**
1. 视频生成通常需要 1-5 分钟
2. 使用 `/generations/{task_id}` 端点查询进度
3. 检查 Replicate/Runway 控制台查看任务状态

### 问题：角色扮演对话质量不高
**解决方案：**
1. 确保使用 OpenAI GPT-4 级别模型
2. 提供更详细的上下文信息
3. 尝试不同的角色预设

## 📝 最佳实践

### 1. API Key 管理
- 为不同环境（开发/测试/生产）使用不同的 API Key
- 定期轮换 API Key
- 使用环境变量或密钥管理服务，不要硬编码

### 2. 成本控制
- 开发测试时使用较低成本的模型（GPT-4o-mini）
- 启用图像/视频生成的缓存机制
- 设置预算告警和使用限额

### 3. 提示词优化
- 图像生成：使用详细的英文描述
- 视频生成：描述镜头运动和场景变化
- 角色扮演：提供充分的上下文信息

### 4. 错误处理
- 实现优雅的降级策略（如 AI 服务不可用时返回模拟数据）
- 设置合理的超时时间
- 记录错误日志便于排查

## 🔗 相关链接

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Stability AI 文档](https://platform.stability.ai/docs)
- [Replicate 文档](https://replicate.com/docs)
- [Runway ML 文档](https://docs.runwayml.com/)
- [StepFun 文档](https://platform.stepfun.com/docs)

---

**最后更新**: 2026-02-05
