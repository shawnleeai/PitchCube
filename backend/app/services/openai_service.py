"""
OpenAI 服务集成
用于文案生成、图像生成(DALL-E)、对话等
"""

import httpx
import base64
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


class OpenAIService:
    """OpenAI API 服务封装"""
    
    API_BASE = "https://api.openai.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API Key not configured")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        调用 OpenAI 对话模型
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            response_format: 响应格式，如 {"type": "json_object"}
            
        Returns:
            生成的文本内容
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            if response_format:
                payload["response_format"] = response_format
                
            response = await client.post(
                f"{self.API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                except:
                    pass
                raise Exception(error_msg)
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1
    ) -> List[bytes]:
        """
        使用 DALL-E 生成图像
        
        Args:
            prompt: 图像描述提示词
            model: 模型 (dall-e-2 或 dall-e-3)
            size: 图像尺寸
                - dall-e-2: 256x256, 512x512, 1024x1024
                - dall-e-3: 1024x1024, 1792x1024, 1024x1792
            quality: 图像质量 (standard 或 hd，仅dall-e-3)
            style: 风格 (vivid 或 natural，仅dall-e-3)
            n: 生成数量 (dall-e-2支持1-10, dall-e-3只支持1)
            
        Returns:
            图像二进制数据列表
        """
        async with httpx.AsyncClient() as client:
            payload = {
                "model": model,
                "prompt": prompt,
                "n": n,
                "size": size,
                "response_format": "b64_json"
            }
            
            # dall-e-3 特有参数
            if model == "dall-e-3":
                payload["quality"] = quality
                payload["style"] = style
            
            response = await client.post(
                f"{self.API_BASE}/images/generations",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"DALL-E API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                except:
                    pass
                raise Exception(error_msg)
            
            data = response.json()
            images = []
            for item in data["data"]:
                b64_data = item["b64_json"]
                images.append(base64.b64decode(b64_data))
            
            return images
    
    async def generate_variation(
        self,
        image_data: bytes,
        n: int = 1,
        size: str = "1024x1024"
    ) -> List[bytes]:
        """
        生成图像变体 (仅dall-e-2)
        
        Args:
            image_data: 原始图像数据
            n: 生成数量
            size: 图像尺寸
            
        Returns:
            图像二进制数据列表
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/images/variations",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                files={
                    "image": ("image.png", image_data, "image/png")
                },
                data={
                    "n": n,
                    "size": size,
                    "response_format": "b64_json"
                },
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"DALL-E Variation API error: {response.status_code}"
                raise Exception(error_msg)
            
            data = response.json()
            images = []
            for item in data["data"]:
                b64_data = item["b64_json"]
                images.append(base64.b64decode(b64_data))
            
            return images
    
    async def edit_image(
        self,
        image_data: bytes,
        prompt: str,
        mask_data: Optional[bytes] = None,
        n: int = 1,
        size: str = "1024x1024"
    ) -> List[bytes]:
        """
        编辑图像 (仅dall-e-2)
        
        Args:
            image_data: 原始图像
            prompt: 编辑提示词
            mask_data: 遮罩图像（可选）
            n: 生成数量
            size: 图像尺寸
            
        Returns:
            图像二进制数据列表
        """
        async with httpx.AsyncClient() as client:
            files = {
                "image": ("image.png", image_data, "image/png")
            }
            if mask_data:
                files["mask"] = ("mask.png", mask_data, "image/png")
            
            response = await client.post(
                f"{self.API_BASE}/images/edits",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                files=files,
                data={
                    "prompt": prompt,
                    "n": n,
                    "size": size,
                    "response_format": "b64_json"
                },
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"DALL-E Edit API error: {response.status_code}"
                raise Exception(error_msg)
            
            data = response.json()
            images = []
            for item in data["data"]:
                b64_data = item["b64_json"]
                images.append(base64.b64decode(b64_data))
            
            return images
    
    async def generate_copywriting(
        self,
        product_name: str,
        product_description: str,
        target_audience: str = "",
        style: str = "professional",
        length: str = "medium",
        language: str = "zh"
    ) -> Dict[str, str]:
        """
        生成营销文案
        
        Args:
            product_name: 产品名称
            product_description: 产品描述
            target_audience: 目标受众
            style: 风格 (professional/casual/urgent/emotional/storytelling)
            length: 长度 (short/medium/long)
            language: 语言 (zh/en)
            
        Returns:
            包含多种文案变体的字典
        """
        style_desc = {
            "professional": "专业正式，适合商务场景",
            "casual": "轻松自然，适合社交媒体",
            "urgent": "紧迫促销，适合活动推广",
            "emotional": "情感共鸣，适合品牌故事",
            "storytelling": "故事叙述，吸引注意力"
        }
        
        length_words = {
            "short": "30-50字",
            "medium": "80-120字",
            "long": "200-300字"
        }
        
        lang_prompt = "中文" if language == "zh" else "English"
        
        prompt = f"""请为以下产品生成营销文案，使用{lang_prompt}：

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
6. ad_short - 短广告文案
7. ad_long - 长广告文案

只返回JSON格式，不要有其他文字。"""

        messages = [
            {"role": "system", "content": "You are a professional copywriter specializing in marketing content."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.chat_completion(
            messages,
            response_format={"type": "json_object"}
        )
        
        import json
        try:
            return json.loads(response)
        except:
            return {"raw_response": response}
    
    async def create_chat_session(
        self,
        system_prompt: str,
        model: str = "gpt-4o-mini"
    ) -> "OpenAIChatSession":
        """创建对话会话"""
        return OpenAIChatSession(self, system_prompt, model)


class OpenAIChatSession:
    """OpenAI 对话会话（支持角色扮演）"""
    
    def __init__(
        self,
        service: OpenAIService,
        system_prompt: str,
        model: str = "gpt-4o-mini"
    ):
        self.service = service
        self.model = model
        self.messages = [{"role": "system", "content": system_prompt}]
    
    async def send_message(self, message: str) -> str:
        """发送消息并获取回复"""
        self.messages.append({"role": "user", "content": message})
        
        response = await self.service.chat_completion(
            messages=self.messages,
            model=self.model
        )
        
        self.messages.append({"role": "assistant", "content": response})
        return response
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.messages.copy()
    
    def clear_history(self):
        """清除对话历史（保留system prompt）"""
        system_msg = self.messages[0] if self.messages else {"role": "system", "content": ""}
        self.messages = [system_msg]


# 便捷函数
async def generate_image(
    prompt: str,
    model: str = "dall-e-3",
    size: str = "1024x1024"
) -> bytes:
    """快速生成图像"""
    service = OpenAIService()
    images = await service.generate_image(prompt, model=model, size=size)
    return images[0]


async def generate_copywriting(
    product_name: str,
    product_description: str,
    style: str = "professional"
) -> Dict[str, str]:
    """快速生成文案"""
    service = OpenAIService()
    return await service.generate_copywriting(
        product_name=product_name,
        product_description=product_description,
        style=style
    )


# 角色扮演预设
CHARACTER_PRESETS = {
    "sales_expert": {
        "name": "销售专家",
        "prompt": """你是一位经验丰富的销售专家，擅长：
- 挖掘客户需求和痛点
- 提供专业的销售建议
- 制定有效的销售策略
- 回答各种销售相关问题

请用专业、友好的语气与用户交流，提供具体、可执行的建议。"""
    },
    "marketing_guru": {
        "name": "营销大师",
        "prompt": """你是一位创意十足的营销大师，擅长：
- 品牌营销战略
- 社交媒体运营
- 内容营销策划
- 病毒式传播技巧

请提供有创意、接地气的营销建议，帮助用户打造爆款产品。"""
    },
    "product_manager": {
        "name": "产品经理",
        "prompt": """你是一位资深产品经理，擅长：
- 产品规划与设计
- 用户研究分析
- 需求优先级管理
- 产品路演策略

请从专业产品角度提供建议，帮助用户打造优秀的产品。"""
    },
    "investor": {
        "name": "投资人",
        "prompt": """你是一位资深风险投资家，擅长：
- 评估创业项目
- 分析商业模式
- 提供融资建议
- 指导路演技巧

请从投资人视角提供犀利、有价值的反馈和建议。"""
    },
    "storyteller": {
        "name": "故事讲述者",
        "prompt": """你是一位擅长品牌故事讲述的专家，擅长：
- 挖掘品牌独特故事
- 创作感人的叙事内容
- 打造品牌人格
- 用故事打动听众

请帮助用户用故事的力量传递品牌价值。"""
    }
}


async def create_character_chat(
    character: str,
    custom_prompt: Optional[str] = None
) -> OpenAIChatSession:
    """
    创建角色扮演对话
    
    Args:
        character: 角色预设名称 或 "custom"
        custom_prompt: 自定义角色prompt（当character为custom时使用）
    """
    service = OpenAIService()
    
    if character == "custom" and custom_prompt:
        prompt = custom_prompt
    else:
        preset = CHARACTER_PRESETS.get(character, CHARACTER_PRESETS["sales_expert"])
        prompt = preset["prompt"]
    
    return await service.create_chat_session(prompt)
