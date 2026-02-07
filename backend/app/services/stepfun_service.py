"""
StepFun (阶跃星辰) 服务集成
用于大语言模型调用 - 视频脚本生成、文案优化等
"""

import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.core.logging import logger


class StepFunLLM:
    """阶跃星辰大语言模型服务"""
    
    API_BASE = "https://api.stepfun.com/v1"
    DEFAULT_MODEL = "step-1-8k"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.STEPFUN_API_KEY
        self.model = model or settings.STEPFUN_LLM_MODEL or self.DEFAULT_MODEL
        
        if not self.api_key:
            raise ValueError("StepFun API Key not configured")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        调用阶跃星辰对话模型
        
        Args:
            messages: 消息列表，格式 [{"role": "system"/"user"/"assistant", "content": "..."}]
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本内容
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"StepFun API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                except:
                    pass
                raise Exception(error_msg)
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_video_script(
        self,
        product_name: str,
        product_description: str,
        key_features: List[str],
        style: str = "professional",
        duration: int = 60,
        platform: str = "youtube"
    ) -> Dict[str, Any]:
        """
        生成视频脚本
        
        Args:
            product_name: 产品名称
            product_description: 产品描述
            key_features: 核心功能列表
            style: 脚本风格 (professional/casual/energetic/storytelling)
            duration: 视频时长（秒）
            platform: 目标平台 (youtube/bilibili/douyin/xiaohongshu)
            
        Returns:
            视频脚本数据结构
        """
        # 构建提示词
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
            import json
            # 清理可能的 markdown 代码块
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
            logger.error(f"Failed to generate video script: {e}")
            raise
    
    async def optimize_copywriting(
        self,
        original_text: str,
        style: str = "professional",
        max_length: int = 100
    ) -> str:
        """
        优化文案
        
        Args:
            original_text: 原始文案
            style: 风格 (professional/casual/catchy/emotional)
            max_length: 最大字数
            
        Returns:
            优化后的文案
        """
        style_descriptions = {
            "professional": "专业正式，适合商务场景",
            "casual": "轻松自然，适合社交媒体",
            "catchy": " catchy吸睛，适合广告语",
            "emotional": "情感共鸣，适合品牌故事"
        }
        
        prompt = f"""请优化以下文案，使其更{style_descriptions.get(style, '吸引人')}。

原始文案：
{original_text}

要求：
- 不超过{max_length}字
- 保持原意但更有感染力
- 直接返回优化后的文案，不要解释"""

        messages = [
            {"role": "system", "content": "你是一个资深的文案策划专家，擅长创作简洁有力的营销文案。"},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(messages, temperature=0.7)


# 便捷函数
async def generate_video_script(
    product_name: str,
    product_description: str,
    key_features: List[str],
    style: str = "professional",
    duration: int = 60,
    platform: str = "youtube"
) -> Dict[str, Any]:
    """快速生成视频脚本的便捷函数"""
    llm = StepFunLLM()
    return await llm.generate_video_script(
        product_name=product_name,
        product_description=product_description,
        key_features=key_features,
        style=style,
        duration=duration,
        platform=platform
    )


async def optimize_copywriting(text: str, style: str = "professional") -> str:
    """快速优化文案的便捷函数"""
    llm = StepFunLLM()
    return await llm.optimize_copywriting(text, style)
