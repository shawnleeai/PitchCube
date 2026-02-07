"""
StepFun TTS Skill - 阶跃星辰语音合成服务
"""

import os
import hashlib
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass
class Voice:
    """音色信息"""
    id: str
    name: str
    gender: str
    style: str
    description: str
    tags: List[str]


class TTSError(Exception):
    """TTS 错误基类"""
    pass


class VoiceNotFoundError(TTSError):
    """音色不存在错误"""
    pass


class APIError(TTSError):
    """API 调用错误"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


# 预设音色库
VOICE_LIBRARY: List[Voice] = [
    # 专业风格
    Voice("zhengpaiqingnian", "正派青年", "male", "professional", 
          "适合商务路演、专业解说", ["专业", "稳重", "商务"]),
    Voice("ganliannvsheng", "干练女声", "female", "professional",
          "专业干练，适合正式场合", ["专业", "干练", "正式"]),
    Voice("cixingnansheng", "磁性男声", "male", "professional",
          "低沉磁性，适合品牌宣传", ["磁性", "低沉", "品牌"]),
    Voice("ruyananshi", "儒雅男士", "male", "professional",
          "儒雅稳重，适合文化内容", ["儒雅", "文化", "稳重"]),
    
    # 亲切风格
    Voice("linjiajiejie", "邻家姐姐", "female", "casual",
          "亲切自然，适合轻松场景", ["亲切", "自然", "轻松"]),
    Voice("wenrounansheng", "温柔男声", "male", "casual",
          "温柔体贴，适合情感内容", ["温柔", "情感", "治愈"]),
    Voice("qinhenvsheng", "亲和女声", "female", "casual",
          "亲和力强，适合客服场景", ["亲和", "客服", "友好"]),
    Voice("wenrougongzi", "温柔公子", "male", "casual",
          "温柔儒雅，适合故事讲述", ["温柔", "故事", "讲述"]),
    
    # 活力风格
    Voice("yuanqishaonv", "元气少女", "female", "energetic",
          "活力四射，适合年轻产品", ["活力", "年轻", "可爱"]),
    Voice("yuanqinansheng", "元气男声", "male", "energetic",
          "元气满满，适合活泼内容", ["活力", "阳光", "积极"]),
    Voice("huolinvsheng", "活力女声", "female", "energetic",
          "活力热情，适合营销场景", ["活力", "营销", "热情"]),
    Voice("zhengpaiqingnian", "正派青年", "male", "energetic",
          "正派阳光，适合激励内容", ["阳光", "积极", "激励"]),
    
    # 特色风格
    Voice("tianmeinvsheng", "甜美女声", "female", "sweet",
          "甜美动听，适合时尚美妆", ["甜美", "时尚", "美妆"]),
    Voice("qingchunshaonv", "清纯少女", "female", "youth",
          "清纯可爱，适合二次元", ["清纯", "可爱", "二次元"]),
    Voice("shenchennanyin", "深沉男音", "male", "deep",
          "深沉磁性，适合纪录片", ["深沉", "磁性", "纪录"]),
    Voice("boyinnansheng", "播音男声", "male", "broadcast",
          "标准播音腔，适合新闻播报", ["播音", "标准", "新闻"]),
]


class StepFunTTS:
    """
    阶跃星辰语音合成服务
    
    使用示例:
        >>> tts = StepFunTTS(api_key="your_key")
        >>> audio = await tts.generate("你好世界", voice="zhengpaiqingnian")
        >>> with open("output.mp3", "wb") as f:
        ...     f.write(audio)
    """
    
    API_BASE = "https://api.stepfun.com/v1"
    DEFAULT_MODEL = "step-tts-mini"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_voice: str = "zhengpaiqingnian",
        default_speed: float = 1.0,
        cache_dir: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        初始化 StepFun TTS 服务
        
        Args:
            api_key: 阶跃星辰 API Key，默认从环境变量 STEPFUN_API_KEY 读取
            base_url: API 基础地址
            default_voice: 默认音色ID
            default_speed: 默认语速 (0.5-2.0)
            cache_dir: 缓存目录，None 表示不缓存
            model: 使用的模型，默认 step-tts-mini
            timeout: API 调用超时时间
        """
        self.api_key = api_key or os.getenv("STEPFUN_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set STEPFUN_API_KEY env var or pass api_key parameter.")
        
        self.base_url = base_url or self.API_BASE
        self.default_voice = default_voice
        self.default_speed = max(0.5, min(2.0, default_speed))
        self.model = model or os.getenv("STEPFUN_TTS_MODEL", self.DEFAULT_MODEL)
        self.timeout = timeout
        
        # 设置缓存
        self.cache_dir = None
        if cache_dir is not False:
            self.cache_dir = Path(cache_dir or os.getenv("STEPFUN_TTS_CACHE_DIR", "./cache/tts"))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 验证默认音色
        if not self._get_voice_by_id(self.default_voice):
            raise VoiceNotFoundError(f"Default voice '{default_voice}' not found")
    
    def _get_voice_by_id(self, voice_id: str) -> Optional[Voice]:
        """根据ID获取音色"""
        for voice in VOICE_LIBRARY:
            if voice.id == voice_id:
                return voice
        return None
    
    def _get_cache_path(self, text: str, voice: str, speed: float) -> Optional[Path]:
        """获取缓存文件路径"""
        if not self.cache_dir:
            return None
        
        # 生成缓存key
        content = f"{text}|{voice}|{speed}|{self.model}"
        cache_key = hashlib.md5(content.encode()).hexdigest()
        return self.cache_dir / f"{cache_key}.mp3"
    
    async def generate(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        use_cache: bool = True
    ) -> bytes:
        """
        生成语音
        
        Args:
            text: 要转换的文本（建议不超过500字）
            voice: 音色ID，默认使用初始化设置的 default_voice
            speed: 语速，范围 0.5-2.0，默认 1.0
            use_cache: 是否使用缓存
            
        Returns:
            MP3 格式的音频数据
            
        Raises:
            VoiceNotFoundError: 音色不存在
            APIError: API 调用失败
            ValueError: 参数错误
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 2000:
            raise ValueError("Text too long (max 2000 characters)")
        
        # 使用默认参数
        voice_id = voice or self.default_voice
        voice_speed = speed if speed is not None else self.default_speed
        voice_speed = max(0.5, min(2.0, voice_speed))
        
        # 验证音色
        if not self._get_voice_by_id(voice_id):
            raise VoiceNotFoundError(f"Voice '{voice_id}' not found. Use get_voices() to list available voices.")
        
        # 检查缓存
        if use_cache and self.cache_dir:
            cache_path = self._get_cache_path(text, voice_id, voice_speed)
            if cache_path and cache_path.exists():
                return cache_path.read_bytes()
        
        # 调用API生成
        try:
            audio_data = await self._call_api(text, voice_id, voice_speed)
            
            # 保存缓存
            if use_cache and self.cache_dir:
                cache_path = self._get_cache_path(text, voice_id, voice_speed)
                if cache_path:
                    cache_path.write_bytes(audio_data)
            
            return audio_data
            
        except httpx.HTTPError as e:
            raise APIError(f"API request failed: {str(e)}", getattr(e.response, 'status_code', None))
        except Exception as e:
            raise TTSError(f"Generation failed: {str(e)}")
    
    async def _call_api(self, text: str, voice: str, speed: float) -> bytes:
        """调用阶跃星辰 API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text.strip(),
                    "voice": voice,
                    "speed": speed
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = f"{error_msg} - {error_data.get('error', {}).get('message', 'Unknown error')}"
                except:
                    pass
                raise APIError(error_msg, response.status_code)
            
            return response.content
    
    def get_voices(
        self,
        style: Optional[str] = None,
        gender: Optional[str] = None
    ) -> List[Voice]:
        """
        获取可用音色列表
        
        Args:
            style: 按风格过滤 (professional/casual/energetic/sweet/youth/deep/broadcast)
            gender: 按性别过滤 (male/female)
            
        Returns:
            符合条件的音色列表
        """
        voices = VOICE_LIBRARY
        
        if style:
            voices = [v for v in voices if v.style == style]
        
        if gender:
            voices = [v for v in voices if v.gender == gender]
        
        return voices
    
    def get_voice_by_style(self, style: str, gender: Optional[str] = None) -> Optional[Voice]:
        """
        根据风格获取推荐音色
        
        Args:
            style: 风格 (professional/casual/energetic)
            gender: 性别偏好
            
        Returns:
            推荐的音色
        """
        voices = self.get_voices(style=style, gender=gender)
        return voices[0] if voices else None
    
    @staticmethod
    def estimate_duration(text: str, speed: float = 1.0) -> float:
        """
        估算语音时长
        
        中文语速约 240-280 字/分钟
        
        Args:
            text: 文本内容
            speed: 语速倍率
            
        Returns:
            预估时长（秒）
        """
        if not text:
            return 0.0
        
        # 中文字符计数
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        # 英文单词计数（简化处理）
        english_words = len([w for w in text.split() if w.isascii()])
        
        # 中文 4 字符/秒，英文 2 单词/秒（正常语速）
        base_duration = (chinese_chars / 4) + (english_words / 2)
        
        # 根据语速调整
        return base_duration / speed
    
    async def generate_with_breaks(
        self,
        segments: List[Dict[str, Any]],
        pause_duration: float = 0.5
    ) -> bytes:
        """
        生成带停顿的多段语音
        
        Args:
            segments: 段落列表，每个段落包含 text, voice, speed
            pause_duration: 段落间停顿时长（秒）
            
        Returns:
            合并后的音频数据
        """
        from io import BytesIO
        
        audio_parts = []
        
        for segment in segments:
            text = segment.get("text", "")
            voice = segment.get("voice", self.default_voice)
            speed = segment.get("speed", self.default_speed)
            
            if not text.strip():
                continue
            
            audio = await self.generate(text, voice=voice, speed=speed)
            audio_parts.append(audio)
        
        # 简单合并（实际应用中可能需要使用音频处理库）
        return b"".join(audio_parts)
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache_dir and self.cache_dir.exists():
            for file in self.cache_dir.glob("*.mp3"):
                file.unlink()


