from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.emby_library_service import get_emby_library_service
from app.utils.logger import logger

router = APIRouter()

@router.get("/list")
async def list_libraries(server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service: raise HTTPException(status_code=400, detail="Emby server not configured")
    return await service.get_libraries()

@router.post("/add")
async def add_library(name: str, collection_type: str, path: Optional[str] = None, server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service: raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.add_library(name, collection_type, path)
    if not success: raise HTTPException(status_code=500, detail="Failed to add library")
    return {"message": "Library added"}

@router.post("/update")
async def update_library(library_data: Dict[str, Any], server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service: raise HTTPException(status_code=400, detail="Emby server not configured")
    
    lib_id = library_data.get("Id")
    lib_name = library_data.get("Name")
    new_options = library_data.get("LibraryOptions", {})
    
    # 1. 路径同步逻辑
    current_libs = await service.get_libraries()
    current_lib = next((l for l in current_libs if l.get("Id") == lib_id), None)
    
    if current_lib:
        # 获取当前路径列表 (Locations)
        current_paths = set([p.rstrip('/') for p in current_lib.get("Locations", [])])
        # 获取目标路径列表 (PathInfos)
        new_paths_list = new_options.get("PathInfos", [])
        new_paths = set([p.get("Path").rstrip('/') for p in new_paths_list if p.get("Path")])
        
        logger.info(f"Path Sync - Current: {current_paths} | New: {new_paths}")
        
        # A. 增加新路径
        for p in (new_paths - current_paths):
            logger.info(f"Adding new path: {p}")
            await service.add_library_path(lib_name, lib_id, p)
            
        # B. 删除旧路径 (注意：如果新旧路径完全一致，则不执行任何操作)
        for p in (current_paths - new_paths):
            logger.info(f"Removing old path: {p}")
            await service.remove_library_path(lib_name, lib_id, p)

    # 2. 更新元数据设置 (使用专门的 LibraryOptions 接口)
    # 过滤掉 LibraryOptions 中的 PathInfos 字段，因为它已经由上述原子操作处理
    clean_options = {k: v for k, v in new_options.items() if k != "PathInfos"}
    
    success = await service.update_library_options(lib_id, clean_options)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update library options")
        
    return {"message": "Library updated successfully"}

@router.delete("/remove")
async def remove_library(name: str, id: str, server_id: Optional[str] = None):
    service = get_emby_library_service(server_id)
    if not service: raise HTTPException(status_code=400, detail="Emby server not configured")
    success = await service.delete_library(name, id)
    if not success: raise HTTPException(status_code=500, detail="Failed to remove library")
    return {"message": "Library removed"}