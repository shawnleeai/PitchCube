"""
测试 StepFun API 直接调用
"""
import asyncio
import httpx
from app.core.config import settings

async def test_voices():
    api_key = settings.STEPFUN_API_KEY
    print(f"API Key length: {len(api_key)}")
    
    async with httpx.AsyncClient() as client:
        # 获取音色列表
        print("\n=== Getting voice list ===")
        response = await client.get(
            'https://api.stepfun.com/v1/audio/voices',
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            voices = data.get('voices', [])
            print(f"Available voices: {len(voices)}")
            for voice in voices[:10]:
                print(f"  - {voice.get('id')}: {voice.get('name')} ({voice.get('gender')})")
        else:
            print(f"Error: {response.text[:200]}")
        
        # 测试生成语音
        print("\n=== Testing voice generation ===")
        if voices:
            voice_id = voices[0]['id']
            print(f"Using voice: {voice_id}")
            
            response = await client.post(
                'https://api.stepfun.com/v1/audio/speech',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    "model": "step-tts-mini",
                    "input": "欢迎使用 PitchCube",
                    "voice": voice_id,
                    "speed": 1.0
                },
                timeout=30.0
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Audio size: {len(response.content)} bytes")
            else:
                print(f"Error: {response.text[:200]}")

if __name__ == "__main__":
    asyncio.run(test_voices())
