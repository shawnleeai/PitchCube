"""
批量生成 API
"""

import uuid
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/batch", tags=["批量生成"])

batch_jobs: Dict[str, Dict[str, Any]] = {}


class BatchGenerateRequest(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    key_features: List[str]
    types: List[str]
    options: Optional[Dict[str, Any]] = {}


class BatchGenerateResponse(BaseModel):
    batch_id: str
    status: str
    message: str


async def process_batch_item(
    batch_id: str, item_type: str, product_data: dict, index: int, total: int
):
    try:
        batch_jobs[batch_id]["status"] = "processing"
        batch_jobs[batch_id]["progress"] = (index / total) * 100
        batch_jobs[batch_id]["completed"] = index

        if batch_id not in batch_jobs:
            return

        if item_type == "poster":
            result = await generate_poster_async(product_data)
        elif item_type == "video":
            result = await generate_video_async(product_data)
        elif item_type == "voice":
            result = await generate_voice_async(product_data)
        elif item_type == "ip":
            result = await generate_ip_async(product_data)
        else:
            result = {"status": "failed", "message": f"Unknown type: {item_type}"}

        if batch_id not in batch_jobs:
            return

        batch_jobs[batch_id]["results"].append(
            {
                "type": item_type,
                "status": result.get("status", "completed"),
                "url": result.get("url"),
                "message": result.get("message", "Success"),
            }
        )

    except Exception as e:
        if batch_id in batch_jobs:
            batch_jobs[batch_id]["results"].append(
                {"type": item_type, "status": "failed", "message": str(e)}
            )


async def generate_poster_async(product_data: dict):
    await asyncio.sleep(2)
    return {
        "status": "completed",
        "url": f"/downloads/poster_{uuid.uuid4().hex[:8]}.png",
        "message": "海报生成完成",
    }


async def generate_video_async(product_data: dict):
    await asyncio.sleep(3)
    return {
        "status": "completed",
        "url": f"/downloads/video_{uuid.uuid4().hex[:8]}.mp4",
        "message": "视频脚本生成完成",
    }


async def generate_voice_async(product_data: dict):
    await asyncio.sleep(1)
    return {
        "status": "completed",
        "url": f"/downloads/voice_{uuid.uuid4().hex[:8]}.mp3",
        "message": "语音合成完成",
    }


async def generate_ip_async(product_data: dict):
    await asyncio.sleep(2)
    return {
        "status": "completed",
        "url": f"/downloads/ip_{uuid.uuid4().hex[:8]}.png",
        "message": "IP概念生成完成",
    }


@router.post("/generate", response_model=BatchGenerateResponse)
async def create_batch_generation(request: BatchGenerateRequest):
    batch_id = f"batch_{uuid.uuid4().hex[:12]}"

    batch_jobs[batch_id] = {
        "status": "pending",
        "total": len(request.types),
        "completed": 0,
        "progress": 0,
        "results": [],
        "product_id": request.product_id,
    }

    product_data = {
        "product_name": request.product_name,
        "product_description": request.product_description,
        "key_features": request.key_features,
    }

    asyncio.create_task(run_batch_process(batch_id, request.types, product_data))

    return BatchGenerateResponse(
        batch_id=batch_id,
        status="pending",
        message=f"已提交 {len(request.types)} 个生成任务",
    )


async def run_batch_process(batch_id: str, types: List[str], product_data: dict):
    total = len(types)
    for index, item_type in enumerate(types):
        await process_batch_item(batch_id, item_type, product_data, index, total)

    if batch_id in batch_jobs:
        batch_jobs[batch_id]["status"] = "completed"
        batch_jobs[batch_id]["progress"] = 100


@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")

    job = batch_jobs[batch_id]
    return {
        "batch_id": batch_id,
        "status": job["status"],
        "total": job["total"],
        "completed": job["completed"],
        "progress": job["progress"],
        "results": job["results"],
    }


@router.post("/cancel/{batch_id}")
async def cancel_batch(batch_id: str):
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")

    batch_jobs[batch_id]["status"] = "cancelled"
    return {"message": "Batch job cancelled"}


@router.get("/list")
async def list_batches():
    return {"batches": list(batch_jobs.keys())}
