"""
Minimax (稀宇科技) 服务集成
用于大语言模型调用和语音合成
官网: https://www.minimaxi.com/
"""

import httpx
import base64
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


class MinimaxLLM:
    """
    Minimax 大语言模型服务
    支持 abab6.5, abab6, abab5.5 等模型
    """
    
    API_BASE = "https://api.minimaxi.com/v1"
    DEFAULT_MODEL = "abab6.5s-chat"
    
    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.group_id = group_id or settings.MINIMAX_GROUP_ID
        self.model = model or settings.MINIMAX_LLM_MODEL or self.DEFAULT_MODEL
        
        if not self.api_key:
            raise ValueError("Minimax API Key not configured")
        if not self.group_id:
            raise ValueError("Minimax Group ID not configured")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False,
        **kwargs
    ) -> str:
        """
        调用 Minimax 对话模型
        
        Args:
            messages: 消息列表
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成token数
            stream: 是否流式返回
            **kwargs: 其他参数
            
        Returns:
            生成的文本内容
        """
        url = f"{self.API_BASE}/text/chatcompletion_v2"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"Minimax API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    pass
                raise Exception(error_msg)
            
            data = response.json()
            
            if data.get("base_resp", {}).get("status_code") != 0:
                error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                raise Exception(f"Minimax API error: {error_msg}")
            
            # 提取生成的文本
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
    
    async def generate_video_script(
        self,
        product_name: str,
        product_description: str,
        key_features: List[str],
        style: str = "professional",
        duration: int = 60,
        platform: str = "youtube"
    ) -> Dict[str, Any]:
        """生成视频脚本"""
        style_prompts = {
            "professional": "专业商务风格，语气正式、有说服力，适合投资人路演",
            "casual": "轻松亲切风格，语气自然、易懂，适合产品推广",
            "energetic": "活力激情风格，节奏快、感染力强，适合营销视频",
            "storytelling": "故事叙述风格，有情感共鸣，适合品牌故事"
        }
        
        platform_requirements = {
            "youtube": "适合国际观众，可以稍长，注重产品细节",
            "bilibili": "适合年轻用户，可以加入一些网络流行语和梗",
            "douyin": "短视频平台，节奏快，前3秒必须抓人眼球",
            "xiaohongshu": "生活方式平台，注重美感和使用场景"
        }
        
        features_text = "\n".join([f"- {f}" for f in key_features])
        
        prompt = f"""请为以下产品生成一个{duration}秒的视频脚本。

产品信息：
- 名称：{product_name}
- 描述：{product_description}
- 核心功能：
{features_text}

要求：
- 风格：{style_prompts.get(style, style_prompts['professional'])}
- 目标平台：{platform}（{platform_requirements.get(platform, '通用平台')}）
- 时长：{duration}秒
- 场景数：{max(3, duration // 20)}个场景

请按以下JSON格式返回（只返回JSON，不要有其他文字）：
{{
    "title": "视频标题",
    "scenes": [
        {{
            "scene_number": 1,
            "duration": 20,
            "visual_description": "画面描述：场景、动作、视觉效果",
            "narration": "旁白文案",
            "subtitle": "字幕文字（简短）"
        }}
    ],
    "background_music_suggestion": "背景音乐建议"
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的视频脚本创作专家，擅长为科技产品创作吸引人的路演视频脚本。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.8)
            
            # 解析 JSON 响应
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            script_data = json.loads(response)
            script_data["target_platform"] = platform
            script_data["total_duration"] = duration
            
            return script_data
            
        except Exception as e:
            logger.error(f"Failed to generate video script with Minimax: {e}")
            raise
    
    async def generate_copywriting(
        self,
        product_name: str,
        product_description: str,
        target_audience: str = "",
        style: str = "professional",
        length: str = "medium"
    ) -> Dict[str, str]:
        """生成营销文案"""
        style_desc = {
            "professional": "专业正式，适合商务场景",
            "casual": "轻松自然，适合社交媒体",
            "urgent": "紧迫促销，适合活动推广",
            "emotional": "情感共鸣，适合品牌故事"
        }
        
        length_words = {
            "short": "30-50字",
            "medium": "80-120字",
            "long": "200-300字"
        }
        
        prompt = f"""请为以下产品生成营销文案：

产品名称：{product_name}
产品描述：{product_description}
目标受众：{target_audience}
风格：{style_desc.get(style, style)}
长度：{length_words.get(length, '80-120字')}

请生成以下类型的文案（JSON格式）：
1. headline - 主标题（简短有力）
2. subheadline - 副标题（补充说明）
3. description - 产品描述
4. cta - 行动号召按钮文字
5. social - 社交媒体短文案

