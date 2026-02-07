"""
视频生成服务集成
支持 Replicate、Runway ML 等视频生成 API
"""

import httpx
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from enum import Enum
from app.core.config import settings
from app.core.logging import logger


class VideoProvider(Enum):
    """视频生成提供商"""
    REPLICATE = "replicate"
    RUNWAY = "runway"
    STEPFUN = "stepfun"  # 未来可能支持


class VideoGenerationService:
    """视频生成服务基类"""
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 5,
        resolution: str = "1080p",
        **kwargs
    ) -> str:
        """生成视频，返回视频URL或路径"""
        raise NotImplementedError
    
    async def image_to_video(
        self,
        image_data: bytes,
        prompt: str = "",
        duration: int = 5,
        **kwargs
    ) -> str:
        """图像生成视频"""
        raise NotImplementedError


class ReplicateService(VideoGenerationService):
    """
    Replicate API 视频生成服务
    支持多种开源视频生成模型
    """
    
    API_BASE = "https://api.replicate.com/v1"
    
    # 常用视频生成模型
    MODELS = {
        # 文生视频
        "text_to_video": {
            "wan-t2v": "wavespeedai/wan-2.1-t2v-720p",
            "cogvideo": "thudm/cogvideo",
            "ltx_video": "lightricks/ltx-video",
        },
        # 图生视频
        "image_to_video": {
            "wan-i2v": "wavespeedai/wan-2.1-i2v-720p",
            "haiper": "haiper-video",
            "runway_gen2": "runwayml/gen2",
        }
    }
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.REPLICATE_API_TOKEN
        
        if not self.api_token:
            raise ValueError("Replicate API Token not configured")
    
    async def create_prediction(
        self,
        model_version: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建预测任务"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/predictions",
                headers={
                    "Authorization": f"Token {self.api_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": model_version,
                    "input": input_data
                },
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                error_msg = f"Replicate API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data}"
                except:
                    pass
                raise Exception(error_msg)
            
            return response.json()
    
    async def get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """获取预测任务状态"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.API_BASE}/predictions/{prediction_id}",
                headers={
                    "Authorization": f"Token {self.api_token}"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get prediction: {response.status_code}")
            
            return response.json()
    
    async def wait_for_completion(
        self,
        prediction_id: str,
        max_wait: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            prediction = await self.get_prediction(prediction_id)
            status = prediction.get("status")
            
            if status == "succeeded":
                return prediction
            elif status in ["failed", "canceled"]:
                raise Exception(f"Prediction {status}: {prediction.get('error', 'Unknown error')}")
            
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait:
                raise TimeoutError(f"Prediction timeout after {max_wait}s")
            
            await asyncio.sleep(poll_interval)
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "wan-t2v",
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        negative_prompt: str = "",
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        文生视频
        
        Args:
            prompt: 视频描述
            model: 模型名称
            duration: 视频时长（秒）
            resolution: 分辨率
            aspect_ratio: 宽高比
            negative_prompt: 负面提示词
            wait_for_completion: 是否等待完成
            
        Returns:
            包含 prediction_id 和 output（如果完成）的字典
        """
        model_version = self.MODELS["text_to_video"].get(model, model)
        
        input_data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "blur, distortion, low quality",
            "num_frames": min(duration * 24, 120),  # 假设24fps，最多120帧
            "fps": 24,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio
        }
        
        prediction = await self.create_prediction(model_version, input_data)
        
        if wait_for_completion:
            result = await self.wait_for_completion(prediction["id"])
            return {
                "prediction_id": prediction["id"],
                "status": "completed",
                "video_url": result.get("output"),
                "model": model
            }
        
        return {
            "prediction_id": prediction["id"],
            "status": "processing",
            "model": model
        }
    
    async def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        model: str = "wan-i2v",
        duration: int = 5,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
        wait_for_completion: bool = True
    ) -> Dict[str, Any]:
        """
        图生视频
        
        Args:
            image_url: 输入图像URL
            prompt: 运动描述（可选）
            model: 模型名称
            duration: 视频时长
            motion_bucket_id: 运动强度 (0-255)
            noise_aug_strength: 噪声增强强度
            wait_for_completion: 是否等待完成
            
        Returns:
            包含 prediction_id 和 output 的字典
        """
        model_version = self.MODELS["image_to_video"].get(model, model)
        
        input_data = {
            "image": image_url,
            "prompt": prompt or "camera motion, dynamic scene",
            "num_frames": min(duration * 24, 120),
            "fps": 24,
            "motion_bucket_id": motion_bucket_id,
            "noise_aug_strength": noise_aug_strength
        }
        
        prediction = await self.create_prediction(model_version, input_data)
        
        if wait_for_completion:
            result = await self.wait_for_completion(prediction["id"])
            return {
                "prediction_id": prediction["id"],
                "status": "completed",
                "video_url": result.get("output"),
                "model": model
            }
        
        return {
            "prediction_id": prediction["id"],
            "status": "processing",
            "model": model
        }


