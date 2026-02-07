"""
统一的 AI 服务管理器
整合所有 AI 服务，提供统一的接口和管理功能
"""

from typing import Optional, Dict, Any, List
from enum import Enum

from app.core.config import settings
from app.core.logging import logger

# 导入各个服务
from app.services.openai_service import OpenAIService
from app.services.stability_service import StabilityAI
from app.services.stepfun_service import StepFunLLM
from app.services.minimax_service import MinimaxLLM, MinimaxTTS, MinimaxService
from app.services.video_generation_service import video_service_manager, VideoProvider
from app.services.ai_roleplay_service import ai_roleplay_service
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "skills" / "stepfun-tts"))
try:
    from stepfun_tts import StepFunTTS

    STEPFUN_TTS_AVAILABLE = True
except ImportError:
    STEPFUN_TTS_AVAILABLE = False


class AIServiceType(Enum):
    """AI 服务类型"""

    TEXT_GENERATION = "text_generation"  # 文本生成
    IMAGE_GENERATION = "image_generation"  # 图像生成
    VIDEO_GENERATION = "video_generation"  # 视频生成
    VOICE_SYNTHESIS = "voice_synthesis"  # 语音合成
    ROLEPLAY_CHAT = "roleplay_chat"  # 角色扮演对话


class AIServiceStatus:
    """AI 服务状态"""

    def __init__(self):
        self.openai = False
        self.stability = False
        self.stepfun = False
        self.minimax = False
        self.replicate = False
        self.runway = False
        self.azure_speech = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "openai": {
                "configured": self.openai,
                "services": ["text_generation", "image_generation", "chat", "roleplay"],
            },
            "stability": {
                "configured": self.stability,
                "services": ["image_generation", "image_enhancement"],
            },
            "stepfun": {
                "configured": self.stepfun,
                "services": ["text_generation", "voice_synthesis"],
            },
            "minimax": {
                "configured": self.minimax,
                "services": ["text_generation", "voice_synthesis"],
            },
            "replicate": {
                "configured": self.replicate,
                "services": ["video_generation"],
            },
            "runway": {"configured": self.runway, "services": ["video_generation"]},
            "azure_speech": {
                "configured": self.azure_speech,
                "services": ["voice_synthesis"],
            },
        }


class AIServiceManager:
    """
    统一的 AI 服务管理器

    提供：
    1. 服务状态检查
    2. 统一的 API 调用接口
    3. 服务切换和降级
    4. 使用统计和监控
    """

    def __init__(self):
        self.status = AIServiceStatus()
        self._services: Dict[str, Any] = {}
        self._check_services()

    def _check_services(self):
        """检查所有 AI 服务的配置状态"""
        # OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self._services["openai"] = OpenAIService()
                self.status.openai = True
                logger.info("OK: OpenAI service available")
            except Exception as e:
                logger.warning(f"ERROR: OpenAI service error: {e}")

        # Stability AI
        if settings.STABILITY_API_KEY:
            try:
                self._services["stability"] = StabilityAI()
                self.status.stability = True
                logger.info("OK: Stability AI service available")
            except Exception as e:
                logger.warning(f"ERROR: Stability AI service error: {e}")

        # StepFun
        if settings.STEPFUN_API_KEY:
            try:
                self._services["stepfun"] = StepFunLLM()
                self.status.stepfun = True
                logger.info("OK: StepFun service available")
            except Exception as e:
                logger.warning(f"ERROR: StepFun service error: {e}")

        # Minimax
        if settings.MINIMAX_API_KEY and settings.MINIMAX_GROUP_ID:
            try:
                minimax_service = MinimaxService()
                if minimax_service.is_configured():
                    self._services["minimax_llm"] = minimax_service.llm
                    self._services["minimax_tts"] = minimax_service.tts
                    self.status.minimax = True
                    logger.info("OK: Minimax service available")
            except Exception as e:
                logger.warning(f"ERROR: Minimax service error: {e}")

        # Replicate
        if settings.REPLICATE_API_TOKEN:
            self.status.replicate = True
            logger.info("OK: Replicate service available")

        # Runway
        if settings.RUNWAY_API_KEY:
            self.status.runway = True
            logger.info("OK: Runway service available")

        # Azure Speech
        if settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION:
            self.status.azure_speech = True
            logger.info("OK: Azure Speech service available")

    def get_status(self) -> AIServiceStatus:
        """获取服务状态"""
        return self.status

    def is_service_available(self, service_name: str) -> bool:
        """检查特定服务是否可用"""
        return getattr(self.status, service_name, False)

    def get_available_services(self) -> List[str]:
        """获取所有可用的服务列表"""
        available = []
        if self.status.openai:
            available.append("openai")
        if self.status.stability:
            available.append("stability")
        if self.status.stepfun:
            available.append("stepfun")
        if self.status.minimax:
            available.append("minimax")
        if self.status.replicate:
            available.append("replicate")
        if self.status.runway:
            available.append("runway")
        if self.status.azure_speech:
            available.append("azure_speech")
        return available

    # ============== 文本生成服务 ==============

    async def generate_text(self, prompt: str, provider: str = "auto", **kwargs) -> str:
        """
        生成文本

        Args:
            prompt: 提示词
            provider: 提供商 (openai/stepfun/minimax/auto)
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        if provider == "auto":
            # 优先使用国产服务（StepFun/Minimax），其次 OpenAI
            if self.status.stepfun:
                provider = "stepfun"
            elif self.status.minimax:
                provider = "minimax"
            elif self.status.openai:
                provider = "openai"
            else:
                raise ValueError("No text generation service available")

        if provider == "openai" and self.status.openai:
            service = self._services["openai"]
            messages = [{"role": "user", "content": prompt}]
            return await service.chat_completion(messages, **kwargs)

        elif provider == "stepfun" and self.status.stepfun:
            service = self._services["stepfun"]
            messages = [{"role": "user", "content": prompt}]
            return await service.chat_completion(messages, **kwargs)

        elif provider == "minimax" and self.status.minimax:
            service = self._services["minimax_llm"]
            messages = [{"role": "user", "content": prompt}]
            return await service.chat_completion(messages, **kwargs)

        else:
            raise ValueError(f"Provider {provider} not available")

    async def generate_copywriting(
        self,
        product_name: str,
        product_description: str,
        style: str = "professional",
        language: str = "zh",
        provider: str = "auto",
    ) -> Dict[str, str]:
        """
        生成营销文案

        Args:
            product_name: 产品名称
            product_description: 产品描述
            style: 风格
            language: 语言
            provider: 提供商 (openai/stepfun/minimax/auto)

        Returns:
            文案字典
        """
        if provider == "auto":
            if self.status.openai:
                provider = "openai"
            elif self.status.stepfun:
                provider = "stepfun"
            elif self.status.minimax:
                provider = "minimax"

        if provider == "openai" and self.status.openai:
            service = self._services["openai"]
            return await service.generate_copywriting(
                product_name=product_name,
                product_description=product_description,
                style=style,
                language=language,
            )
        elif provider == "stepfun" and self.status.stepfun:
            # 使用 StepFun 生成
            service = self._services["stepfun"]
            prompt = f"""请为产品"{product_name}"生成营销文案。
