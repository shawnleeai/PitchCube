#!/usr/bin/env python3
"""测试完整API流程"""

import requests
import time
import sys

def test_api():
    BASE_URL = "http://localhost:8000/api/v1"
    
    print("=" * 50)
    print("测试 PitchCube API 流程")
    print("=" * 50)
    print()
    
    # 1. 测试健康检查
    print("1. 测试健康检查...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print(f"   状态: 在线 ({r.json()})")
        else:
            print(f"   错误: 状态码 {r.status_code}")
            return False
    except Exception as e:
        print(f"   错误: 无法连接后端 - {e}")
        print("   请确保后端服务已启动: cd backend && python -m uvicorn app.main:app --reload")
        return False
    print()
    
    # 2. 获取模板列表
    print("2. 获取模板列表...")
    r = requests.get(f"{BASE_URL}/posters/templates")
    if r.status_code == 200:
        templates = r.json()
        print(f"   找到 {len(templates)} 个模板:")
        for t in templates:
            print(f"   - {t['name']} ({t['category']})")
    else:
        print(f"   错误: {r.status_code}")
    print()
    
    # 3. 生成海报
    print("3. 生成海报...")
    data = {
        "product_name": "PitchCube",
        "product_description": "AI驱动的路演展示自动化平台，10秒生成专业海报",
        "key_features": ["智能海报生成", "视频脚本创作", "多平台适配", "一键导出"],
        "target_audience": "黑客松团队、初创公司",
        "template_id": "tech-modern"
    }
    
    r = requests.post(f"{BASE_URL}/posters/generate", json=data)
    if r.status_code == 202:
        result = r.json()
        generation_id = result["id"]
        print(f"   任务已创建: {generation_id}")
        print(f"   状态: {result['status']}")
    else:
        print(f"   错误: {r.status_code} - {r.text}")
        return False
    print()
    
    # 4. 轮询状态
    print("4. 轮询生成状态...")
    max_retries = 10
    for i in range(max_retries):
        time.sleep(1)
        r = requests.get(f"{BASE_URL}/posters/generations/{generation_id}")
        if r.status_code == 200:
            status = r.json()
            print(f"   尝试 {i+1}: {status['status']}")
            if status['status'] == 'completed':
                print(f"   生成完成!")
                print(f"   预览: {status['preview_url']}")
                print(f"   下载:")
                for fmt, url in status['download_urls'].items():
                    print(f"      - {fmt}: {url}")
                break
            elif status['status'] == 'failed':
                print(f"   生成失败: {status.get('error_message')}")
                return False
        else:
            print(f"   错误: {r.status_code}")
    else:
        print("   超时: 生成时间过长")
        return False
    print()
    
    # 5. 检查文件是否存在
    print("5. 检查生成的文件...")
    import os
    png_file = f"backend/generated/{generation_id}.png"
    if os.path.exists(png_file):
        size = os.path.getsize(png_file)
        print(f"   文件存在: {png_file}")
        print(f"   文件大小: {size/1024:.1f} KB")
    else:
        print(f"   文件未找到: {png_file}")
    print()
    
    print("=" * 50)
    print("测试完成!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
