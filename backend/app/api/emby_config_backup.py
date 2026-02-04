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

async def _perform_single_backup(category: str, item_id: str, name: str, server_id: Optional[str] = None):
    """核心备份执行逻辑"""
    if category == "users":
        service = get_emby_user_service(server_id)
        config = await service.get_user_info(item_id)
    else:
        service = get_emby_library_service(server_id)
        libs = await service.get_libraries()
        config = next((l for l in libs if l.get("Id") == item_id), None)

    if not config:
        return None

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_name = "".join([c for c in name if c.isalnum() or c in (" ", "_", "-")]).strip()
    filename = f"{safe_name}_{timestamp}.json"
    full_path = os.path.join(get_backup_path(category), filename)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    return filename

async def _perform_restore(category: str, config: Dict[str, Any], server_id: Optional[str] = None):
    """核心还原执行逻辑"""
    if category == "users":
        user_service = get_emby_user_service(server_id)
        target_name = config.get("Name")
        if not target_name: return False

        current_users = await user_service.get_users()
        target_user = next((u for u in current_users if u.get("Name") == target_name), None)
        
        target_id = None
        if target_user:
            target_id = target_user.get("Id")
        else:
            new_user = await user_service.create_user(target_name)
            if new_user:
                target_id = new_user.get("Id")
            else:
                return False

        success = True
        if "Policy" in config:
            if not await user_service.update_user_policy(target_id, config["Policy"]): success = False
        if "Configuration" in config:
            if not await user_service.update_user_configuration(target_id, config["Configuration"]): success = False
        return success
    else:
        lib_service = get_emby_library_service(server_id)
        
        # 深度拷贝并清理 ID 相关字段，确保 Emby 识别为“新建”
        new_config = json.loads(json.dumps(config))
        new_config.pop("Id", None)
        new_config.pop("ItemId", None)
        new_config.pop("Guid", None)
        
        # refreshLibrary=false 避免超时
        params = { "refreshLibrary": "false" }
        
        resp = await lib_service._request("POST", "/Library/VirtualFolders", params=params, json_data=new_config)
        return resp is not None and resp.status_code in [200, 204]

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
    filename = await _perform_single_backup(category, id, name, server_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Source configuration not found")
    return {"message": "Backup created", "filename": filename}

@router.post("/create-all")
async def create_all_backups(
    category: str = Query(..., regex="^(users|libraries)$"),
    server_id: Optional[str] = None
):
    count = 0
    if category == "users":
        service = get_emby_user_service(server_id)
        items = await service.get_users()
    else:
        service = get_emby_library_service(server_id)
        items = await service.get_libraries()

    for item in items:
        item_id = item.get("Id")
        item_name = item.get("Name")
        filename = await _perform_single_backup(category, item_id, item_name, server_id)
        if filename: count += 1

    return {"message": f"Successfully backed up {count} {category}", "count": count}

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

    if await _perform_restore(category, config, server_id):
        return {"message": "Configuration restored successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to restore configuration")

@router.post("/restore-all")
async def restore_all_backups(
    category: str = Query(..., regex="^(users|libraries)$"),
    server_id: Optional[str] = None
):
    path = get_backup_path(category)
    if not os.path.exists(path):
        return {"message": "No backups found", "count": 0}
    
    # 获取该目录下所有 JSON，按时间排序，同名的只取最新的
    all_files = [f for f in os.listdir(path) if f.endswith(".json")]
    all_files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
    
    seen_names = set()
    files_to_restore = []
    for f in all_files:
        name_part = f.rsplit('_20', 1)[0]
        if name_part not in seen_names:
            seen_names.add(name_part)
            files_to_restore.append(f)
    
    count = 0
    for f in files_to_restore:
        with open(os.path.join(path, f), "r", encoding="utf-8") as file:
            config = json.load(file)
            if await _perform_restore(category, config, server_id):
                count += 1
                
    return {"message": f"Successfully restored {count} {category} configurations", "count": count}

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