# 便捷函数
async def generate_speech(
    text: str,
    voice: str = "zhengpaiqingnian",
    speed: float = 1.0,
    api_key: Optional[str] = None
) -> bytes:
    """
    快速生成语音的便捷函数
    
    Args:
        text: 文本内容
        voice: 音色ID
        speed: 语速
        api_key: API Key，默认从环境变量读取
        
    Returns:
        音频数据
    """
    tts = StepFunTTS(api_key=api_key)
    return await tts.generate(text, voice=voice, speed=speed)


def get_voice_recommendations(scenario: str) -> List[Voice]:
    """
    根据场景获取音色推荐
    
    Args:
        scenario: 场景名称
            - "business": 商务路演
            - "product": 产品介绍
            - "marketing": 营销宣传
            - "story": 故事讲述
            - "news": 新闻播报
            - "casual": 轻松休闲
            
    Returns:
        推荐的音色列表
    """
    recommendations = {
        "business": ["zhengpaiqingnian", "ganliannvsheng", "cixingnansheng"],
        "product": ["linjiajiejie", "wenrounansheng", "zhengpaiqingnian"],
        "marketing": ["huolinvsheng", "yuanqishaonv", "yuanqinansheng"],
        "story": ["ruyananshi", "wenrougongzi", "qingchunshaonv"],
        "news": ["boyinnansheng", "ganliannvsheng", "zhengpaiqingnian"],
        "casual": ["linjiajiejie", "wenrounansheng", "qinhenvsheng"],
    }
    
    voice_ids = recommendations.get(scenario, ["zhengpaiqingnian"])
    return [v for v in VOICE_LIBRARY if v.id in voice_ids]
