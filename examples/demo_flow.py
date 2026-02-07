#!/usr/bin/env python3
"""
PitchCube API 流程演示
展示完整的海报生成流程
"""

import asyncio
from app.services.poster_renderer import poster_renderer
from datetime import datetime
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step_num, text):
    print(f"\n[步骤 {step_num}] {text}")
    print("-" * 50)

async def demo_flow():
    """演示完整流程"""
    
    print_header("PitchCube 产品演示")
    print("演示时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("\n这是一款为黑客松和初创团队设计的AI路演展示自动化平台")
    
    # 步骤1: 展示模板选择
    print_step(1, "选择模板")
    templates = [
        {"id": "tech-modern", "name": "科技现代", "desc": "SaaS产品"},
        {"id": "startup-bold", "name": "创业宣言", "desc": "创意展示"},
        {"id": "minimal-clean", "name": "极简主义", "desc": "简约风格"},
        {"id": "creative-gradient", "name": "创意渐变", "desc": "活力展示"},
    ]
    print("可用模板:")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t['name']} - 适合{t['desc']}")
    
    selected_template = "tech-modern"
    print(f"\n[OK] 已选择: 科技现代 (蓝紫渐变)")
    
    # 步骤2: 输入产品信息
    print_step(2, "输入产品信息")
    product_info = {
        "name": "PitchCube",
        "description": "AI驱动的路演展示自动化平台，10秒生成专业海报",
        "features": ["智能海报生成", "视频脚本创作", "多平台适配", "一键导出"],
        "audience": "黑客松团队、初创公司"
    }
    
    print("产品名称:", product_info["name"])
    print("产品描述:", product_info["description"])
    print("核心功能:")
    for f in product_info["features"]:
        print(f"  - {f}")
    print("目标受众:", product_info["audience"])
    
    # 步骤3: 生成海报
    print_step(3, "生成海报")
    print("正在生成海报...")
    print("  - 渲染渐变背景")
    print("  - 绘制产品名称")
    print("  - 绘制描述文字")
    print("  - 生成功能标签")
    print("  - 保存图片文件")
    
    start_time = datetime.now()
    
    result = await poster_renderer.generate(
        product_name=product_info["name"],
        description=product_info["description"],
        features=product_info["features"],
        template_id=selected_template,
        primary_color="#0ea5e9"
    )
    
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n[OK] 生成完成！用时: {elapsed:.2f}秒")
    
    # 步骤4: 展示结果
    print_step(4, "生成结果")
    print(f"文件ID: {result['id']}")
    print(f"模板: {result['template_id']}")
    print(f"分辨率: {result['dimensions']['width']} x {result['dimensions']['height']} px")
    print("\n下载链接:")
    for fmt, url in result['download_urls'].items():
        file_path = f"generated/{result['id']}.{fmt}"
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  [OK] {fmt.upper()}: {url} ({size/1024:.1f} KB)")
    
    # 步骤5: 展示文件
    print_step(5, "文件信息")
    png_file = f"generated/{result['id']}.png"
    if os.path.exists(png_file):
        print(f"海报文件: {png_file}")
        print(f"文件大小: {os.path.getsize(png_file)/1024:.1f} KB")
        print(f"文件类型: PNG (支持透明背景)")
        
        # 显示图片路径供用户查看
        abs_path = os.path.abspath(png_file)
        print(f"\n完整路径: {abs_path}")
        print("\n*** 海报已生成，请在文件管理器中查看 ***")
    
    # 总结
    print_header("演示总结")
    print("[OK] 模板系统: 4种精美模板")
    print("[OK] 渲染引擎: PIL直接渲染，无需AI API")
    print("[OK] 生成速度: {:.2f}秒".format(elapsed))
    print("[OK] 输出格式: PNG + JPG")
    print("[OK] 分辨率: 1200x1600px (适合社交媒体)")
    print("\n*** 这就是 PitchCube 的核心功能！ ***")
    
    return result

if __name__ == "__main__":
    try:
        result = asyncio.run(demo_flow())
        
        print("\n" + "="*60)
        print("提示: 运行 launch_demo.bat 启动完整服务")
        print("      然后访问 http://localhost:3000 体验完整界面")
        print("="*60)
        
    except Exception as e:
        print(f"\n[X] 错误: {e}")
        import traceback
        traceback.print_exc()