只返回JSON格式，不要有其他文字。"""

        messages = [
            {"role": "system", "content": "你是一个资深的文案策划专家，擅长创作简洁有力的营销文案。"},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(messages, temperature=0.7)
        
        try:
            return json.loads(response)
        except:
            return {"content": response}


class MinimaxTTS:
    """
    Minimax 语音合成服务 (T2A)
    支持多种中文音色
    """
    
    API_BASE = "https://api.minimaxi.com/v1"
    DEFAULT_MODEL = "speech-01-turbo"
    
    # Minimax 音色库
    VOICE_LIBRARY = [
        {"id": "male-qn-qingse", "name": "青涩青年", "gender": "male", "style": "youth", "description": "青涩自然的男声"},
        {"id": "male-qn-jingying", "name": "精英男士", "gender": "male", "style": "professional", "description": "专业稳重的男声"},
        {"id": "male-qn-badao", "name": "霸道总裁", "gender": "male", "style": "authoritative", "description": "霸气有磁性的男声"},
        {"id": "male-qn-daxuesheng", "name": "阳光大学生", "gender": "male", "style": "youth", "description": "阳光活力的男声"},
        {"id": "female-shaonv", "name": "少女", "gender": "female", "style": "youth", "description": "甜美可爱的女声"},
        {"id": "female-yujie", "name": "御姐", "gender": "female", "style": "mature", "description": "成熟魅力的女声"},
        {"id": "female-chengshu", "name": "成熟女性", "gender": "female", "style": "professional", "description": "知性专业的女声"},
        {"id": "female-tianmei", "name": "甜美女孩", "gender": "female", "style": "sweet", "description": "甜美温柔的女声"},
        {"id": "presenter_male", "name": "男主持人", "gender": "male", "style": "broadcast", "description": "标准主持腔男声"},
        {"id": "presenter_female", "name": "女主持人", "gender": "female", "style": "broadcast", "description": "标准主持腔女声"},
        {"id": "audiobook_male_1", "name": "有声书男声1", "gender": "male", "style": "story", "description": "适合讲故事的男声"},
        {"id": "audiobook_male_2", "name": "有声书男声2", "gender": "male", "style": "story", "description": "低沉磁性的男声"},
        {"id": "audiobook_female_1", "name": "有声书女声1", "gender": "female", "style": "story", "description": "温柔讲故事的女声"},
        {"id": "audiobook_female_2", "name": "有声书女声2", "gender": "female", "style": "story", "description": "清亮动人的女声"},
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        group_id: Optional[str] = None,
        model: Optional[str] = None,
        default_voice: str = "presenter_male",
        default_speed: float = 1.0
    ):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.group_id = group_id or settings.MINIMAX_GROUP_ID
        self.model = model or settings.MINIMAX_TTS_MODEL or self.DEFAULT_MODEL
        self.default_voice = default_voice
        self.default_speed = max(0.5, min(2.0, default_speed))
        
        if not self.api_key:
            raise ValueError("Minimax API Key not configured")
        if not self.group_id:
            raise ValueError("Minimax Group ID not configured")
    
    def get_voices(
        self,
        style: Optional[str] = None,
        gender: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取可用音色列表
        
        Args:
            style: 风格过滤 (youth/professional/mature/sweet/broadcast/story)
            gender: 性别过滤 (male/female)
        """
        voices = self.VOICE_LIBRARY
        
        if style:
            voices = [v for v in voices if v["style"] == style]
        
        if gender:
            voices = [v for v in voices if v["gender"] == gender]
        
        return voices
    
    def get_voice_by_id(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取音色"""
        for voice in self.VOICE_LIBRARY:
            if voice["id"] == voice_id:
                return voice
        return None
    
    async def generate(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        volume: float = 1.0,
        pitch: float = 0.0
    ) -> bytes:
        """
        生成语音
        
        Args:
            text: 要转换的文本（最长 8000 字符）
            voice: 音色ID
            speed: 语速 (0.5-2.0)
            volume: 音量 (0-10)
            pitch: 音调 (-12 到 12)
            
        Returns:
            MP3 格式的音频数据
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > 8000:
            raise ValueError("Text too long (max 8000 characters)")
        
        voice_id = voice or self.default_voice
        voice_speed = speed if speed is not None else self.default_speed
        voice_speed = max(0.5, min(2.0, voice_speed))
        
        # 验证音色
        if not self.get_voice_by_id(voice_id):
            available = [v["id"] for v in self.VOICE_LIBRARY[:5]]
            raise ValueError(f"Voice '{voice_id}' not found. Available: {available}")
        
        url = f"{self.API_BASE}/text_to_speech"
        
        payload = {
            "model": self.model,
            "text": text.strip(),
            "voice_setting": {
                "voice_id": voice_id,
                "speed": voice_speed,
                "vol": volume,
                "pitch": pitch
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"Minimax TTS error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    pass
                raise Exception(error_msg)
            
            data = response.json()
            
            if data.get("base_resp", {}).get("status_code") != 0:
                error_msg = data.get("base_resp", {}).get("status_msg", "Unknown error")
                raise Exception(f"Minimax TTS error: {error_msg}")
            
            # 解码音频数据
            audio_hex = data.get("data", {}).get("audio", "")
            if audio_hex:
                return bytes.fromhex(audio_hex)
            
            raise Exception("No audio data in response")
    
    @staticmethod
    def estimate_duration(text: str, speed: float = 1.0) -> float:
        """
        估算语音时长
        
        中文语速约 240-280 字/分钟
        """
        if not text:
            return 0.0
        
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len([w for w in text.split() if w.isascii()])
        
        base_duration = (chinese_chars / 4) + (english_words / 2)
        return base_duration / speed


class MinimaxService:
    """
    Minimax 统一服务入口
    同时提供 LLM 和 TTS 功能
    """
    
    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.group_id = group_id or settings.MINIMAX_GROUP_ID
        
        self.llm = None
        self.tts = None
        
        if self.api_key and self.group_id:
            try:
                self.llm = MinimaxLLM(self.api_key, self.group_id)
                self.tts = MinimaxTTS(self.api_key, self.group_id)
            except Exception as e:
                logger.error(f"Failed to initialize Minimax service: {e}")
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return self.llm is not None and self.tts is not None


# 便捷函数
async def minimax_generate_speech(
    text: str,
    voice: str = "presenter_male",
    speed: float = 1.0,
    api_key: Optional[str] = None,
    group_id: Optional[str] = None
) -> bytes:
    """快速生成语音的便捷函数"""
    tts = MinimaxTTS(api_key=api_key, group_id=group_id)
    return await tts.generate(text, voice=voice, speed=speed)
