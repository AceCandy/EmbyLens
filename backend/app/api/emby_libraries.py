from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.emby_library_service import get_emby_library_service

router = APIRouter()

@router.get("/list")
async def list_libraries(server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    return await service.get_libraries()

@router.post("/add")
async def add_library(name: str, collection_type: str, path: Optional[str] = None, server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.add_library(name, collection_type, path)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add library")
    return {"message": "Library added"}

@router.post("/update")
async def update_library(library_data: Dict[str, Any], server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.update_library_options(library_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update library")
    return {"message": "Library updated"}

@router.delete("/remove")
async def remove_library(name: str, id: str, server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service:
        raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.delete_library(name, id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to remove library")
    return {"message": "Library removed"}