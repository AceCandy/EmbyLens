import os
import json
import time
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.emby_user_service import get_emby_user_service
from app.services.emby_library_service import get_emby_library_service
from app.utils.logger import logger

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
    if not os.path.exists(path):
        return []
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
        service = get_emby_library_service(server_id)
        libs = await service.get_libraries()
        config = next((l for l in libs if l.get("Id") == id), None)

    if not config:
        raise HTTPException(status_code=404, detail="Source configuration not found")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    # 清理文件名中的非法字符
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
        backup_config = json.load(f)

    if category == "users":
        user_service = get_emby_user_service(server_id)
        target_name = backup_config.get("Name")
        if not target_name:
            raise HTTPException(status_code=400, detail="Backup file is missing user 'Name'")

        # 1. 查找现有用户
        current_users = await user_service.get_users()
        target_user = next((u for u in current_users if u.get("Name") == target_name), None)
        
        target_id = None
        if target_user:
            target_id = target_user.get("Id")
            logger.info(f"Restoring to existing user: {target_name} ({target_id})")
        else:
            # 2. 如果没找到，创建新用户
            logger.info(f"User {target_name} not found, creating new user...")
            new_user = await user_service.create_user(target_name)
            if new_user:
                target_id = new_user.get("Id")
            else:
                raise HTTPException(status_code=500, detail=f"Failed to create user {target_name}")

        # 3. 应用 Policy 和 Configuration
        success = True
        if "Policy" in backup_config:
            p_res = await user_service.update_user_policy(target_id, backup_config["Policy"])
            if not p_res: success = False
            
        if "Configuration" in backup_config:
            c_res = await user_service.update_user_configuration(target_id, backup_config["Configuration"])
            if not c_res: success = False
            
        if not success:
            raise HTTPException(status_code=500, detail="Failed to apply some user settings")
    else:
        # 媒体库还原逻辑保持不变（原本就是增量/覆盖性质的）
        lib_service = get_emby_library_service(server_id)
        success = await lib_service.update_library_options(backup_config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to restore library configuration")

    return {"message": "Configuration restored successfully"}

@router.delete("/delete")
async def delete_backup(category: str, filename: str):
    full_path = os.path.join(get_backup_path(category), filename)
    if os.path.exists(full_path):
        os.remove(full_path)
    return {"message": "Backup deleted"}

@router.delete("/clear")
async def clear_backups(category: str = Query(..., regex="^(users|libraries)$")):
    path = get_backup_path(category)
    if os.path.exists(path):
        for f in os.listdir(path):
            if f.endswith(".json"):
                os.remove(os.path.join(path, f))
    return {"message": f"All {category} backups cleared"}