"""
Stability AI 服务集成
用于海报图像生成和增强
"""

import httpx
import base64
from typing import Optional, List
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


class StabilityAI:
    """Stability AI 图像生成服务"""
    
    API_BASE = "https://api.stability.ai/v2beta"
    DEFAULT_MODEL = "stable-image-ultra"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.STABILITY_API_KEY
        
        if not self.api_key:
            raise ValueError("Stability API Key not configured")
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        aspect_ratio: str = "3:4",
        output_format: str = "png"
    ) -> bytes:
        """
        生成图像
        
        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            aspect_ratio: 宽高比 (16:9, 1:1, 3:4, etc.)
            output_format: 输出格式 (png, jpeg, webp)
            
        Returns:
            图像二进制数据
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/stable-image/generate/ultra",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "image/*"
                },
                data={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                error_msg = f"Stability API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('errors', [''])[0]}"
                except:
                    pass
                raise Exception(error_msg)
            
            return response.content
    
    async def upscale_image(
        self,
        image_data: bytes,
        prompt: Optional[str] = None
    ) -> bytes:
        """
        图像超分辨率放大
        
        Args:
            image_data: 原始图像数据
            prompt: 可选的提示词来指导放大
            
        Returns:
            放大后的图像数据
        """
        async with httpx.AsyncClient() as client:
            files = {
                "image": ("image.png", image_data, "image/png")
            }
            data = {}
            if prompt:
                data["prompt"] = prompt
            
            response = await client.post(
                f"{self.API_BASE}/stable-image/upscale/conservative",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "image/*"
                },
                files=files,
                data=data,
                timeout=120.0
            )
            
            if response.status_code != 200:
                error_msg = f"Stability Upscale API error: {response.status_code}"
                raise Exception(error_msg)
            
            return response.content
    
    async def enhance_poster(
        self,
        product_name: str,
        description: str,
        style: str = "modern tech",
        color_scheme: Optional[str] = None
    ) -> bytes:
        """
        为产品生成增强版海报背景
        
        Args:
            product_name: 产品名称
            description: 产品描述
            style: 风格 (modern tech, minimalist, vibrant, professional, etc.)
            color_scheme: 配色方案描述
            
        Returns:
            海报背景图像数据
        """
        # 构建提示词
        color_text = f" with {color_scheme} color scheme" if color_scheme else ""
        
        prompt = f"""Professional marketing poster background for "{product_name}".
Style: {style}{color_text}.
Product concept: {description}

Requirements:
- Clean, modern design suitable for tech startup pitch deck
- Abstract geometric shapes or subtle tech patterns
- Space for text overlay in center and top areas
- High contrast but not overwhelming
- Professional business aesthetic
- 1200x1600 pixels composition
- No text, no watermarks, no logos
- Gradient lighting effects
- Suitable for SaaS product marketing"""

        negative_prompt = "text, watermark, logo, signature, blurry, low quality, distorted, deformed"
        
        return await self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio="3:4",
            output_format="png"
        )
    
    async def generate_background_variations(
        self,
        base_description: str,
        num_variations: int = 3
    ) -> List[bytes]:
        """
        生成多个背景变体
        
        Args:
            base_description: 基础描述
            num_variations: 变体数量
            
        Returns:
            图像数据列表
        """
        variations = []
        styles = ["modern tech", "minimalist gradient", "vibrant creative"]
        
        for i in range(min(num_variations, len(styles))):
            try:
                image_data = await self.enhance_poster(
                    product_name=base_description,
                    description=base_description,
                    style=styles[i]
                )
                variations.append(image_data)
            except Exception as e:
                logger.error(f"Failed to generate variation {i+1}: {e}")
        
        return variations


# 便捷函数
async def enhance_poster_background(
    product_name: str,
    description: str,
    style: str = "modern tech"
) -> bytes:
    """快速生成海报背景的便捷函数"""
    stability = StabilityAI()
    return await stability.enhance_poster(product_name, description, style)


async def upscale_poster(image_path: str, output_path: Optional[str] = None) -> str:
    """放大海报图像"""
    stability = StabilityAI()
    
    image_data = Path(image_path).read_bytes()
    upscaled_data = await stability.upscale_image(image_data)
    
    if output_path:
        Path(output_path).write_bytes(upscaled_data)
        return output_path
    else:
        # 返回临时路径
        temp_path = image_path.replace(".", "_upscaled.")
        Path(temp_path).write_bytes(upscaled_data)
        return temp_path
