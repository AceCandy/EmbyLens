from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import os
import shutil
from app.db.session import get_db
from app.models.terminal import TerminalHost
from app.services.file_service import FileService
from app.utils.logger import logger

router = APIRouter()

async def get_file_service_for_host(host_id: int, db: AsyncSession):
    file_service = FileService()
    if host_id == 0:
        file_service.mode = 'local'
        return file_service
    
    result = await db.execute(select(TerminalHost).where(TerminalHost.id == host_id))
    host_info = result.scalar_one_or_none()
    if not host_info:
        raise HTTPException(status_code=404, detail="Host not found")
    
    h_dict = {
        "host": host_info.host,
        "port": host_info.port,
        "username": host_info.username,
        "auth_type": host_info.auth_type,
        "password": host_info.password,
        "private_key": host_info.private_key
    }
    await file_service.connect_ssh(h_dict)
    return file_service

@router.post("/{host_id}/upload")
async def file_upload(
    host_id: int,
    path: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        for file in files:
            target_path = os.path.join(path, file.filename).replace("\\", "/")
            await file_service.upload_file(target_path, file)
        return {"status": "success", "count": len(files)}
    finally:
        file_service.close()

@router.get("/{host_id}/download")
async def file_download(
    host_id: int,
    path: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        result = await file_service.download_file(path)
        if file_service.mode == 'ssh':
            background_tasks.add_task(os.remove, result)
            
        return FileResponse(
            path=result,
            filename=os.path.basename(path),
            media_type='application/octet-stream'
        )
    except Exception as e:
        if file_service: file_service.close()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file_service.close()

@router.get("/{host_id}/ls")
async def file_ls(host_id: int, path: str = "/", db: AsyncSession = Depends(get_db)):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        items = await file_service.list_dir(path)
        return {"current_path": path, "items": items}
    finally:
        file_service.close()

@router.get("/{host_id}/read")
async def file_read(host_id: int, path: str, db: AsyncSession = Depends(get_db)):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        content = await file_service.read_file(path)
        return {"content": content}
    finally:
        file_service.close()

@router.post("/{host_id}/write")
async def file_write(
    host_id: int, 
    path: str = Body(..., embed=True), 
    content: str = Body(..., embed=True), 
    db: AsyncSession = Depends(get_db)
):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        await file_service.write_file(path, content)
        return {"status": "success"}
    finally:
        file_service.close()

@router.post("/{host_id}/action")
async def file_action(
    host_id: int, 
    action: str = Body(..., embed=True), 
    path: str = Body(..., embed=True), 
    target: str = Body(None, embed=True),
    db: AsyncSession = Depends(get_db)
):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        await file_service.file_action(action, path, target)
        return {"status": "success"}
    finally:
        file_service.close()

@router.post("/{host_id}/chmod")
async def file_chmod(
    host_id: int,
    path: str = Body(..., embed=True),
    mode: str = Body(None, embed=True),
    owner: str = Body(None, embed=True),
    group: str = Body(None, embed=True),
    recursive: bool = Body(False, embed=True),
    db: AsyncSession = Depends(get_db)
):
    file_service = await get_file_service_for_host(host_id, db)
    try:
        rec_flag = "-R " if recursive else ""
        if mode:
            cmd = f"chmod {rec_flag}{mode} '{path}'"
            if file_service.mode == 'local':
                import subprocess
                subprocess.run(cmd, shell=True)
            else:
                file_service.ssh_client.exec_command(cmd)
        
        if owner or group:
            target = f"{owner or ''}:{group or ''}".strip(":")
            cmd = f"chown {rec_flag}{target} '{path}'"
            if file_service.mode == 'local':
                import subprocess
                subprocess.run(cmd, shell=True)
            else:
                file_service.ssh_client.exec_command(cmd)
        
        return {"status": "success"}
    finally:
        file_service.close()