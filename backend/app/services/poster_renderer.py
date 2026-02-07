"""
快速海报渲染引擎 - 使用PIL直接生成
无需外部依赖，适合黑客松快速演示
"""

import io
import os
import random
from datetime import datetime
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asyncio
import urllib.request


class PosterRenderer:
    """极简海报渲染器 - PIL实现"""

    # 预设配色方案
    COLOR_SCHEMES = {
        "tech-modern": {
            "bg_colors": [("#0ea5e9", "#6366f1"), ("#1e3a8a", "#3b82f6")],
            "text_color": "#ffffff",
            "accent_color": "#60a5fa",
            "font": "modern",
        },
        "startup-bold": {
            "bg_colors": [("#f97316", "#ec4899"), ("#dc2626", "#f59e0b")],
            "text_color": "#ffffff",
            "accent_color": "#fcd34d",
            "font": "bold",
        },
        "minimal-clean": {
            "bg_colors": [("#18181b", "#3f3f46"), ("#27272a", "#52525b")],
            "text_color": "#fafafa",
            "accent_color": "#a1a1aa",
            "font": "clean",
        },
        "creative-gradient": {
            "bg_colors": [("#8b5cf6", "#ec4899"), ("#06b6d4", "#8b5cf6")],
            "text_color": "#ffffff",
            "accent_color": "#c084fc",
            "font": "creative",
        },
    }

    def __init__(self):
        self.output_dir = "generated"
        os.makedirs(self.output_dir, exist_ok=True)
        self.font_path = self._ensure_font()

    def _ensure_font(self) -> str:
        """确保有中文字体可用"""
        # 下载开源中文字体
        font_dir = "fonts"
        os.makedirs(font_dir, exist_ok=True)

        font_path = os.path.join(font_dir, "NotoSansCJK-Regular.ttc")

        # 如果字体不存在，尝试下载或使用系统字体
        if not os.path.exists(font_path):
            # 先尝试找系统字体
            system_fonts = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # 文泉驿
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/System/Library/Fonts/PingFang.ttc",  # 苹方
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]

            for sf in system_fonts:
                if os.path.exists(sf):
                    return sf

            # 如果没有系统字体，下载Google Noto字体
            try:
                print("Downloading Noto Sans CJK font...")
                url = "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
                font_path = os.path.join(font_dir, "NotoSansCJKsc-Regular.otf")
                if not os.path.exists(font_path):
                    urllib.request.urlretrieve(url, font_path)
                return font_path
            except:
                pass

        return font_path if os.path.exists(font_path) else None

    def _get_font(self, size: int) -> ImageFont:
        """获取字体"""
        if self.font_path and os.path.exists(self.font_path):
            try:
                return ImageFont.truetype(self.font_path, size)
            except:
                pass

        # 尝试其他系统字体
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]

        for path in font_paths:
            try:
                return ImageFont.truetype(path, size)
            except:
                continue

        return ImageFont.load_default()

    async def generate(
        self,
        product_name: str,
        description: str,
        features: List[str],
        template_id: str = "tech-modern",
        primary_color: Optional[str] = None,
    ) -> dict:
        """生成海报主函数"""

        # 模拟处理时间
        await asyncio.sleep(1.5)

        # 选择配色
        scheme = self.COLOR_SCHEMES.get(template_id, self.COLOR_SCHEMES["tech-modern"])
        bg_gradient = random.choice(scheme["bg_colors"])

        # 创建画布 (1200 x 1600 - 适合社交媒体)
        width, height = 1200, 1600
        image = Image.new("RGB", (width, height), bg_gradient[0])
        draw = ImageDraw.Draw(image)

        # 绘制渐变背景
        self._draw_gradient(draw, width, height, bg_gradient[0], bg_gradient[1])

        # 绘制装饰元素
        self._draw_decorations(draw, width, height, scheme["accent_color"])

        # 绘制内容
        self._draw_content(
            draw,
            width,
            height,
            product_name,
            description,
            features,
            scheme["text_color"],
            scheme["accent_color"],
        )

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poster_{timestamp}_{random.randint(1000, 9999)}"

        # 保存PNG
        png_path = f"{self.output_dir}/{filename}.png"
        image.save(png_path, "PNG", quality=95)

        # 保存JPG
        jpg_path = f"{self.output_dir}/{filename}.jpg"
        image_jpg = image.convert("RGB")
        image_jpg.save(jpg_path, "JPEG", quality=90)

        return {
            "id": filename,
            "preview_url": f"/download/{filename}.png",
            "download_urls": {
                "png": f"/download/{filename}.png",
                "jpg": f"/download/{filename}.jpg",
            },
            "template_id": template_id,
            "dimensions": {"width": width, "height": height},
        }

    def _draw_gradient(
        self, draw: ImageDraw, width: int, height: int, color1: str, color2: str
    ):
        """绘制渐变背景"""
        c1_rgb = self._hex_to_rgb(color1)
        c2_rgb = self._hex_to_rgb(color2)

        for y in range(height):
            ratio = y / height
            r = int(c1_rgb[0] * (1 - ratio) + c2_rgb[0] * ratio)
            g = int(c1_rgb[1] * (1 - ratio) + c2_rgb[1] * ratio)
            b = int(c1_rgb[2] * (1 - ratio) + c2_rgb[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    def _draw_decorations(
        self, draw: ImageDraw, width: int, height: int, accent_color: str
    ):
        """绘制装饰元素"""
        accent_rgb = self._hex_to_rgb(accent_color)

        # 绘制几个圆形装饰（半透明）
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        circles = [
            (100, 200, 250),
            (width - 150, height - 300, 350),
            (width // 2, 150, 120),
        ]

        for x, y, r in circles:
            overlay_draw.ellipse([x - r, y - r, x + r, y + r], fill=(*accent_rgb, 25))

        # 合并图层
        # 注意：这里简化处理，直接绘制

    def _draw_content(
        self,
        draw: ImageDraw,
        width: int,
        height: int,
        product_name: str,
        description: str,
        features: List[str],
        text_color: str,
        accent_color: str,
    ):
        """绘制文字内容"""
        text_rgb = self._hex_to_rgb(text_color)
        accent_rgb = self._hex_to_rgb(accent_color)

        # 获取字体
        title_font = self._get_font(90)
        body_font = self._get_font(36)
        small_font = self._get_font(32)

        margin = 80
        current_y = 280

        # 绘制产品名称（居中，自动换行）
        max_width = width - 2 * margin
        lines = self._wrap_text(product_name, title_font, max_width, draw)

        for line in lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, current_y), line, font=title_font, fill=text_rgb)
            current_y += 110

        current_y += 50

        # 绘制分隔线
        line_margin = 150
        draw.line(
            [(line_margin, current_y), (width - line_margin, current_y)],
            fill=accent_rgb,
            width=3,
        )
        current_y += 60

        # 绘制描述（自动换行）
        desc_lines = self._wrap_text(description, body_font, max_width - 40, draw)
        for line in desc_lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, current_y), line, font=body_font, fill=text_rgb)
            current_y += 55

        current_y += 80

        # 绘制功能标签
        if features:
            tag_height = 65
            tag_padding = 25
            gap = 20

            # 计算每行能放多少个标签
            row_tags = []
            current_row = []
            current_width = 0

            for feature in features[:4]:
                bbox = draw.textbbox((0, 0), feature, font=small_font)
                tag_width = bbox[2] - bbox[0] + tag_padding * 2

                if current_width + tag_width + gap > max_width and current_row:
                    row_tags.append(current_row)
                    current_row = [feature]
                    current_width = tag_width
                else:
                    current_row.append(feature)
                    current_width += tag_width + gap

            if current_row:
                row_tags.append(current_row)

            # 绘制标签
            for row in row_tags[:2]:
                total_width = 0
                tag_widths = []

                for tag in row:
                    bbox = draw.textbbox((0, 0), tag, font=small_font)
                    tw = bbox[2] - bbox[0] + tag_padding * 2
                    tag_widths.append(tw)
                    total_width += tw

                total_width += gap * (len(row) - 1)
                start_x = (width - total_width) // 2
                x = start_x

                for i, tag in enumerate(row):
                    tw = tag_widths[i]
                    # 绘制圆角矩形背景
                    draw.rounded_rectangle(
                        [x, current_y, x + tw, current_y + tag_height],
                        radius=32,
                        fill=accent_rgb,
                        outline=accent_rgb,
                        width=2,
                    )

                    # 绘制文字
                    bbox = draw.textbbox((0, 0), tag, font=small_font)
                    text_w = bbox[2] - bbox[0]
                    text_x = x + (tw - text_w) // 2
                    text_y = current_y + (tag_height - 32) // 2
                    draw.text((text_x, text_y), tag, font=small_font, fill=text_rgb)

                    x += tw + gap

                current_y += tag_height + 25

        # 底部文字
        current_y = height - 120
        footer_text = "Generated by PitchCube"
        bbox = draw.textbbox((0, 0), footer_text, font=small_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, current_y), footer_text, font=small_font, fill=text_rgb)

    def _wrap_text(
        self, text: str, font: ImageFont, max_width: int, draw: ImageDraw
    ) -> List[str]:
        """自动换行"""
        lines = []
        current_line = ""

        for char in text:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        return lines if lines else [text]

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """十六进制转RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


# 全局渲染器实例
poster_renderer = PosterRenderer()
