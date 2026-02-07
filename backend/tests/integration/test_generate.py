#!/usr/bin/env python3
"""测试海报生成"""

import sys
sys.path.insert(0, '.')

import asyncio
from app.services.poster_renderer import poster_renderer

async def test_generate():
    print("开始生成 PitchCube 宣传海报...")
    print()
    
    result = await poster_renderer.generate(
        product_name='PitchCube',
        description='AI驱动的路演展示自动化平台，10秒生成专业海报',
        features=['智能海报生成', '视频脚本创作', '多平台适配', '一键导出'],
        template_id='tech-modern',
        primary_color='#0ea5e9'
    )
    
    print('海报生成成功！')
    print(f'文件ID: {result["id"]}')
    print(f'预览路径: {result["preview_url"]}')
    print('下载链接:')
    for fmt, url in result['download_urls'].items():
        print(f'   - {fmt.upper()}: {url}')
    print()
    
    # 检查文件是否存在
    import os
    png_file = result['download_urls']['png'].replace('/download/', 'generated/')
    print(f'检查文件: {png_file}')
    if os.path.exists(png_file):
        size = os.path.getsize(png_file)
        print(f'文件存在！大小: {size/1024:.1f} KB')
    else:
        print('文件未找到')
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_generate())
    print("\n测试完成！")
