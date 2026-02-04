import os
import json
import time
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.emby_user_service import get_emby_user_service
from app.services.emby_library_service import get_emby_library_service

router = APIRouter()

BASE_BACKUP_DIR = "data/backups/emby_configs"

def get_backup_path(category: str):
    path = os.path.join(BASE_BACKUP_DIR, category)
    os.makedirs(path, exist_ok=True)
    return path

@router.get("/list")
async def list_backups(category: str = Query(..., regex="^(users|libraries)$")):
    path = get_backup_path(category)
    files = []
    for f in os.listdir(path):
        if f.endswith(".json"):
            full_path = os.path.join(path, f)
            stat = os.stat(full_path)
            files.append({
                "filename": f,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "path": full_path
            })
    # 按时间倒序
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files

@router.post("/create")
async def create_backup(
    category: str, 
    id: str, 
    name: str, 
    server_id: Optional[str] = None
):
    if category == "users":
        service = get_emby_user_service(server_id)
        config = await service.get_user_info(id)
    else:
        # 媒体库备份，我们需要先获取列表找到对应的那个
        service = get_emby_library_service(server_id)
        libs = await service.get_libraries()
        config = next((l for l in libs if l.get("Id") == id), None)

    if not config:
        raise HTTPException(status_code=404, detail="Source configuration not found")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in name if c.isalnum() or c in (" ", "_", "-")]).strip()
    filename = f"{safe_name}_{timestamp}.json"
    full_path = os.path.join(get_backup_path(category), filename)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    return {"message": "Backup created", "filename": filename}

@router.post("/restore")
async def restore_backup(
    category: str, 
    filename: str, 
    server_id: Optional[str] = None
):
    full_path = os.path.join(get_backup_path(category), filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Backup file not found")

    with open(full_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if category == "users":
        service = get_emby_user_service(server_id)
        user_id = config.get("Id")
        policy = config.get("Policy")
        if not user_id or not policy:
            raise HTTPException(status_code=400, detail="Invalid backup file structure")
        success = await service.update_user_policy(user_id, policy)
    else:
        service = get_emby_library_service(server_id)
        success = await service.update_library_options(config)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to restore configuration to Emby")

    return {"message": "Configuration restored successfully"}

@router.delete("/delete")
async def delete_backup(category: str, filename: str):
    full_path = os.path.join(get_backup_path(category), filename)
    if os.path.exists(full_path):
        os.remove(full_path)
    return {"message": "Backup deleted"}
