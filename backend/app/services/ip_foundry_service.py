"""
IP铸造厂服务 - 生成3D打印IP形象
使用AI生成IP形象设计图和3D打印指南
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.logging import logger


class IPFoundryService:
    """IP铸造厂服务"""

    # IP形象风格模板
    IP_STYLES = {
        "cute": {
            "name": "可爱萌系",
            "description": "圆润可爱的形象，适合面向消费者的产品",
            "features": ["圆润造型", "大眼睛", "友好表情", "柔和色彩"],
            "prompt_template": "cute kawaii 3D character, {theme}, round and friendly design, big expressive eyes, soft pastel colors, toy-like appearance, blender 3D render style, studio lighting, white background, high quality, 8k",
        },
        "tech": {
            "name": "科技未来",
            "description": "现代科技感形象，适合科技产品",
            "features": ["几何造型", "金属质感", "LED元素", "流线设计"],
            "prompt_template": "futuristic tech 3D character, {theme}, geometric design, metallic surfaces, LED accents, sleek modern look, sci-fi style, blender 3D render, studio lighting, white background, high quality, 8k",
        },
        "professional": {
            "name": "专业商务",
            "description": "专业稳重形象，适合B2B产品",
            "features": ["简洁线条", "稳重配色", "专业造型", "可靠感"],
            "prompt_template": "professional corporate 3D mascot, {theme}, clean lines, professional color scheme, trustworthy appearance, minimalist design, blender 3D render, studio lighting, white background, high quality, 8k",
        },
        "creative": {
            "name": "创意艺术",
            "description": "独特创意形象，适合创意类产品",
            "features": ["独特造型", "艺术感", "鲜明个性", "创意元素"],
            "prompt_template": "creative artistic 3D character, {theme}, unique sculptural design, artistic expression, vibrant personality, creative elements, blender 3D render, studio lighting, white background, high quality, 8k",
        },
        "minimalist": {
            "name": "极简主义",
            "description": "极简设计风格，适合现代产品",
            "features": ["简洁几何", "留白设计", "现代感", "优雅线条"],
            "prompt_template": "minimalist 3D character, {theme}, simple geometric shapes, clean design, modern aesthetic, elegant lines, blender 3D render, studio lighting, white background, high quality, 8k",
        },
    }

    # 3D打印参数建议
    PRINT_SETTINGS = {
        "pla": {
            "name": "PLA",
            "description": "环保易打印，适合展示用",
            "temperature": "190-220°C",
            "bed_temperature": "50-60°C",
            "speed": "50-60mm/s",
            "layer_height": "0.2mm",
            "infill": "15-20%",
            "supports": "需要支撑结构",
        },
        "abs": {
            "name": "ABS",
            "description": "强度高，适合功能性部件",
            "temperature": "230-250°C",
            "bed_temperature": "90-110°C",
            "speed": "40-50mm/s",
            "layer_height": "0.2mm",
            "infill": "20-25%",
            "supports": "需要支撑结构",
        },
        "petg": {
            "name": "PETG",
            "description": "强度高且环保，推荐",
            "temperature": "230-250°C",
            "bed_temperature": "70-80°C",
            "speed": "40-50mm/s",
            "layer_height": "0.2mm",
            "infill": "15-20%",
            "supports": "需要支撑结构",
        },
        "resin": {
            "name": "光敏树脂",
            "description": "精度高，适合精细模型",
            "temperature": "室温",
            "bed_temperature": "N/A",
            "speed": "低速",
            "layer_height": "0.05mm",
            "infill": "实心",
            "supports": "自动生成支撑",
        },
    }

    def __init__(self):
        self.output_dir = Path("generated/ip_foundry")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_ip_concept(
        self,
        product_name: str,
        product_description: str,
        style: str = "cute",
        custom_elements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        生成IP形象概念设计

        Args:
            product_name: 产品名称
            product_description: 产品描述
            style: IP形象风格
            custom_elements: 自定义元素

        Returns:
            包含IP形象概念设计的字典
        """
        style_config = self.IP_STYLES.get(style, self.IP_STYLES["cute"])

        # 生成IP形象概念
        concept = {
            "name": f"{product_name}吉祥物",
            "style": style,
            "style_name": style_config["name"],
            "description": self._generate_concept_description(
                product_name, product_description, style_config
            ),
            "features": style_config["features"],
            "custom_elements": custom_elements or [],
            "personality": self._generate_personality(product_description),
            "color_scheme": self._suggest_color_scheme(style),
            "story": self._generate_story(product_name, product_description),
        }

        return concept

    async def generate_image_prompt(
        self,
        product_name: str,
        product_description: str,
        style: str = "cute",
        custom_elements: Optional[List[str]] = None,
    ) -> str:
        """
        生成AI图像生成提示词

        Args:
            product_name: 产品名称
            product_description: 产品描述
            style: IP形象风格
            custom_elements: 自定义元素

        Returns:
            AI图像生成提示词
        """
        style_config = self.IP_STYLES.get(style, self.IP_STYLES["cute"])

        # 构建主题描述
        theme_parts = [product_name]
        if custom_elements:
            theme_parts.extend(custom_elements)
        theme = " ".join(theme_parts)

        # 使用模板生成提示词
        prompt = style_config["prompt_template"].format(theme=theme)

        # 添加产品特征
        if product_description:
            # 提取关键词
            keywords = self._extract_keywords(product_description)
            if keywords:
                prompt += f", featuring {', '.join(keywords[:3])}"

        return prompt

    async def generate_print_guide(
        self, ip_concept: Dict[str, Any], material: str = "pla", size_cm: float = 10.0
    ) -> Dict[str, Any]:
        """
        生成3D打印指南

        Args:
            ip_concept: IP形象概念
            material: 打印材料
            size_cm: 打印尺寸（厘米）

        Returns:
            3D打印指南
        """
        material_config = self.PRINT_SETTINGS.get(material, self.PRINT_SETTINGS["pla"])

        # 计算打印时间和材料用量
        estimated_time = self._estimate_print_time(size_cm, material)
        material_weight = self._estimate_material_weight(size_cm)

        guide = {
            "material": material,
            "material_name": material_config["name"],
            "material_description": material_config["description"],
            "size": f"{size_cm}cm",
            "settings": {
                "temperature": material_config["temperature"],
                "bed_temperature": material_config["bed_temperature"],
                "print_speed": material_config["speed"],
                "layer_height": material_config["layer_height"],
                "infill": material_config["infill"],
                "supports": material_config["supports"],
            },
            "estimated_time": estimated_time,
            "material_weight": f"{material_weight}g",
            "tips": self._generate_print_tips(ip_concept, material),
            "post_processing": self._generate_post_processing_tips(material),
        }

        return guide

    def _generate_concept_description(
        self, product_name: str, product_description: str, style_config: Dict[str, Any]
    ) -> str:
        """生成IP形象概念描述"""
        descriptions = [
            f"为{product_name}设计的专属IP形象",
            f"采用{style_config['name']}风格",
        ]

        if product_description:
            # 提取产品特点
            features = product_description.split("。")[:2]
            if features:
                descriptions.append(f"体现产品特点：{features[0]}")

        return "；".join(descriptions)

    def _generate_personality(self, product_description: str) -> str:
        """生成IP形象性格"""
        personalities = [
            "友好热情，乐于助人",
            "聪明机智，充满创意",
            "可靠稳重，值得信任",
            "活力四射，充满激情",
            "温和亲切，易于接近",
        ]

        # 根据产品描述选择性格
        if "智能" in product_description or "AI" in product_description:
            return personalities[1]  # 聪明机智
        elif "服务" in product_description or "帮助" in product_description:
            return personalities[0]  # 友好热情
        elif "企业" in product_description or "B2B" in product_description:
            return personalities[2]  # 可靠稳重
        else:
            return personalities[0]

    def _suggest_color_scheme(self, style: str) -> List[str]:
        """建议配色方案"""
        schemes = {
            "cute": ["#FFB6C1", "#FFD700", "#98FB98"],  # 粉色、金色、浅绿
            "tech": ["#00CED1", "#4169E1", "#9370DB"],  # 青色、蓝色、紫色
            "professional": ["#2F4F4F", "#4682B4", "#708090"],  # 深灰、钢蓝、灰
            "creative": ["#FF6347", "#FFD700", "#00FA9A"],  # 番茄、金、春绿
            "minimalist": ["#FFFFFF", "#808080", "#000000"],  # 白、灰、黑
        }
        return schemes.get(style, schemes["cute"])

    def _generate_story(self, product_name: str, product_description: str) -> str:
        """生成IP形象背景故事"""
        return (
            f"{product_name}的吉祥物诞生于产品的核心理念之中。"
            f"它代表着{product_description[:30]}... "
            f"它将陪伴用户，带来更好的产品体验。"
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单的关键词提取
        keywords = []
        important_words = [
            "智能",
            "快速",
            "高效",
            "创新",
            "安全",
            "便捷",
            "智能",
            "cloud",
            "data",
            "AI",
            "fast",
            "secure",
        ]

        for word in important_words:
            if word.lower() in text.lower():
                keywords.append(word)

        return keywords

    def _estimate_print_time(self, size_cm: float, material: str) -> str:
        """估算打印时间"""
        # 简化的估算公式
        base_time = 2  # 基础时间2小时
        size_factor = (size_cm / 10) ** 3  # 体积因子
        material_factor = 1.2 if material == "resin" else 1.0  # 树脂打印较慢

        total_hours = base_time * size_factor * material_factor

        if total_hours < 1:
            return f"{int(total_hours * 60)}分钟"
        elif total_hours < 24:
            return f"{total_hours:.1f}小时"
        else:
            return f"{total_hours / 24:.1f}天"

    def _estimate_material_weight(self, size_cm: float) -> int:
        """估算材料用量（克）"""
        # 简化的估算：假设密度和填充率
        volume_cm3 = (size_cm**3) * 0.2  # 20%填充率
        density = 1.25  # PLA密度 g/cm3
        return int(volume_cm3 * density)

    def _generate_print_tips(
        self, ip_concept: Dict[str, Any], material: str
    ) -> List[str]:
        """生成打印技巧"""
        tips = [
            "建议使用0.4mm喷嘴，平衡精度和速度",
            "打印前请确保平台水平校准",
            "首层附着力很重要，请调整Z轴高度",
        ]

        if material == "abs":
            tips.append("ABS容易翘边，建议使用封闭打印室")
        elif material == "petg":
            tips.append("PETG粘喷嘴，建议降低打印速度和温度")
        elif material == "resin":
            tips.extend(["树脂打印后需要清洗和固化", "请在通风良好的环境下操作"])

        # 根据IP形象特点添加建议
        style = ip_concept.get("style", "cute")
        if style == "cute":
            tips.append("圆润造型需要良好的支撑结构")
        elif style == "tech":
            tips.append("细小部件建议降低打印速度提高精度")

        return tips

    def _generate_post_processing_tips(self, material: str) -> List[str]:
        """生成后处理建议"""
        tips = {
            "pla": [
                "移除支撑结构",
                "使用细砂纸打磨表面（400-800目）",
                "可用丙烯颜料上色",
                "喷保护漆增加光泽度",
            ],
            "abs": [
                "移除支撑结构",
                "使用丙酮蒸汽抛光（可选）",
                "打磨后喷涂底漆",
                "使用模型漆上色",
            ],
            "petg": [
                "移除支撑结构",
                "PETG表面较光滑，少量打磨即可",
                "可直接上色或保持原色",
                "喷保护漆防止刮花",
            ],
            "resin": [
                "使用酒精清洗未固化树脂",
                "UV固化（阳光下或UV灯）",
                "去除支撑痕迹",
                "可打磨抛光至镜面效果",
            ],
        }
        return tips.get(material, tips["pla"])

    async def save_ip_design(
        self, ip_id: str, ip_concept: Dict[str, Any], image_url: Optional[str] = None
    ) -> str:
        """
        保存IP形象设计

        Args:
            ip_id: IP形象ID
            ip_concept: IP形象概念
            image_url: 图像URL

        Returns:
            保存的文件路径
        """
        # 保存设计信息为JSON
        design_data = {
            "id": ip_id,
            "created_at": datetime.utcnow().isoformat(),
            "concept": ip_concept,
            "image_url": image_url,
        }

        filepath = self.output_dir / f"{ip_id}_design.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(design_data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def get_ip_styles(self) -> List[Dict[str, Any]]:
        """获取所有IP形象风格"""
        return [
            {
                "id": key,
                "name": config["name"],
                "description": config["description"],
                "features": config["features"],
            }
            for key, config in self.IP_STYLES.items()
        ]

    def get_print_materials(self) -> List[Dict[str, Any]]:
        """获取所有打印材料选项"""
        return [
            {"id": key, "name": config["name"], "description": config["description"]}
            for key, config in self.PRINT_SETTINGS.items()
        ]


# 创建全局服务实例
ip_foundry_service = IPFoundryService()
