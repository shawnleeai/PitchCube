# PitchCube AI API 集成 - 快速设置指南

## 🎉 已完成的功能集成

我已经为 PitchCube 项目完成了以下 AI API 集成：

### ✅ 1. 文生图 (Text-to-Image)
- **OpenAI DALL-E 3/2** - 高质量图像生成
- **Stability AI** - 开源模型图像生成
- API 端点: `/api/v1/ai/images/*`

### ✅ 2. 文生视频 (Text-to-Video)
- **Replicate** - 开源视频生成模型 (Wan, LTX-Video, CogVideo)
- **Runway ML** - 专业级视频生成 (Gen-2, Gen-3)
- API 端点: `/api/v1/ai/videos/*`

### ✅ 3. AI 角色扮演 (AI Roleplay)
- **OpenAI GPT-4** 驱动
- 8种内置角色：投资大佬、营销鬼才、产品军师、品牌故事家、销冠导师、技术极客、创业导师、内容创作者
- 支持自定义角色创建
- WebSocket 实时对话
- API 端点: `/api/v1/ai/roleplay/*`

### ✅ 4. 语音合成 (TTS) - 国产 AI
- **StepFun 阶跃星辰** - 16种中文音色
- **Minimax 稀宇科技** - 14种中文音色
- API 端点: `/api/v1/voice/*` 和 `/api/v1/chinese-ai/*`

### ✅ 5. 国产 AI 统一接口
- **StepFun + Minimax** 统一调用接口
- 支持服务对比和自动切换
- API 端点: `/api/v1/chinese-ai/*`

---

## 🚀 快速开始

### 第一步：配置 API Key

编辑 `pitchcube-new/backend/.env` 文件，填入你的 API Key：

```bash
# 1. OpenAI - 用于图像生成、角色扮演、对话 (强烈推荐配置)
OPENAI_API_KEY=sk-your-openai-api-key-here

# 2. Stability AI - 用于海报图像增强
STABILITY_API_KEY=sk-your-stability-api-key-here

# 3. Replicate - 用于视频生成 (开源模型)
REPLICATE_API_TOKEN=r8-your-replicate-token-here

# 4. Runway ML - 用于高质量视频生成
RUNWAY_API_KEY=your-runway-api-key-here

# 5. StepFun (阶跃星辰) - 国产 AI 服务 (语音合成 + LLM)
STEPFUN_API_KEY=your-stepfun-api-key-here

# 6. Minimax (稀宇科技) - 国产 AI 服务 (语音合成 + LLM)
MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_GROUP_ID=your-minimax-group-id-here
```

### 第二步：验证配置

运行配置检查脚本：

```bash
cd pitchcube-new/backend
python check_ai_services.py
```

### 第三步：启动服务

```bash
# 启动后端服务
cd pitchcube-new/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 第四步：测试 API

```bash
# 1. 检查图像生成服务
curl http://localhost:8001/api/v1/ai/images/health

# 2. 检查视频生成服务
curl http://localhost:8001/api/v1/ai/videos/health

# 3. 检查角色扮演服务
curl http://localhost:8001/api/v1/ai/roleplay/health

# 4. 检查国产 AI 服务
curl http://localhost:8001/api/v1/chinese-ai/health

# 5. 获取国产 AI 服务对比
curl http://localhost:8001/api/v1/chinese-ai/providers
```

---

## 📁 新增文件清单

### 核心服务代码
```
pitchcube-new/backend/
├── app/services/
│   ├── ai_service_manager.py          # 统一 AI 服务管理器
│   ├── openai_service.py              # OpenAI/DALL-E 服务
│   ├── video_generation_service.py    # 视频生成服务
│   ├── ai_roleplay_service.py         # AI 角色扮演服务
│   ├── minimax_service.py             # Minimax 服务 ⭐ NEW
│   └── stepfun_service.py             # StepFun 服务
├── app/api/v1/
│   ├── ai_images.py                   # 图像生成 API
│   ├── ai_videos.py                   # 视频生成 API
│   ├── ai_roleplay.py                 # 角色扮演 API
│   ├── chinese_ai.py                  # 国产 AI 统一 API ⭐ NEW
│   └── __init__.py                    # 更新路由注册
├── .env.example                       # 更新配置示例
└── check_ai_services.py               # 配置检查脚本
```

### 文档
```
pitchcube-new/docs/
├── AI_API_SETUP_GUIDE.md              # AI API 配置完全指南
├── MINIMAX_STEPFUN_GUIDE.md           # Minimax + StepFun 指南 ⭐ NEW
└── ...

pitchcube-new/
├── AI_FEATURES_SUMMARY.md             # 功能集成总结
└── SETUP_INSTRUCTIONS.md              # 本文件
```

---

## 🔧 配置文件 (.env)

需要配置的 API Key:

```bash
# 1. OpenAI (用于对话、图像生成、角色扮演) - 推荐优先配置
OPENAI_API_KEY=sk-your-openai-api-key-here

# 2. Stability AI (用于海报图像生成)
STABILITY_API_KEY=sk-your-stability-api-key-here

# 3. Replicate (用于视频生成 - 开源模型)
REPLICATE_API_TOKEN=r8-your-replicate-token-here

# 4. Runway ML (用于视频生成 - 高质量)
RUNWAY_API_KEY=your-runway-api-key-here

# 5. StepFun (阶跃星辰) - 国产 AI 服务
STEPFUN_API_KEY=your-stepfun-api-key-here

# 6. Minimax (稀宇科技) - 国产 AI 服务
MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_GROUP_ID=your-minimax-group-id-here
```

---

## 🚀 快速验证

### 1. 运行配置检查脚本
```bash
cd pitchcube-new/backend
python check_ai_services.py
```

### 2. 测试国产 AI 服务
```bash
# 测试 StepFun TTS
curl -X POST http://localhost:8001/api/v1/chinese-ai/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 PitchCube",
    "voice": "zhengpaiqingnian",
    "provider": "stepfun"
  }'

# 测试 Minimax TTS
curl -X POST http://localhost:8001/api/v1/chinese-ai/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 PitchCube",
    "voice": "presenter_male",
    "provider": "minimax"
  }'

# 测试国产 LLM
curl -X POST http://localhost:8001/api/v1/chinese-ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "请为 PitchCube 路演平台写一段产品介绍",
    "provider": "minimax"
  }'
```

---

## 💡 使用建议

### 优先级配置建议
1. **必需**: StepFun 或 Minimax (国产 AI 语音 + 文本)
2. **强烈推荐**: OpenAI - 图像生成 + 角色扮演
3. **推荐**: Stability AI - 海报增强 + 图像生成备选
4. **可选**: Replicate/Runway - 视频生成

### 国产 AI 服务选择建议
| 场景 | 推荐服务 | 原因 |
|------|----------|------|
| 语音合成 | StepFun | 音色更丰富，价格更低 |
| 文案生成 | Minimax | abab6.5 模型能力强 |
| 视频脚本 | Minimax/StepFun | 两者都可以 |
| 快速响应 | Minimax | API 响应速度快 |

### 成本控制
- 开发测试使用国产服务（成本更低）
- 生产环境根据质量要求选择
- 启用图像缓存避免重复生成

---

## 📚 详细文档

- [AI API 配置完全指南](docs/AI_API_SETUP_GUIDE.md) - 完整的配置和使用说明
- [Minimax + StepFun 指南](docs/MINIMAX_STEPFUN_GUIDE.md) - 国产 AI 服务详细指南
- [AI 功能集成总结](AI_FEATURES_SUMMARY.md) - 所有新增功能的详细说明

---

**集成完成时间**: 2026-02-05
