"""
Poster generation service
"""

import random
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


class PosterGenerator:
    """Poster generation service."""
    
    def __init__(self):
        self.templates = [
            "tech-modern",
            "startup-bold", 
            "minimal-clean",
            "creative-gradient",
        ]
    
    async def generate_with_ai(self, request) -> dict:
        """
        Generate poster using AI service.
        Requires STABILITY_API_KEY to be configured.
        """
        logger.info(f"Generating AI poster for: {request.product_name}")
        
        # In production, this would call Stability AI or similar service
        # For now, return mock result
        return await self.generate_mock(request)
    
    async def generate_mock(self, request) -> dict:
        """
        Generate poster using templates and mock data.
        Works without API keys.
        """
        logger.info(f"Generating mock poster for: {request.product_name}")
        
        template_id = request.template_id or random.choice(self.templates)
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(2)
        
        generation_id = f"poster_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
        
        return {
            "id": generation_id,
            "status": "completed",
            "template_id": template_id,
            "product_name": request.product_name,
            "preview_url": f"/generated/{generation_id}_preview.png",
            "download_urls": {
                "png": f"/download/{generation_id}.png",
                "pdf": f"/download/{generation_id}.pdf",
                "jpg": f"/download/{generation_id}.jpg",
            },
            "dimensions": {
                "width": 1200,
                "height": 1600,
            },
            "colors_used": [request.primary_color or "#0ea5e9"],
            "generated_at": datetime.utcnow().isoformat(),
        }
    
    def get_template_preview(self, template_id: str) -> Optional[dict]:
        """Get template preview data."""
        templates = {
            "tech-modern": {
                "id": "tech-modern",
                "name": "科技现代",
                "colors": ["#0ea5e9", "#6366f1", "#1e293b"],
                "font": "Inter",
                "style": "modern",
            },
            "startup-bold": {
                "id": "startup-bold",
                "name": "创业宣言",
                "colors": ["#f97316", "#ec4899", "#7c2d12"],
                "font": "Poppins",
                "style": "bold",
            },
            "minimal-clean": {
                "id": "minimal-clean",
                "name": "极简主义",
                "colors": ["#18181b", "#71717a", "#f4f4f5"],
                "font": "SF Pro",
                "style": "minimal",
            },
            "creative-gradient": {
                "id": "creative-gradient",
                "name": "创意渐变",
                "colors": ["#8b5cf6", "#ec4899", "#f43f5e"],
                "font": "Outfit",
                "style": "creative",
            },
        }
        return templates.get(template_id)
