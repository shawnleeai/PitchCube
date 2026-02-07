# PitchCube API 配置指南

## 配置状态总览

| 服务 | 状态 | 用途 | 配置位置 |
|------|------|------|----------|
| StepFun TTS | ✅ 已配置 | 语音解说员 | `backend/.env` |
| StepFun LLM | ✅ 已配置 | 视频脚本生成 | `backend/.env` |
| Stability AI | ⚠️ 占位符 | 海报图像增强 | `backend/.env` |
| OpenAI | ⚠️ 占位符 | 文案优化/DALL-E | `backend/.env` |
| Replicate | ⚠️ 占位符 | 视频生成 | `backend/.env` |

---

## 已验证可用的音色

经过测试，以下 StepFun TTS 音色可用：

| 音色 ID | 名称 | 性别 | 风格 | 适用场景 |
|---------|------|------|------|----------|
| `cixingnansheng` | 磁性男声 | 男 | 专业 | 品牌宣传 |
| `zhengpaiqingnian` | 正派青年 | 男 | 专业 | 商务路演 |
| `ganliannvsheng` | 干练女声 | 女 | 专业 | 正式场合 |
| `ruyananshi` | 儒雅男士 | 男 | 专业 | 文化内容 |
| `linjiajiejie` | 邻家姐姐 | 女 | 亲切 | 轻松场景 |
| `wenrounansheng` | 温柔男声 | 男 | 亲切 | 情感内容 |
| `qinhenvsheng` | 亲和女声 | 女 | 亲切 | 客服场景 |
| `yuanqishaonv` | 元气少女 | 女 | 活力 | 年轻产品 |
| `yuanqinansheng` | 元气男声 | 男 | 活力 | 活泼内容 |
| `huolinvsheng` | 活力女声 | 女 | 活力 | 营销场景 |

---

## 配置文件说明

### 后端配置 (`backend/.env`)

```bash
# =============================================================================
# 阶跃星辰 StepFun API (已配置)
# =============================================================================
STEPFUN_API_KEY=your-stepfun-api-key-here
STEPFUN_TTS_MODEL=step-tts-mini
STEPFUN_LLM_MODEL=step-1-8k

# =============================================================================
# OpenAI API (文案生成/图像生成)
# 获取方式: https://platform.openai.com/api-keys
# =============================================================================
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# =============================================================================
# Stability AI API (海报图像增强)
# 获取方式: https://platform.stability.ai/
# =============================================================================
STABILITY_API_KEY=sk-your-stability-api-key-here
STABILITY_MODEL=stable-diffusion-xl-1024-v1-0

# =============================================================================
# Replicate API (视频生成)
# 获取方式: https://replicate.com/
# =============================================================================
REPLICATE_API_TOKEN=r8-your-replicate-token-here

# =============================================================================
# Runway ML API (视频编辑)
# 获取方式: https://runwayml.com/
# =============================================================================
RUNWAY_API_KEY=your-runway-api-key-here
```

---

## API 端点说明

### 语音服务

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/voice/health` | GET | 健康检查 | ✅ |
| `/api/v1/voice/voices` | GET | 获取音色列表 | ✅ |
| `/api/v1/voice/recommendations` | GET | 场景推荐 | ✅ |
| `/api/v1/voice/generate` | POST | 生成语音 | ✅ |
| `/api/v1/voice/generations/{id}` | GET | 查询任务状态 | ✅ |
| `/api/v1/voice/preview` | POST | 快速预览 | ✅ |

### 海报增强服务

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/posters/enhance/health` | GET | 健康检查 | ✅ |
| `/api/v1/posters/enhance` | POST | AI增强海报 | ⚠️ 需 Stability API Key |
| `/api/v1/posters/enhancements/{id}` | GET | 查询任务状态 | ✅ |
| `/api/v1/posters/styles` | GET | 获取风格列表 | ✅ |

### 视频服务

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/api/v1/videos/health` | GET | 健康检查 | ✅ |
| `/api/v1/videos/generate-script` | POST | 生成脚本 | ✅ |
| `/api/v1/videos/generate` | POST | 生成视频 | ⚠️ 部分功能 |
| `/api/v1/videos/generations/{id}` | GET | 查询任务状态 | ✅ |
| `/api/v1/videos/templates` | GET | 获取模板列表 | ✅ |

---

## 测试示例

### 1. 测试语音生成

```powershell
# 提交生成任务
$body = @{
    text = "欢迎使用 PitchCube 路演魔方"
    voice_style = "professional"
    voice_gender = "male"
    speed = 1.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/voice/generate" `
    -Method POST -ContentType "application/json" -Body $body

# 查询状态
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/voice/generations/{task_id}"
```

### 2. 测试视频脚本生成

```powershell
Invoke-RestMethod -Uri "http://localhost:8001/api/v1/videos/generate-script?`$
    product_name=PitchCube&`$
    product_description=AI驱动的路演展示自动化平台&`$
    key_features=智能海报生成,视频脚本创作&`$
    style=professional&`$
    duration=60&`$
    platform=youtube" -Method POST
```

### 3. 测试海报增强

```powershell
$body = @{
    product_name = "测试产品"
    product_description = "这是一个AI驱动的产品"
    style = "modern tech"
    color_scheme = "blue and purple"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/posters/enhance" `
    -Method POST -ContentType "application/json" -Body $body
```

---

## 获取 API Key

### StepFun (阶跃星辰)
1. 访问 https://platform.stepfun.com/
2. 注册/登录账号
3. 进入「API Keys」页面
4. 创建新的 API Key
5. 复制到 `backend/.env` 中的 `STEPFUN_API_KEY`

### OpenAI
1. 访问 https://platform.openai.com/api-keys
2. 登录账号
3. 点击「Create new secret key」
4. 复制到 `backend/.env` 中的 `OPENAI_API_KEY`

### Stability AI
1. 访问 https://platform.stability.ai/
2. 注册账号
3. 获取 API Key
4. 复制到 `backend/.env` 中的 `STABILITY_API_KEY`

---

## 故障排查

### 语音生成返回 401
- 检查 `backend/.env` 中的 `STEPFUN_API_KEY` 是否正确
- 重启后端服务

### 语音生成返回 400 (voice_id 无效)
- 使用本指南中列出的可用音色 ID
- 避免使用文档中但未启用的音色

### 海报增强返回 503
- 检查 `backend/.env` 中的 `STABILITY_API_KEY` 是否配置
- 需要有效的 Stability AI API Key

---

## 服务启动命令

```bash
# 后端
cd pitchcube-new/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 前端
cd pitchcube-new/frontend
npm run dev
```

---

**最后更新**: 2026-02-02
