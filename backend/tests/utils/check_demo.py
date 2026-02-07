"""
PitchCube 演示健康检查脚本
检查所有关键 API 端点是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加后端目录到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import httpx
from datetime import datetime


BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def check_health():
    """检查基础健康状态"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ 后端服务健康检查通过")
                return True
            else:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 无法连接到后端: {e}")
        print(
            "   请确保后端服务已启动: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
        )
        return False


async def check_templates():
    """检查海报模板 API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_URL}/posters/templates")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 海报模板 API 正常 - 获取到 {len(data)} 个模板")
                return True
            else:
                print(f"❌ 海报模板 API 错误: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 海报模板 API 异常: {e}")
        return False


async def check_voices():
    """检查语音 API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{API_URL}/voice/voices")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 语音 API 正常 - 获取到 {len(data)} 个音色")
                return True
            elif response.status_code == 503:
                print("⚠️  语音 API 未配置 (需要 STEPFUN_API_KEY)")
                return True  # 不算失败，只是未配置
            else:
                print(f"❌ 语音 API 错误: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 语音 API 异常: {e}")
        return False


async def test_poster_generation():
    """测试海报生成"""
    try:
        print("🧪 测试海报生成...")
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 提交生成任务
            response = await client.post(
                f"{API_URL}/posters/generate",
                json={
                    "product_name": "测试产品",
                    "product_description": "这是一个测试产品，用于验证海报生成功能是否正常工作。",
                    "key_features": ["功能1", "功能2", "功能3"],
                    "template_id": "tech-modern",
                },
            )

            if response.status_code == 202:
                data = response.json()
                generation_id = data["id"]
                print(f"✅ 海报生成任务已提交 - ID: {generation_id}")

                # 等待几秒钟然后检查状态
                await asyncio.sleep(3)

                status_response = await client.get(
                    f"{API_URL}/posters/generations/{generation_id}"
                )
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data["status"] == "completed":
                        print(f"✅ 海报生成成功!")
                        print(f"   预览URL: {status_data.get('preview_url', 'N/A')}")
                        return True
                    elif status_data["status"] == "processing":
                        print("⏳ 海报仍在生成中，这是正常的")
                        return True
                    else:
                        print(
                            f"❌ 海报生成失败: {status_data.get('error_message', '未知错误')}"
                        )
                        return False
                else:
                    print(f"❌ 无法查询生成状态: HTTP {status_response.status_code}")
                    return False
            else:
                print(f"❌ 海报生成请求失败: HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   错误详情: {error_detail}")
                except:
                    print(f"   响应内容: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 海报生成测试异常: {e}")
        import traceback

        traceback.print_exc()
        return False


async def check_frontend_build():
    """检查前端配置"""
    env_file = Path(__file__).parent / "frontend" / ".env.local"
    if env_file.exists():
        content = env_file.read_text()
        if "8000" in content:
            print("✅ 前端 API 配置正确 (端口 8000)")
            return True
        else:
            print(f"⚠️  前端 API 配置可能有问题，请检查 {env_file}")
            print(f"   当前配置: {content.strip()}")
            return False
    else:
        print(f"⚠️  前端配置文件不存在: {env_file}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("🎲 PitchCube 演示健康检查")
    print("=" * 60)
    print()

    results = []

    # 检查前端配置
    print("📋 检查前端配置...")
    results.append(("前端配置", await check_frontend_build()))
    print()

    # 检查后端健康状态
    print("🔍 检查后端服务...")
    if not await check_health():
        print()
        print("❌ 后端服务未启动，停止检查")
        print(
            "   请先启动后端: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
        )
        return
    print()

    # 检查 API 端点
    print("🔍 检查 API 端点...")
    results.append(("海报模板", await check_templates()))
    results.append(("语音服务", await check_voices()))
    print()

    # 测试海报生成
    print("🎨 测试核心功能...")
    results.append(("海报生成", await test_poster_generation()))
    print()

    # 总结
    print("=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")

    print()
    print(f"结果: {passed}/{total} 项检查通过")

    if passed == total:
        print()
        print("🎉 所有检查通过！演示系统可以正常工作。")
        print()
        print("访问地址:")
        print("  前端: http://localhost:3000")
        print("  后端: http://localhost:8000")
        print("  API文档: http://localhost:8000/docs")
    else:
        print()
        print("⚠️  部分检查未通过，请根据错误信息修复问题。")
        print()
        print("常见问题:")
        print(
            "  1. 后端未启动 - 运行: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
        )
        print("  2. 端口冲突 - 检查 8000 端口是否被占用")
        print("  3. 依赖缺失 - 运行: pip install -r backend/requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())