产品描述：{product_description}
风格：{style}
语言：{"中文" if language == "zh" else "English"}

请生成：1.主标题 2.副标题 3.产品描述 4.行动号召"""

            messages = [
                {"role": "system", "content": "你是一位资深文案策划专家。"},
                {"role": "user", "content": prompt},
            ]
            response = await service.chat_completion(messages)
            return {"content": response}
        elif provider == "minimax" and self.status.minimax:
            # 使用 Minimax 生成
            service = self._services["minimax_llm"]
            return await service.generate_copywriting(
                product_name=product_name,
                product_description=product_description,
                target_audience="",
                style=style,
                length="medium",
            )
        else:
            raise ValueError("No text generation service available")

    # ============== 图像生成服务 ==============

    async def generate_image(
        self, prompt: str, provider: str = "auto", **kwargs
    ) -> bytes:
        """
        生成图像

        Args:
            prompt: 图像描述
            provider: 提供商 (openai/stability/auto)
            **kwargs: 其他参数

        Returns:
            图像二进制数据
        """
        if provider == "auto":
            # 优先使用 OpenAI (DALL-E)，其次 Stability
            if self.status.openai:
                provider = "openai"
            elif self.status.stability:
                provider = "stability"
            else:
                raise ValueError("No image generation service available")

        if provider == "openai" and self.status.openai:
            service = self._services["openai"]
            images = await service.generate_image(prompt, **kwargs)
            return images[0]

        elif provider == "stability" and self.status.stability:
            service = self._services["stability"]
            return await service.generate_image(prompt, **kwargs)

        else:
            raise ValueError(f"Provider {provider} not available")

    async def enhance_poster(
        self, product_name: str, description: str, style: str = "modern tech"
    ) -> bytes:
        """
        增强海报背景

        Args:
            product_name: 产品名称
            description: 产品描述
            style: 风格

        Returns:
            海报图像数据
        """
        if self.status.stability:
            service = self._services["stability"]
            return await service.enhance_poster(product_name, description, style)
        else:
            raise ValueError(
                "Stability AI service not available for poster enhancement"
            )

    # ============== 视频生成服务 ==============

    async def generate_video(
        self, prompt: str, provider: str = "replicate", **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频

        Args:
            prompt: 视频描述
            provider: 提供商 (replicate/runway)
            **kwargs: 其他参数

        Returns:
            视频生成结果
        """
        provider_enum = VideoProvider(provider)
        return await video_service_manager.generate_video(
            prompt=prompt, provider=provider_enum, **kwargs
        )

    # ============== 角色扮演服务 ==============

    def get_roleplay_characters(self) -> List[Dict[str, Any]]:
        """获取可用角色列表"""
        from app.services.ai_roleplay_service import get_available_characters

        return get_available_characters()

    async def chat_with_character(
        self, character_id: str, message: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        与AI角色对话

        Args:
            character_id: 角色ID
            message: 用户消息
            session_id: 会话ID（可选）

        Returns:
            对话结果
        """
        from app.services.ai_roleplay_service import chat_with_character

        return await chat_with_character(character_id, message, session_id)

    def create_roleplay_session(
        self, character_id: str, user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        创建角色扮演会话

        Returns:
            会话ID
        """
        session = ai_roleplay_service.create_session(character_id, user_id)
        return session.id if session else None

    # ============== 服务推荐 ==============

    # ============== 语音合成服务 ==============

    def get_tts_voices(self, provider: str = "auto") -> List[Dict[str, Any]]:
        """
        获取可用的 TTS 音色

        Args:
            provider: 提供商 (stepfun/minimax/auto)

        Returns:
            音色列表
        """
        if provider == "auto":
            if self.status.stepfun:
                provider = "stepfun"
            elif self.status.minimax:
                provider = "minimax"
            elif self.status.azure_speech:
                provider = "azure"

        if provider == "stepfun" and self.status.stepfun:
            # 返回 StepFun 音色
            return [
                {
                    "id": "zhengpaiqingnian",
                    "name": "正派青年",
                    "gender": "male",
                    "style": "professional",
                },
                {
                    "id": "ganliannvsheng",
                    "name": "干练女声",
                    "gender": "female",
                    "style": "professional",
                },
                {
                    "id": "cixingnansheng",
                    "name": "磁性男声",
                    "gender": "male",
                    "style": "professional",
                },
                {
                    "id": "linjiajiejie",
                    "name": "邻家姐姐",
                    "gender": "female",
                    "style": "casual",
                },
                {
                    "id": "yuanqishaonv",
                    "name": "元气少女",
                    "gender": "female",
                    "style": "energetic",
                },
            ]
        elif provider == "minimax" and self.status.minimax:
            # 返回 Minimax 音色
            service = self._services.get("minimax_tts")
            if service:
                return service.get_voices()

        return []

    async def generate_speech(
        self, text: str, voice: str, provider: str = "auto", **kwargs
    ) -> bytes:
        """
        生成语音

        Args:
            text: 文本内容
            voice: 音色ID
            provider: 提供商 (stepfun/minimax/azure/auto)
            **kwargs: 其他参数

        Returns:
            音频数据
        """
        if provider == "auto":
            if self.status.stepfun and STEPFUN_TTS_AVAILABLE:
                provider = "stepfun"
            elif self.status.minimax:
                provider = "minimax"

        if provider == "stepfun" and self.status.stepfun and STEPFUN_TTS_AVAILABLE:
            api_key = settings.STEPFUN_API_KEY
            tts = StepFunTTS(api_key=api_key, cache_dir="./generated/voice_cache")
            return await tts.generate(text, voice=voice, **kwargs)

        if provider == "minimax" and self.status.minimax:
            service = self._services["minimax_tts"]
            return await service.generate(text, voice=voice, **kwargs)

        raise ValueError(f"TTS provider {provider} not available")

# ============== 服务推荐 ==============

    def recommend_service(self, task_type: str) -> Dict[str, Any]:
        """
        根据任务类型推荐服务

        Args:
            task_type: 任务类型 (copywriting/image_generation/video_generation/etc.)

        Returns:
            推荐的服务信息
        """
        recommendations = {
            "copywriting": {
                "primary": "openai"
                if self.status.openai
                else ("minimax" if self.status.minimax else "stepfun"),
                "fallback": "stepfun"
                if self.status.stepfun and (self.status.openai or self.status.minimax)
                else None,
                "reason": "OpenAI GPT-4 擅长创意文案，Minimax/StepFun 是国内可用备选",
            },
            "image_generation": {
                "primary": "openai" if self.status.openai else "stability",
                "fallback": "stability"
                if self.status.stability and self.status.openai
                else None,
                "reason": "DALL-E 3 理解力强，Stability AI 性价比高",
            },
            "poster_enhancement": {
                "primary": "stability" if self.status.stability else "openai",
                "fallback": "openai"
                if self.status.openai and self.status.stability
                else None,
                "reason": "Stability AI 更适合营销海报风格",
            },
            "video_generation": {
                "primary": "replicate" if self.status.replicate else "runway",
                "fallback": "runway"
                if self.status.runway and self.status.replicate
                else None,
                "reason": "Replicate 模型选择多，Runway 质量高",
            },
            "voice_synthesis": {
                "primary": "stepfun"
                if self.status.stepfun
                else ("minimax" if self.status.minimax else "azure_speech"),
                "fallback": "minimax"
                if self.status.minimax and self.status.stepfun
                else None,
                "reason": "StepFun 音色丰富，Minimax 语音质量高",
            },
            "roleplay_chat": {
                "primary": "openai" if self.status.openai else None,
                "fallback": None,
                "reason": "角色扮演需要 GPT-4 级别的模型能力",
            },
        }

        return recommendations.get(
            task_type,
            {"primary": None, "fallback": None, "reason": "Unknown task type"},
        )


# 全局服务管理器实例
ai_service_manager = AIServiceManager()
