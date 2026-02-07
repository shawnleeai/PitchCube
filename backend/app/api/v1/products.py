"""
产品管理 API
完整的 CRUD 操作，支持 GitHub 项目导入
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.db.mongodb import db
from app.services.github_parser import parse_github_project

router = APIRouter()


# ============ 请求/响应模型 ============


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="产品名称")
    tagline: str = Field(..., max_length=200, description="产品标语")
    description: str = Field(
        ..., min_length=10, max_length=5000, description="产品描述"
    )
    key_features: List[str] = Field(
        default_factory=list, max_length=10, description="关键功能"
    )
    target_audience: Optional[str] = Field(None, max_length=500, description="目标用户")
    github_url: Optional[str] = Field(None, description="GitHub 链接")
    tech_stack: List[str] = Field(default_factory=list, description="技术栈")
    industry: Optional[str] = Field(None, description="行业领域")
    competitors: List[str] = Field(default_factory=list, description="竞争对手")


class ProductCreate(ProductBase):
    """创建产品请求"""

    pass


class ProductUpdate(BaseModel):
    """更新产品请求（所有字段可选）"""

    name: Optional[str] = Field(None, max_length=100)
    tagline: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    key_features: Optional[List[str]] = None
    target_audience: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    industry: Optional[str] = None
    competitors: Optional[List[str]] = None


class ProductResponse(ProductBase):
    """产品响应"""

    id: str
    user_id: str
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    """产品列表响应"""

    total: int
    items: List[ProductResponse]
    offset: int
    limit: int


class GitHubImportRequest(BaseModel):
    """GitHub 导入请求"""

    github_url: str = Field(..., description="GitHub 项目 URL")
    auto_fill: bool = Field(True, description="是否自动填充所有字段")


class GitHubImportResponse(BaseModel):
    """GitHub 导入响应"""

    success: bool
    product: Optional[ProductResponse] = None
    message: str
    extracted_data: Optional[dict] = None


# ============ 辅助函数 ============


async def _get_product_by_id(product_id: str) -> Optional[dict]:
    """通过 ID 获取产品"""
    if db.connected:
        return await db.db.products.find_one({"id": product_id})
    return None


async def _get_products_by_user(
    user_id: str, limit: int = 20, offset: int = 0
) -> tuple:
    """获取用户的产品列表"""
    if not db.connected:
        return 0, []

    total = await db.db.products.count_documents(
        {"user_id": user_id, "is_active": True}
    )

    cursor = (
        db.db.products.find({"user_id": user_id, "is_active": True})
        .sort("created_at", -1)
        .skip(offset)
        .limit(limit)
    )

    products = []
    async for doc in cursor:
        doc.pop("_id", None)
        products.append(doc)

    return total, products


# ============ API 端点 ============


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    user_id: str = "user_123",  # 实际应该从 JWT 获取
):
    """
    创建新产品

    手动创建产品信息
    """
    logger.info(f"创建产品: {product_data.name}")

    product = {
        "id": f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
        "user_id": user_id,
        "name": product_data.name,
        "tagline": product_data.tagline,
        "description": product_data.description,
        "key_features": product_data.key_features,
        "target_audience": product_data.target_audience,
        "github_url": product_data.github_url,
        "tech_stack": product_data.tech_stack,
        "industry": product_data.industry,
        "competitors": product_data.competitors,
        "stars": 0,
        "forks": 0,
        "language": None,
        "topics": [],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.products.insert_one(product)
        logger.info(f"产品已保存到数据库: {product['id']}")
    else:
        logger.warning("数据库未连接，产品仅保存在内存中")

    return ProductResponse(**product)


@router.post("/import-github", response_model=GitHubImportResponse)
async def import_from_github(
    request: GitHubImportRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "user_123",
):
    """
    从 GitHub 导入产品

    自动解析 GitHub 项目信息并创建产品
    """
    logger.info(f"从 GitHub 导入: {request.github_url}")

    # 解析 GitHub 项目
    try:
        github_data = await parse_github_project(request.github_url)

        if not github_data:
            return GitHubImportResponse(
                success=False, message="无法解析 GitHub 项目，请检查 URL 是否正确"
            )

        # 创建产品
        product_data = {
            "id": f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            "user_id": user_id,
            "name": github_data["name"],
            "tagline": github_data["tagline"],
            "description": github_data["description"],
            "key_features": github_data["key_features"],
            "target_audience": None,
            "github_url": github_data["github_url"],
            "tech_stack": github_data["tech_stack"],
            "industry": None,
            "competitors": [],
            "stars": github_data.get("stars", 0),
            "forks": github_data.get("forks", 0),
            "language": github_data.get("language"),
            "topics": github_data.get("topics", []),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        if db.connected:
            await db.db.products.insert_one(product_data)
            logger.info(f"GitHub 产品已导入: {product_data['id']}")

        return GitHubImportResponse(
            success=True,
            product=ProductResponse(**product_data),
            message="GitHub 项目导入成功",
            extracted_data=github_data,
        )

    except Exception as e:
        logger.error(f"GitHub 导入失败: {e}")
        return GitHubImportResponse(success=False, message=f"导入失败: {str(e)}")


@router.get("", response_model=ProductListResponse)
async def list_products(limit: int = 20, offset: int = 0, user_id: str = "user_123"):
    """
    获取产品列表

    获取当前用户的产品列表
    """
    logger.info(f"获取产品列表: user={user_id}, limit={limit}, offset={offset}")

    if db.connected:
        total, products = await _get_products_by_user(user_id, limit, offset)
    else:
        # 演示模式：返回模拟数据
        total = 1
        products = [
            {
                "id": "prod_demo",
                "user_id": user_id,
                "name": "PitchCube",
                "tagline": "AI驱动的路演展示智能魔方平台",
                "description": "专为黑客松团队和初创公司设计的路演展示生成工具",
                "key_features": ["AI海报生成", "视频脚本生成", "语音合成"],
                "github_url": "https://github.com/example/pitchcube",
                "tech_stack": ["Python", "FastAPI", "Next.js"],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        ]

    return ProductListResponse(
        total=total,
        items=[ProductResponse(**p) for p in products],
        offset=offset,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """获取产品详情"""
    logger.info(f"获取产品详情: {product_id}")

    product = await _get_product_by_id(product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

    product.pop("_id", None)
    return ProductResponse(**product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, update_data: ProductUpdate):
    """
    更新产品信息

    只更新提供的字段
    """
    logger.info(f"更新产品: {product_id}")

    product = await _get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

    # 构建更新数据（只包含非 None 的字段）
    update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)
    update_dict["updated_at"] = datetime.utcnow()

    if db.connected:
        await db.db.products.update_one({"id": product_id}, {"$set": update_dict})
        logger.info(f"产品已更新: {product_id}")

    # 获取更新后的产品
    updated_product = await _get_product_by_id(product_id)
    updated_product.pop("_id", None)

    return ProductResponse(**updated_product)


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """删除产品（软删除）"""
    logger.info(f"删除产品: {product_id}")

    product = await _get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

    if db.connected:
        # 软删除
        await db.db.products.update_one(
            {"id": product_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}},
        )
        logger.info(f"产品已软删除: {product_id}")

    return {"message": "产品已删除", "product_id": product_id}


@router.post("/{product_id}/refresh-github")
async def refresh_from_github(product_id: str):
    """
    刷新 GitHub 数据

    重新从 GitHub 获取项目信息并更新
    """
    logger.info(f"刷新 GitHub 数据: {product_id}")

    product = await _get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

    github_url = product.get("github_url")
    if not github_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="产品没有关联的 GitHub 链接"
        )

    # 重新解析 GitHub
    github_data = await parse_github_project(github_url)
    if not github_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无法刷新 GitHub 数据"
        )

    # 更新产品信息
    update_data = {
        "stars": github_data.get("stars", 0),
        "forks": github_data.get("forks", 0),
        "language": github_data.get("language"),
        "topics": github_data.get("topics", []),
        "updated_at": datetime.utcnow(),
    }

    if db.connected:
        await db.db.products.update_one({"id": product_id}, {"$set": update_data})

    return {
        "message": "GitHub 数据已刷新",
        "stars": github_data.get("stars"),
        "forks": github_data.get("forks"),
    }


@router.get("/{product_id}/stats")
async def get_product_stats(product_id: str):
    """获取产品统计信息"""
    logger.info(f"获取产品统计: {product_id}")

    product = await _get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="产品不存在")

    # 查询相关的生成记录
    if db.connected:
        poster_count = await db.db.poster_generations.count_documents(
            {"product_id": product_id}
        )
        video_count = await db.db.video_generations.count_documents(
            {"product_id": product_id}
        )
        voice_count = await db.db.voice_generations.count_documents(
            {"product_id": product_id}
        )
    else:
        poster_count = video_count = voice_count = 0

    return {
        "product_id": product_id,
        "github_stats": {
            "stars": product.get("stars", 0),
            "forks": product.get("forks", 0),
            "language": product.get("language"),
        },
        "generation_stats": {
            "posters": poster_count,
            "videos": video_count,
            "voices": voice_count,
            "total": poster_count + video_count + voice_count,
        },
    }
