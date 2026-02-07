from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.services.emby_task_service import EmbyTaskService

router = APIRouter()

@router.get("", summary="获取 Emby 任务计划列表")
async def list_tasks():
    return await EmbyTaskService.get_tasks()

@router.post("/{task_id}/run", summary="启动 Emby 任务")
async def run_task(task_id: str):
    success = await EmbyTaskService.run_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="启动任务失败")
    return {"message": "任务已启动"}

@router.delete("/{task_id}/run", summary="停止 Emby 任务")
async def stop_task(task_id: str):
    success = await EmbyTaskService.stop_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="停止任务失败")
    return {"message": "任务已停止"}
