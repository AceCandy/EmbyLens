from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, or_
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.models.media import MediaItem
from app.services.emby import EmbyService, get_emby_service
from app.core.scorer import Scorer
from app.core.config_manager import get_config, save_config
from app.utils.logger import logger, audit_log
import time
import re
import asyncio
from collections import defaultdict

router = APIRouter()

# --- 辅助逻辑 ---
SEARCH_FIELD_MAP = { "名称": "name", "路径": "path", "年份": "year", "embyid": "id", "tmdb": "tmdb_id" }

def parse_advanced_search(text: str):
    criteria = {}
    pattern = re.compile(r'(\w+):(?:"([^"]*)"|(\S+))')
    for match in pattern.finditer(text):
        field, quoted_value, unquoted_value = match.groups()
        field_key = field.lower()
        val = (quoted_value if quoted_value is not None else unquoted_value).strip()
        db_field = SEARCH_FIELD_MAP.get(field_key) or SEARCH_FIELD_MAP.get(field)
        if db_field: criteria[db_field] = val
    return criteria

class BulkDeleteRequest(BaseModel):
    item_ids: List[str]

# --- 接口实现 ---

@router.post("/sync")
async def sync_media(db: AsyncSession = Depends(get_db)):
    """同步 Emby 媒体数据，支持 10 并发并行拉取，支持多服务器隔离"""
    start_time = time.time()
    service = get_emby_service()
    if not service:
        raise HTTPException(status_code=400, detail="未配置 Emby 服务器")
    
    config = get_config()
    active_server_id = config.get("active_server_id")
    
    logger.info(f"🚀 [同步] 启动隔离同步引擎 (Server: {active_server_id}, Concurrency: 10)...")
    
    unique_items = {} 
    item_to_series_tmdb = {}

    async def fetch_paged(types, p_id=None):
        fetched = []
        limit = 300
        start = 0
        while True:
            params = {
                "IncludeItemTypes": ",".join(types), "Recursive": "true",
                "Fields": "Path,ProductionYear,ProviderIds,MediaStreams,DisplayTitle,SortName,ParentId,SeriesId,SeasonId,IndexNumber,ParentIndexNumber",
                "StartIndex": start, "Limit": limit
            }
            if p_id: params["ParentId"] = p_id
            resp = await service._request("GET", "/Items", params=params)
            if not resp or resp.status_code != 200: break
            batch = resp.json().get("Items", [])
            if not batch: break
            fetched.extend(batch)
            if len(batch) < limit: break
            start += limit
        return fetched

    # 1. 抓取 Movie 和 Series
    top_items = await fetch_paged(["Movie", "Series"])
    for i in top_items:
        unique_items[i["Id"]] = i
        if i.get("Type") == "Series":
            tmdb = i.get("ProviderIds", {}).get("Tmdb")
            if tmdb: item_to_series_tmdb[i["Id"]] = tmdb
    
    # 2. 并行处理剧集子项
    series_items = [i for i in top_items if i.get("Type") == "Series"]
    total_series = len(series_items)
    logger.info(f"┣ 📂 准备并发解析 {total_series} 个剧集的子层级...")

    sem = asyncio.Semaphore(10)
    processed_count = 0

    async def process_single_series(s_item):
        nonlocal processed_count
        async with sem:
            s_tmdb = item_to_series_tmdb.get(s_item["Id"])
            children = await fetch_paged(["Season", "Episode"], p_id=s_item["Id"])
            for child in children:
                if s_tmdb and not child.get("ProviderIds", {}).get("Tmdb"):
                    if "ProviderIds" not in child: child["ProviderIds"] = {}
                    child["ProviderIds"]["Tmdb"] = s_tmdb
                unique_items[child["Id"]] = child
            
            processed_count += 1
            if processed_count % 20 == 0 or processed_count == total_series:
                logger.info(f"┃  🕒 同步进度: {processed_count}/{total_series}...")

    await asyncio.gather(*[process_single_series(s) for s in series_items])
    
    # 3. 隔离式入库操作
    logger.info(f"┣ 💾 正在将 {len(unique_items)} 条数据持久化至本地库 (Server: {active_server_id})...")
    await db.execute(delete(MediaItem).where(MediaItem.server_id == active_server_id))
    
    for item_id, item in unique_items.items():
        v = next((s for s in item.get("MediaStreams", []) if s.get("Type") == "Video"), {})
        a = next((s for s in item.get("MediaStreams", []) if s.get("Type") == "Audio"), {})
        
        s_num = item.get("ParentIndexNumber") if item.get("Type") == "Episode" else item.get("IndexNumber") if item.get("Type") == "Season" else None
        e_num = item.get("IndexNumber") if item.get("Type") == "Episode" else None
        p_id = item.get("SeasonId") or item.get("SeriesId") or item.get("ParentId")
        
        db.add(MediaItem(
            id=item["Id"], server_id=active_server_id, name=item.get("Name"), item_type=item.get("Type"),
            tmdb_id=item.get("ProviderIds", {}).get("Tmdb"), path=item.get("Path"),
            year=item.get("ProductionYear"), parent_id=p_id,
            season_num=s_num, episode_num=e_num,
            display_title=v.get("DisplayTitle", "N/A"), video_codec=v.get("Codec", "N/A"),
            video_range=v.get("VideoRange", "N/A"), audio_codec=a.get("Codec", "N/A"),
            raw_data=item
        ))
    
    await db.commit()
    process_time = (time.time() - start_time) * 1000
    audit_log("媒体库隔离同步成功", process_time, [
        f"服务器: {active_server_id}",
        f"同步条目数: {len(unique_items)}"
    ])
    logger.info(f"✅ [同步] 完成，总耗时: {int(process_time/1000)}s")
    return {"message": "ok"}