class RunwayMLService(VideoGenerationService):
    """
    Runway ML API 视频生成服务
    支持 Gen-2 等高级视频生成模型
    """
    
    API_BASE = "https://api.runwayml.com/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.RUNWAY_API_KEY
        
        if not self.api_key:
            raise ValueError("Runway API Key not configured")
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 4,
        resolution: str = "1080p",
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用 Runway Gen-2/Gen-3 生成视频
        
        Args:
            prompt: 视频描述
            duration: 视频时长（秒）
            resolution: 分辨率 (720p/1080p/4k)
            
        Returns:
            包含 task_id 和 video_url 的字典
        """
        # Runway API 调用示例
        # 注意：具体实现需要根据 Runway 实际 API 文档调整
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_BASE}/text_to_video",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "duration": min(duration, 16),  # Runway通常限制16秒
                    "resolution": resolution
                },
                timeout=30.0
            )
            
            if response.status_code not in [200, 201, 202]:
                error_msg = f"Runway API error: {response.status_code}"
                raise Exception(error_msg)
            
            data = response.json()
            return {
                "task_id": data.get("id"),
                "status": "processing",
                "provider": "runway"
            }
    
    async def image_to_video(
        self,
        image_data: bytes,
        prompt: str = "",
        duration: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """图生视频"""
        # 实现与 Replicate 类似
        # 需要先将图片上传到可访问的URL
        raise NotImplementedError("Image to video with Runway requires image URL")


class VideoServiceManager:
    """视频服务管理器"""
    
    def __init__(self):
        self._services: Dict[VideoProvider, VideoGenerationService] = {}
        self._init_services()
    
    def _init_services(self):
        """初始化可用的视频服务"""
        # Replicate
        if settings.REPLICATE_API_TOKEN:
            try:
                self._services[VideoProvider.REPLICATE] = ReplicateService()
                logger.info("Replicate service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Replicate service: {e}")
        
        # Runway
        if settings.RUNWAY_API_KEY:
            try:
                self._services[VideoProvider.RUNWAY] = RunwayMLService()
                logger.info("Runway service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Runway service: {e}")
    
    def get_service(self, provider: VideoProvider) -> Optional[VideoGenerationService]:
        """获取指定提供商的服务"""
        return self._services.get(provider)
    
    def get_available_providers(self) -> List[str]:
        """获取可用的提供商列表"""
        return [p.value for p in self._services.keys()]
    
    def is_available(self, provider: VideoProvider) -> bool:
        """检查提供商是否可用"""
        return provider in self._services
    
    async def generate_video(
        self,
        prompt: str,
        provider: VideoProvider = VideoProvider.REPLICATE,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用指定提供商生成视频
        
        Args:
            prompt: 视频描述
            provider: 提供商
            **kwargs: 其他参数
            
        Returns:
            视频生成结果
        """
        service = self.get_service(provider)
        if not service:
            raise ValueError(f"Provider {provider.value} not available")
        
        return await service.generate_video(prompt, **kwargs)


# 全局服务管理器实例
video_service_manager = VideoServiceManager()


# 便捷函数
async def generate_video_from_text(
    prompt: str,
    provider: str = "replicate",
    duration: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    快速生成视频
    
    Args:
        prompt: 视频描述
        provider: 提供商 (replicate/runway)
        duration: 视频时长
        
    Returns:
        视频生成结果
    """
    provider_enum = VideoProvider(provider)
    return await video_service_manager.generate_video(
        prompt=prompt,
        provider=provider_enum,
        duration=duration,
        **kwargs
    )


async def generate_video_from_image(
    image_url: str,
    prompt: str = "",
    provider: str = "replicate",
    duration: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """
    从图像生成视频
    
    Args:
        image_url: 图像URL
        prompt: 运动描述
        provider: 提供商
        duration: 视频时长
        
    Returns:
        视频生成结果
    """
    provider_enum = VideoProvider(provider)
    service = video_service_manager.get_service(provider_enum)
    
    if not service:
        raise ValueError(f"Provider {provider} not available")
    
    return await service.image_to_video(
        image_url=image_url,
        prompt=prompt,
        duration=duration,
        **kwargs
    )
