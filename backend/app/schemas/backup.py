from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class BackupTaskSchema(BaseModel):
    id: Optional[str] = None
    name: str
    mode: str # '7z', 'tar', 'sync', 'pgsql'
    src_path: Optional[str] = None # For pgsql mode, this can be empty
    dst_path: str
    password: Optional[str] = None
    enabled: bool = True
    schedule_type: str # 'cron', 'interval'
    schedule_value: str
    ignore_patterns: Optional[List[str]] = []
    
    # 新增字段
    storage_type: str = "ssd" # 'ssd', 'hdd', 'cloud'
    compression_level: int = 1 # 1-9
    sync_strategy: str = "mirror" # 'mirror', 'incremental'
    
    # 远程备份支持
    host_id: Optional[str] = "local" # 对应 docker_hosts 中的 id

    # PostgreSQL 支持
    pgsql_host_id: Optional[str] = None # 对应 pgsql_hosts 中的 id
    db_names: Optional[List[str]] = []  # 要备份的数据库列表

class BackupHistorySchema(BaseModel):
    id: int
    task_id: str
    task_name: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    mode: str
    size: float
    message: Optional[str]
    output_path: Optional[str]

    class Config:
        from_attributes = True