@router.get("/items")
async def get_all_items(query_text: Optional[str] = None, item_type: Optional[str] = None, parent_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    active_server_id = get_config().get("active_server_id")
    query = select(MediaItem).where(MediaItem.server_id == active_server_id)
    
    if query_text:
        if ":" in query_text:
            for f, v in parse_advanced_search(query_text).items():
                if f == "year":
                    try: query = query.where(MediaItem.year == int(v))
                    except: pass
                else: query = query.where(getattr(MediaItem, f).ilike(f"%{v}%"))
        else: query = query.where((MediaItem.name.ilike(f"%{query_text}%")) | (MediaItem.path.ilike(f"%{query_text}%")) | (MediaItem.id == query_text))
    
    if parent_id: query = query.where(MediaItem.parent_id == parent_id)
    elif not query_text:
        if item_type: query = query.where(MediaItem.item_type == item_type)
        else: query = query.where(MediaItem.item_type.in_(["Movie", "Series"]))
        
    result = await db.execute(query.order_by(MediaItem.name))
    return result.scalars().all()

@router.get("/duplicates")
async def list_duplicates(db: AsyncSession = Depends(get_db)):
    """获取所有重复项目 (基于当前服务器隔离)"""
    active_server_id = get_config().get("active_server_id")
    
    body_sub = select(MediaItem.tmdb_id).where(MediaItem.server_id == active_server_id, MediaItem.item_type.in_(["Movie", "Series"]), MediaItem.tmdb_id.isnot(None)).group_by(MediaItem.tmdb_id).having(func.count(MediaItem.id) > 1).subquery()
    bodies = await db.execute(select(MediaItem).where(MediaItem.server_id == active_server_id, MediaItem.tmdb_id.in_(select(body_sub)), MediaItem.item_type.in_(["Movie", "Series"])))
    
    ep_sub = select(MediaItem.tmdb_id, MediaItem.season_num, MediaItem.episode_num).where(MediaItem.server_id == active_server_id, MediaItem.item_type == "Episode", MediaItem.tmdb_id.isnot(None)).group_by(MediaItem.tmdb_id, MediaItem.season_num, MediaItem.episode_num).having(func.count(MediaItem.id) > 1).subquery()
    eps = await db.execute(select(MediaItem).where(MediaItem.server_id == active_server_id).join(ep_sub, (MediaItem.tmdb_id == ep_sub.c.tmdb_id) & (MediaItem.season_num == ep_sub.c.season_num) & (MediaItem.episode_num == ep_sub.c.episode_num)))
    
    res = []
    for item in list(bodies.scalars().all()) + list(eps.scalars().all()):
        res.append({"id": item.id, "name": item.name, "item_type": item.item_type, "path": item.path, "display_title": item.display_title, "video_codec": item.video_codec, "video_range": item.video_range, "tmdb_id": item.tmdb_id, "raw_data": item.raw_data, "is_duplicate": True})
    return res

@router.post("/smart-select")
async def smart_select_v4(db: AsyncSession = Depends(get_db)):
    """智能分析评分引擎 (V4): 深度日志跟踪与内容完整性保护"""
    start_time = time.time()
    active_server_id = get_config().get("active_server_id")
    config = get_config()
    rule_data = config.get("dedupe_rules")
    exclude_paths = config.get("exclude_paths", [])
    scorer = Scorer(rule_data)
    
    logger.info(f"🧪 [智能分析] 评分引擎启动 (Server: {active_server_id})...")
    
    all_items_res = await db.execute(select(MediaItem).where(MediaItem.server_id == active_server_id, MediaItem.item_type.in_(["Movie", "Series", "Episode"])))
    all_items = all_items_res.scalars().all()
    
    # 建立父子关系索引，用于分析 Series 的完整性
    series_episode_map = defaultdict(set)
    for i in all_items:
        if i.item_type == "Episode" and i.parent_id:
            # 记录剧集 ID 下拥有的单集编号 (SxxExx)
            key = f"S{str(i.season_num or 0).zfill(2)}E{str(i.episode_num or 0).zfill(2)}"
            series_episode_map[i.parent_id].add(key)

    groups = defaultdict(list)
    for i in all_items:
        if not i.tmdb_id: continue
        if i.item_type == "Movie": key = f"Movie-{i.tmdb_id}"
        elif i.item_type == "Series": key = f"Series-{i.tmdb_id}"
        elif i.item_type == "Episode": key = f"TV-{i.tmdb_id}-S{str(i.season_num or 0).zfill(2)}E{str(i.episode_num or 0).zfill(2)}"
        else: continue
        groups[key].append(i)
        
    to_delete_ids = []
    duplicate_group_count = 0
    
    for key, g_items in groups.items():
        if len(g_items) > 1:
            duplicate_group_count += 1
            
            # 特殊处理剧集 (Series): 检查内容是否互补
            if key.startswith("Series-"):
                # 如果剧集文件夹包含的集数不完全一致，则视为“互补”或“非镜像”，不自动建议删除
                ep_sets = [series_episode_map.get(i.id, set()) for i in g_items]
                is_complementary = False
                for idx, s1 in enumerate(ep_sets):
                    for jdx, s2 in enumerate(ep_sets):
                        if idx == jdx: continue
                        # 如果 A 有 B 没有的集数，且 B 也有 A 没有的集数，则为互补
                        if (s1 - s2) and (s2 - s1):
                            is_complementary = True
                            break
                    if is_complementary: break
                
                if is_complementary:
                    logger.info(f"┃  🛡️ [剧集保护] 组 [{key}] 为互补内容（各文件夹包含不同集数），跳过自动删除建议")
                    continue

            scored_data = [{"id": i.id, "emby_id": i.id, "path": i.path, "display_title": i.display_title, "video_codec": i.video_codec, "video_range": i.video_range} for i in g_items]
            suggested = scorer.select_best(scored_data)
            
            logger.info(f"┃  ┣ 📦 重复组 [{key}] 有 {len(g_items)} 个副本")
            for i in g_items:
                status = "🗑️ 建议删除" if i.id in suggested else "✅ 建议保留"
                # 改为包含匹配 (只要路径包含关键词即排除)，且忽略大小写
                if i.id in suggested and any(ex.lower() in i.path.lower() for ex in exclude_paths if ex.strip()):
                    status = "🛡️ 白名单保护"
                    suggested.remove(i.id)
                logger.info(f"┃  ┃  ┗ {status}: [{i.display_title} | {i.video_codec}] {i.path}")
            
            to_delete_ids.extend(suggested)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(f"✅ [智能分析] 任务结束: 扫描全库发现 {duplicate_group_count} 组重复，建议删除 {len(to_delete_ids)} 个节点。")
    
    audit_log("智能分析引擎执行完毕", process_time, [
        f"分析总数: {len(all_items)}",
        f"发现重复组: {duplicate_group_count}",
        f"建议清理数: {len(to_delete_ids)}"
    ])
    
    if not to_delete_ids: return []
    final_res = await db.execute(select(MediaItem).where(MediaItem.server_id == active_server_id, MediaItem.id.in_(to_delete_ids)))
    return final_res.scalars().all()

@router.delete("/items")
async def delete_items_optimized(request: BulkDeleteRequest, db: AsyncSession = Depends(get_db)):
    """优化版隔离删除：支持冗余折叠、路径白名单保护与剧集内容降级清理"""
    start_time = time.time()
    active_server_id = get_config().get("active_server_id")
    config = get_config()
    exclude_paths = config.get("exclude_paths", []) # 加载白名单
    service = get_emby_service()
    if not service: raise HTTPException(status_code=400, detail="未配置服务器")
    
    # 1. 加载所有待删条目信息
    res = await db.execute(select(MediaItem).where(MediaItem.server_id == active_server_id, MediaItem.id.in_(request.item_ids)))
    delete_map = {item.id: item for item in res.scalars().all()}
    
    # 2. 预检与拦截
    final_ids_to_call = []
    actual_deleted_ids = [] # 真正需要从数据库移除的 ID
    skipped_count = 0
    downgrade_count = 0
    protected_count = 0
    
    # 提前获取全库单集索引，用于剧集保护
    all_episodes_res = await db.execute(select(MediaItem.tmdb_id, MediaItem.season_num, MediaItem.episode_num, MediaItem.id).where(MediaItem.server_id == active_server_id, MediaItem.item_type == "Episode"))
    ep_registry = defaultdict(list)
    for tmdb_id, s_num, e_num, eid in all_episodes_res.all():
        if tmdb_id: ep_registry[f"{tmdb_id}-S{s_num}E{e_num}"].append(eid)

    for eid in request.item_ids:
        item = delete_map.get(eid)
        if not item: continue
        
        # --- 路径白名单绝对保护 ---
        if any(ex.lower() in item.path.lower() for ex in exclude_paths if ex.strip()):
            logger.error(f"🛡️ [绝对拦截] 尝试删除受白名单保护的路径: {item.path}。操作已拒绝。")
            protected_count += 1
            continue
            
        # 冗余折叠
        if item.parent_id in request.item_ids:
            # 检查父级是否也被保护了，如果父级被保护了，子级不能直接跳过，也得进入保护逻辑（这里由于是递归删除，通常父级保护了子级就安全）
            skipped_count += 1
            actual_deleted_ids.append(eid)
            continue
            
        # 剧集安全校验
        if item.item_type == "Series":
            children_res = await db.execute(select(MediaItem).where(MediaItem.parent_id == item.id, MediaItem.item_type == "Episode"))
            children = children_res.scalars().all()
            
            unsafe_episodes = []
            for child in children:
                key = f"{child.tmdb_id}-S{child.season_num}E{child.episode_num}"
                others = [oid for oid in ep_registry.get(key, []) if oid != child.id and oid not in request.item_ids]
                if not others: unsafe_episodes.append(child)
            
            if unsafe_episodes:
                logger.warning(f"🛡️ [安全拦截] 剧集文件夹 {item.path} 包含唯一集数，拦截并降级。")
                downgrade_count += 1
                for child in children:
                    # 即使降级，也要检查子项是否在白名单中
                    if any(ex.lower() in child.path.lower() for ex in exclude_paths if ex.strip()): continue
                    
                    key = f"{child.tmdb_id}-S{child.season_num}E{child.episode_num}"
                    if any(oid for oid in ep_registry.get(key, []) if oid != child.id and oid not in request.item_ids):
                        final_ids_to_call.append(child.id)
                        actual_deleted_ids.append(child.id)
                continue 

        final_ids_to_call.append(eid)
        actual_deleted_ids.append(eid)

    # 3. 执行物理删除
    success = 0
    for eid in final_ids_to_call:
        item = delete_map.get(eid)
        if not item: continue
        logger.warning(f"🔥 [清理] 执行 Emby 物理删除: {item.path}")
        if await service.delete_item(eid):
            success += 1
    
    # 4. 同步更新数据库 (仅移除真正被删除或需要清理的 ID)
    if actual_deleted_ids:
        await db.execute(delete(MediaItem).where(MediaItem.server_id == active_server_id, MediaItem.id.in_(actual_deleted_ids)))
        await db.commit()
    
    process_time = (time.time() - start_time) * 1000
    audit_log("媒体清理任务完成 (全重保护模式)", process_time, [
        f"API物理删除: {success}",
        f"路径白名单拦截: {protected_count}",
        f"安全拦截降级: {downgrade_count}",
        f"逻辑折叠跳过: {skipped_count}"
    ])
    return {"success": success, "protected": protected_count, "downgraded": downgrade_count}

@router.get("/config")
async def get_dedupe_config():
    config = get_config()
    return {"rules": config.get("dedupe_rules"), "exclude_paths": config.get("exclude_paths", [])}

@router.post("/config")
async def save_dedupe_config(data: Dict[str, Any]):
    config = get_config()
    if "rules" in data: config["dedupe_rules"] = data["rules"]
    if "exclude_paths" in data: config["exclude_paths"] = data["exclude_paths"]
    save_config(config)
    return {"message": "ok"}