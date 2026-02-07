#!/usr/bin/env python3
"""
AI 服务配置检查脚本
用于验证所有 AI API Key 是否正确配置
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.logging import logger


async def check_openai():
    """检查 OpenAI 服务"""
    print("\n🔍 检查 OpenAI 服务...")

    if (
        not settings.OPENAI_API_KEY
        or settings.OPENAI_API_KEY == "sk-your-openai-api-key-here"
    ):
        print("  ❌ OpenAI API Key 未配置")
        return False

    try:
        from app.services.openai_service import OpenAIService

        service = OpenAIService()

        # 测试简单请求
        messages = [{"role": "user", "content": "Hello"}]
        response = await service.chat_completion(messages, max_tokens=10)

        print("  ✅ OpenAI 服务正常")
        print(f"  📊 使用模型: {settings.OPENAI_MODEL}")
        return True

    except Exception as e:
        print(f"  ❌ OpenAI 服务异常: {e}")
        return False


async def check_stability():
    """检查 Stability AI 服务"""
    print("\n🔍 检查 Stability AI 服务...")

    if (
        not settings.STABILITY_API_KEY
        or settings.STABILITY_API_KEY == "sk-your-stability-api-key-here"
    ):
        print("  ❌ Stability API Key 未配置")
        return False

    try:
        from app.services.stability_service import StabilityAI

        service = StabilityAI()

        print("  ✅ Stability AI 配置正确")
        print(f"  📊 使用模型: {settings.STABILITY_MODEL}")
        return True

    except Exception as e:
        print(f"  ❌ Stability AI 服务异常: {e}")
        return False


async def check_replicate():
    """检查 Replicate 服务"""
    print("\n🔍 检查 Replicate 服务...")

    if (
        not settings.REPLICATE_API_TOKEN
        or settings.REPLICATE_API_TOKEN == "r8-your-replicate-token-here"
    ):
        print("  ❌ Replicate API Token 未配置")
        return False

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.replicate.com/v1/models",
                headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"},
                timeout=10.0,
            )

            if response.status_code == 200:
                print("  ✅ Replicate 服务正常")
                return True
            else:
                print(f"  ❌ Replicate 服务异常: HTTP {response.status_code}")
                return False

    except Exception as e:
        print(f"  ❌ Replicate 服务异常: {e}")
        return False


async def check_runway():
    """检查 Runway ML 服务"""
    print("\n🔍 检查 Runway ML 服务...")

    if (
        not settings.RUNWAY_API_KEY
        or settings.RUNWAY_API_KEY == "your-runway-api-key-here"
    ):
        print("  ❌ Runway API Key 未配置")
        return False

    print("  ⚠️  Runway 配置已设置（需要实际调用来验证）")
    return True


async def check_stepfun():
    """检查 StepFun 服务"""
    print("\n🔍 检查 StepFun (阶跃星辰) 服务...")

    if (
        not settings.STEPFUN_API_KEY
        or settings.STEPFUN_API_KEY == "your-stepfun-api-key-here"
    ):
        print("  ❌ StepFun API Key 未配置")
        return False

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.stepfun.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.STEPFUN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.STEPFUN_LLM_MODEL,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10,
                },
                timeout=10.0,
            )

            if response.status_code == 200:
                print("  ✅ StepFun 服务正常")
                print(f"  📊 LLM 模型: {settings.STEPFUN_LLM_MODEL}")
                print(f"  📊 TTS 模型: {settings.STEPFUN_TTS_MODEL}")
                return True
            else:
                print(f"  ❌ StepFun 服务异常: HTTP {response.status_code}")
                return False

    except Exception as e:
        print(f"  ❌ StepFun 服务异常: {e}")
        return False


async def check_minimax():
    """检查 Minimax 服务"""
    print("\n🔍 检查 Minimax (稀宇科技) 服务...")

    if (
        not settings.MINIMAX_API_KEY
        or settings.MINIMAX_API_KEY == "your-minimax-api-key-here"
    ):
        print("  ❌ Minimax API Key 未配置")
        return False

    if (
        not settings.MINIMAX_GROUP_ID
        or settings.MINIMAX_GROUP_ID == "your-minimax-group-id-here"
    ):
        print("  ❌ Minimax Group ID 未配置")
        return False

    try:
        from app.services.minimax_service import MinimaxLLM

        service = MinimaxLLM()

        # 测试简单请求
        messages = [{"role": "user", "content": "Hello"}]
        response = await service.chat_completion(messages, max_tokens=10)

        print("  ✅ Minimax 服务正常")
        print(f"  📊 LLM 模型: {settings.MINIMAX_LLM_MODEL}")
        print(f"  📊 TTS 模型: {settings.MINIMAX_TTS_MODEL}")
        return True

    except Exception as e:
        print(f"  ❌ Minimax 服务异常: {e}")
        return False


async def check_azure_speech():
    """检查 Azure Speech 服务"""
    print("\n🔍 检查 Azure Speech 服务...")

    if not settings.AZURE_SPEECH_KEY or not settings.AZURE_SPEECH_REGION:
        print("  ❌ Azure Speech 配置不完整")
        return False

    print("  ⚠️  Azure Speech 配置已设置（需要实际调用来验证）")
    return True


def print_summary(results):
    """打印检查结果摘要"""
    print("\n" + "=" * 60)
    print("📋 AI 服务配置检查结果")
    print("=" * 60)

    total = len(results)
    configured = sum(1 for r in results.values() if r)

    print(f"\n已配置服务: {configured}/{total}")
    print()

    for service, status in results.items():
        icon = "✅" if status else "❌"
        status_text = "已配置" if status else "未配置"
        print(f"  {icon} {service:20s} {status_text}")

    print("\n" + "=" * 60)
    print("💡 使用建议:")

    if results.get("OpenAI"):
        print("  • 图像生成: 使用 OpenAI DALL-E 3 获得最佳效果")
        print("  • AI 角色扮演: 已可用，支持8种专业角色")
    elif results.get("Stability AI"):
        print("  • 图像生成: 使用 Stability AI 作为备选方案")

    if results.get("Replicate") or results.get("Runway"):
        print("  • 视频生成: 已可用，支持文生视频和图生视频")

    if results.get("StepFun"):
        print("  • 语音合成: StepFun 已可用，支持多种中文音色")
        print("  • 文案生成: 可使用 StepFun 替代 OpenAI")

    if results.get("Minimax"):
        print("  • 语音合成: Minimax 已可用，语音质量高")
        print("  • 文案生成: 可使用 Minimax abab6.5 模型")

    if results.get("StepFun") and results.get("Minimax"):
        print("  • 国产 AI: StepFun + Minimax 双服务可用，可自由切换")

    print("\n📖 详细配置指南: docs/AI_API_SETUP_GUIDE.md")
    print("=" * 60)


async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 PitchCube AI 服务配置检查")
    print("=" * 60)

    results = {}

    # 检查各项服务
    results["OpenAI"] = await check_openai()
    results["Stability AI"] = await check_stability()
    results["Replicate"] = await check_replicate()
    results["Runway"] = await check_runway()
    results["StepFun"] = await check_stepfun()
    results["Minimax"] = await check_minimax()
    results["Azure Speech"] = await check_azure_speech()

    # 打印摘要
    print_summary(results)

    # 返回退出码
    configured = sum(1 for r in results.values() if r)
    if configured == 0:
        print("\n⚠️  警告: 没有配置任何 AI 服务，部分功能将不可用")
        return 1
    elif configured < 3:
        print("\n⚠️  建议: 配置更多服务以获得完整体验")
        return 0
    else:
        print("\n🎉 恭喜! 你的 AI 服务配置完善")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
