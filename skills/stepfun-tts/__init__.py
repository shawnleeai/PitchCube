"""
StepFun TTS Skill - 阶跃星辰语音合成服务

使用示例:
    >>> from stepfun_tts import StepFunTTS
    >>> tts = StepFunTTS()
    >>> audio = await tts.generate("你好，世界！")
    
按场景使用:
    >>> from stepfun_tts import get_voice_recommendations, generate_speech
    >>> voices = get_voice_recommendations("business")
    >>> audio = await generate_speech("欢迎参加路演", voice=voices[0].id)
"""

from .stepfun_tts import (
    StepFunTTS,
    Voice,
    TTSError,
    VoiceNotFoundError,
    APIError,
    VOICE_LIBRARY,
    generate_speech,
    get_voice_recommendations,
)

__version__ = "1.0.0"
__all__ = [
    "StepFunTTS",
    "Voice",
    "TTSError",
    "VoiceNotFoundError",
    "APIError",
    "VOICE_LIBRARY",
    "generate_speech",
    "get_voice_recommendations",
]
