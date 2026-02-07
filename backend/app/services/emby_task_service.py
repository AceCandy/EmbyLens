from typing import List, Dict, Any, Optional
from app.services.emby import get_emby_service, EmbyService
from app.utils.logger import logger

class EmbyTaskService:
    @staticmethod
    async def get_tasks() -> List[Dict[str, Any]]:
        """获取所有任务计划"""
        service = get_emby_service()
        if not service: return []
        resp = await service._request("GET", "/ScheduledTasks")
        return resp.json() if resp and resp.status_code == 200 else []

    @staticmethod
    async def get_task(task_id: str) -> Optional[Dict[str, Any]]:
        """获取特定任务详情"""
        service = get_emby_service()
        if not service: return None
        resp = await service._request("GET", f"/ScheduledTasks/{task_id}")
        return resp.json() if resp and resp.status_code == 200 else None

    @staticmethod
    async def run_task(task_id: str) -> bool:
        """启动任务"""
        service = get_emby_service()
        if not service: return False
        resp = await service._request("POST", f"/ScheduledTasks/Running/{task_id}")
        return resp is not None and resp.status_code in [200, 204]

    @staticmethod
    async def stop_task(task_id: str) -> bool:
        """停止任务"""
        service = get_emby_service()
        if not service: return False
        resp = await service._request("DELETE", f"/ScheduledTasks/Running/{task_id}")
        return resp is not None and resp.status_code in [200, 204]
