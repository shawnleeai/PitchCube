"""
测试语音解说员 API
"""
import asyncio
import httpx
import time


BASE_URL = "http://localhost:8000/api/v1"


async def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/voice/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200


async def test_list_voices():
    """测试获取音色列表"""
    print("\n=== 测试获取音色列表 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/voice/voices")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            voices = response.json()
            print(f"Available voices: {len(voices)}")
            for voice in voices[:3]:
                print(f"  - {voice['name']} ({voice['id']}): {voice['description']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False


async def test_recommendations():
    """测试获取推荐音色"""
    print("\n=== 测试获取推荐音色 ===")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/voice/recommendations")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            recs = response.json()
            print(f"Scenarios: {len(recs)}")
            for rec in recs[:3]:
                print(f"  - {rec['scenario_name']}: {len(rec['recommended_voices'])} voices")
            return True
        else:
            print(f"Error: {response.text}")
            return False


async def test_generate_voice():
    """测试生成语音"""
    print("\n=== 测试生成语音 ===")
    
    test_text = "欢迎使用 PitchCube 路演魔方，让创意变成现实。"
    
    async with httpx.AsyncClient() as client:
        # 提交生成任务
        print(f"Submitting voice generation task...")
        print(f"Text: {test_text}")
        
        response = await client.post(
            f"{BASE_URL}/voice/generate",
            json={
                "text": test_text,
                "voice_style": "professional",
                "speed": 1.0
            }
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code != 202:
            print(f"Error: {response.text}")
            return False
        
        data = response.json()
        generation_id = data["id"]
        print(f"Generation ID: {generation_id}")
        print(f"Estimated duration: {data.get('duration_estimate', 'unknown')}s")
        print(f"Voice: {data.get('voice_name', 'unknown')}")
        
        # 轮询状态
        print("\nPolling for completion...")
        max_retries = 30
        for i in range(max_retries):
            await asyncio.sleep(2)
            
            status_response = await client.get(f"{BASE_URL}/voice/generations/{generation_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data["status"]
                print(f"  Attempt {i+1}: {status}")
                
                if status == "completed":
                    print(f"\n✅ Generation completed!")
                    print(f"Audio URL: {status_data.get('audio_url')}")
                    return True
                elif status == "failed":
                    print(f"\n❌ Generation failed: {status_data.get('error_message')}")
                    return False
            else:
                print(f"  Attempt {i+1}: Error {status_response.status_code}")
        
        print("\n⏱️ Timeout waiting for completion")
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("PitchCube 语音解说员 API 测试")
    print("=" * 60)
    
    results = []
    
    # 测试健康检查
    try:
        results.append(("Health Check", await test_health()))
    except Exception as e:
        print(f"Health check failed: {e}")
        results.append(("Health Check", False))
    
    # 测试音色列表
    try:
        results.append(("List Voices", await test_list_voices()))
    except Exception as e:
        print(f"List voices failed: {e}")
        results.append(("List Voices", False))
    
    # 测试推荐音色
    try:
        results.append(("Recommendations", await test_recommendations()))
    except Exception as e:
        print(f"Recommendations failed: {e}")
        results.append(("Recommendations", False))
    
    # 测试生成语音（可选，需要API key）
    try:
        results.append(("Generate Voice", await test_generate_voice()))
    except Exception as e:
        print(f"Generate voice failed: {e}")
        results.append(("Generate Voice", False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    print(f"\n总计: {passed_count}/{len(results)} 通过")


if __name__ == "__main__":
    asyncio.run(main())
