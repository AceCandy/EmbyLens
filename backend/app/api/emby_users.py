from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.emby_user_service import get_emby_user_service

router = APIRouter()

@router.get("/list")
async def list_users(server_id: Optional[str] = None):
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    return await service.get_users()

@router.post("/create")
async def create_user(name: str, server_id: Optional[str] = None):
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    user = await service.create_user(name)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: str, server_id: Optional[str] = None):
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user")
    return {"message": "User deleted"}

@router.get("/{user_id}/info")
async def get_user_info(user_id: str, server_id: Optional[str] = None):
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    info = await service.get_user_info(user_id)
    if not info:
        raise HTTPException(status_code=404, detail="User not found")
    return info

@router.post("/{user_id}/policy")
async def update_user_policy(user_id: str, policy: Dict[str, Any], server_id: Optional[str] = None):
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.update_user_policy(user_id, policy)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update policy")
    return {"message": "Policy updated"}

@router.post("/{user_id}/password")
async def update_user_password(user_id: str, data: Dict[str, str], server_id: Optional[str] = None):
    new_password = data.get("password")
    if not new_password:
        raise HTTPException(status_code=400, detail="Password is required")
    service = get_emby_user_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.update_user_password(user_id, new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update password")
    return {"message": "Password updated"}
