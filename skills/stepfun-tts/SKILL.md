# StepFun TTS Skill

阶跃星辰语音合成 Skill，用于将文本转换为自然语音。

## 功能特性

- 🎯 **多种音色**: 30+ 种专业中文音色
- 🎨 **风格分类**: 专业/亲切/活力/温柔等多种风格
- ⚡ **快速生成**: 低延迟语音合成
- 🔄 **灵活配置**: 支持语速、音量调节
- 💾 **本地缓存**: 自动缓存已生成的语音

## 支持的音色

### 专业风格
- `zhengpaiqingnian` - 正派青年（男声，适合商务路演）
- `ganliannvsheng` - 干练女声（女声，适合正式场合）
- `cixingnansheng` - 磁性男声（男声，适合品牌宣传）

### 亲切风格
- `linjiajiejie` - 邻家姐姐（女声，适合轻松场景）
- `wenrounansheng` - 温柔男声（男声，适合情感内容）
- `qinhenvsheng` - 亲和女声（女声，适合客服场景）

### 活力风格
- `yuanqishaonv` - 元气少女（女声，适合年轻产品）
- `yuanqinansheng` - 元气男声（男声，适合活泼内容）
- `huolinvsheng` - 活力女声（女声，适合营销场景）

## 快速开始

### 安装依赖

```bash
pip install httpx>=0.24.0
```

### 基础使用

```python
from stepfun_tts import StepFunTTS

# 初始化
tts = StepFunTTS(api_key="your_api_key")

# 生成语音
audio_bytes = await tts.generate(
    text="欢迎使用 PitchCube 路演魔方",
    voice="zhengpaiqingnian",
    speed=1.0
)

# 保存到文件
with open("output.mp3", "wb") as f:
    f.write(audio_bytes)
```

### 按场景选择音色

```python
# 商务路演
tts = StepFunTTS(api_key="your_api_key", default_style="professional")

# 产品介绍
tts = StepFunTTS(api_key="your_api_key", default_style="casual")

# 营销宣传
tts = StepFunTTS(api_key="your_api_key", default_style="energetic")
```

## API 参考

### StepFunTTS

#### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | str | 必填 | 阶跃星辰 API Key |
| `base_url` | str | https://api.stepfun.com/v1 | API 基础地址 |
| `default_voice` | str | zhengpaiqingnian | 默认音色 |
| `default_speed` | float | 1.0 | 默认语速 |
| `cache_dir` | str | ./cache/tts | 缓存目录 |

#### 方法

##### `async generate(text, voice=None, speed=None) -> bytes`

生成语音。

**参数:**
- `text` (str): 要转换的文本
- `voice` (str, optional): 音色ID，覆盖默认值
- `speed` (float, optional): 语速，范围 0.5-2.0

**返回:**
- `bytes`: MP3 格式的音频数据

##### `get_voices(style=None) -> list`

获取可用音色列表。

**参数:**
- `style` (str, optional): 按风格过滤 (professional/casual/energetic)

**返回:**
- `list`: 音色信息列表

##### `estimate_duration(text, speed=1.0) -> float`

估算语音时长。

**参数:**
- `text` (str): 文本内容
- `speed` (float): 语速

**返回:**
- `float`: 预估时长（秒）

## 环境变量

```bash
# 必需
STEPFUN_API_KEY=your_api_key_here

# 可选
STEPFUN_TTS_MODEL=step-tts-mini  # 或 step-tts-2
STEPFUN_TTS_CACHE_DIR=./cache/tts
```

## 错误处理

```python
from stepfun_tts import StepFunTTS, TTSError, VoiceNotFoundError

try:
    tts = StepFunTTS(api_key="your_key")
    audio = await tts.generate("你好")
except VoiceNotFoundError:
    print("音色不存在")
except TTSError as e:
    print(f"生成失败: {e}")
```

## 许可证

MIT License
