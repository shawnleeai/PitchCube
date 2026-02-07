# Minimax (稀宇科技) 和 StepFun (阶跃星辰) 接入指南

本指南介绍如何在 PitchCube 中使用国产 AI 服务：**Minimax** 和 **StepFun**。

---

## 📊 服务对比

| 特性 | Minimax (稀宇科技) | StepFun (阶跃星辰) |
|------|-------------------|-------------------|
| **官网** | https://www.minimaxi.com/ | https://platform.stepfun.com/ |
| **LLM 模型** | abab6.5s, abab6.5, abab6 | step-1-8k, step-1-32k, step-1-128k |
| **TTS 音色** | 14种 | 16种 |
| **文本价格** | ¥0.01-0.03/千token | ¥0.015/千token |
| **语音价格** | ¥0.02/千字 | ¥0.015/千字 |
| **特点** | 响应速度快，模型能力强 | 音色丰富，语音自然 |

---

## 🔑 获取 API Key

### Minimax
1. 访问 https://www.minimaxi.com/
2. 注册/登录账号
3. 进入「开发者平台」
4. 创建应用，获取 **API Key** 和 **Group ID**

### StepFun
1. 访问 https://platform.stepfun.com/
2. 注册/登录账号
3. 进入「API Keys」页面
4. 创建新的 API Key

---

## ⚙️ 配置方法

编辑 `pitchcube-new/backend/.env` 文件：

```bash
# =============================================================================
# StepFun (阶跃星辰)
# =============================================================================
STEPFUN_API_KEY=your-stepfun-api-key-here
STEPFUN_TTS_MODEL=step-tts-mini
STEPFUN_LLM_MODEL=step-1-8k

# =============================================================================
# Minimax (稀宇科技)
# =============================================================================
MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_GROUP_ID=your-minimax-group-id-here
MINIMAX_LLM_MODEL=abab6.5s-chat
MINIMAX_TTS_MODEL=speech-01-turbo
```

---

## 🚀 使用 API

### 1. 检查服务状态

```bash
curl http://localhost:8001/api/v1/chinese-ai/health
```

### 2. 查看服务对比

```bash
curl http://localhost:8001/api/v1/chinese-ai/providers
```

### 3. 文本生成

```bash
curl -X POST http://localhost:8001/api/v1/chinese-ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "请为 PitchCube 路演平台写一段产品介绍",
    "provider": "minimax",
    "temperature": 0.7
  }'
```

**provider 可选值：**
- `minimax` - 使用 Minimax
- `stepfun` - 使用 StepFun
- `auto` - 自动选择

### 4. 营销文案生成

```bash
curl -X POST http://localhost:8001/api/v1/chinese-ai/copywriting \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "PitchCube",
    "product_description": "AI驱动的路演展示自动化平台",
    "style": "professional",
    "provider": "stepfun"
  }'
```

### 5. 视频脚本生成

```bash
curl -X POST http://localhost:8001/api/v1/chinese-ai/video-script \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "PitchCube",
    "product_description": "AI驱动的路演展示平台",
    "key_features": ["智能海报生成", "视频脚本创作", "语音合成"],
    "style": "professional",
    "duration": 60,
    "platform": "bilibili",
    "provider": "minimax"
  }'
```

### 6. 获取 TTS 音色列表

```bash
curl http://localhost:8001/api/v1/chinese-ai/tts/voices

# 或指定提供商
curl http://localhost:8001/api/v1/chinese-ai/tts/voices?provider=minimax
```

### 7. 语音合成

```bash
curl -X POST http://localhost:8001/api/v1/chinese-ai/tts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "欢迎使用 PitchCube，让路演更简单！",
    "voice": "presenter_male",
    "provider": "minimax",
    "speed": 1.0
  }'
```

---

## 🎭 TTS 音色推荐

### StepFun 推荐音色

| 音色ID | 名称 | 适用场景 |
|--------|------|----------|
| `zhengpaiqingnian` | 正派青年 | 商务路演、专业解说 |
| `ganliannvsheng` | 干练女声 | 正式场合、产品发布 |
| `cixingnansheng` | 磁性男声 | 品牌宣传、广告配音 |
| `linjiajiejie` | 邻家姐姐 | 轻松场景、产品介绍 |
| `yuanqishaonv` | 元气少女 | 年轻产品、营销视频 |

### Minimax 推荐音色

| 音色ID | 名称 | 适用场景 |
|--------|------|----------|
| `presenter_male` | 男主持人 | 正式路演、新闻播报 |
| `presenter_female` | 女主持人 | 正式路演、新闻播报 |
| `male-qn-jingying` | 精英男士 | 商务场景、专业内容 |
| `female-yujie` | 御姐 | 成熟内容、高端产品 |
| `female-tianmei` | 甜美女孩 | 轻松内容、年轻产品 |

---

## 💰 成本对比

| 服务 | 文本生成 | 语音合成 |
|------|----------|----------|
| **Minimax** | ¥0.01-0.03/千token | ¥0.02/千字 |
| **StepFun** | ¥0.015/千token | ¥0.015/千字 |
| **OpenAI GPT-4** | $0.03-0.06/千token | - |

**建议：**
- 日常开发测试使用国产服务（成本更低）
- 生产环境根据质量要求选择

---

## 🔧 故障排查

### 问题：Minimax 返回 401 Unauthorized
**解决方案：**
1. 检查 `MINIMAX_API_KEY` 是否正确
2. 检查 `MINIMAX_GROUP_ID` 是否正确
3. 确认 API Key 是否有调用权限

### 问题：StepFun 返回 401
**解决方案：**
1. 检查 `STEPFUN_API_KEY` 是否正确
2. 确认 API Key 未过期
3. 检查账户余额是否充足

### 问题：TTS 生成失败
**解决方案：**
1. 检查音色 ID 是否正确
2. 确认文本长度不超过限制（StepFun: 2000字符, Minimax: 8000字符）
3. 检查网络连接

---

## 📚 更多资源

- [Minimax 官方文档](https://www.minimaxi.com/)
- [StepFun 官方文档](https://platform.stepfun.com/)
- [PitchCube AI 配置指南](AI_API_SETUP_GUIDE.md)
