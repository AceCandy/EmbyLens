from fastapi import APIRouter, Query, Body
from typing import Dict, Any, Optional
from app.services.playback_report_service import PlaybackReportService

router = APIRouter()

@router.get("/summary", summary="获取播放统计概览")
async def get_summary(days: int = Query(28, description="统计天数")):
    # 概览可以组合几个核心数据
    return {
        "user_activity": await PlaybackReportService.get_user_activity(days),
        "type_filters": await PlaybackReportService.get_type_filters()
    }

@router.get("/activity", summary="获取播放活跃度流水")
async def get_activity(days: int = Query(28, description="统计天数")):
    return await PlaybackReportService.get_user_activity(days)

@router.get("/users", summary="获取用户统计名单")
async def get_users():
    return await PlaybackReportService.get_user_list()

@router.get("/play-activity", summary="获取播放活跃度统计")
async def get_play_activity(
    item_type: str = Query("Episode", description="媒体类型"),
    days: int = Query(28, description="统计天数")
):
    return await PlaybackReportService.get_play_activity(item_type, days)

@router.get("/sessions", summary="获取会话列表")
async def get_sessions():
    return await PlaybackReportService.get_session_list()

@router.get("/config", summary="获取插件配置")
async def get_config():
    return await PlaybackReportService.get_plugin_config()

@router.post("/config", summary="更新插件配置")
async def update_config(config: Dict[str, Any] = Body(...)):
    return await PlaybackReportService.update_plugin_config(config)

@router.get("/users/{user_id}", summary="获取特定用户信息")
async def get_user_info(user_id: str):
    return await PlaybackReportService.get_user_info(user_id)

@router.get("/report-items", summary="获取报表项 (Get Items)")
async def get_report_items(parent_id: str = Query("0", description="父级ID")):
    return await PlaybackReportService.get_report_items(parent_id)

@router.get("/reports/{report_type}", summary="获取特定报表")
async def get_report(
    report_type: str,
    days: int = Query(28, description="统计天数"),
    user_id: Optional[str] = Query(None, description="用户ID")
):
    """
    report_type 可选: 
    MoviesReport (电影报表), 
    TvShowsReport (剧集报表), 
    DeviceName-BreakdownReport (设备统计), 
    PlaybackMethod-BreakdownReport (播放方式统计), 
    ItemType-BreakdownReport (媒体类型统计), 
    UserId-BreakdownReport (用户活跃统计), 
    HourlyReport (小时活跃度)
    """
    # 转换路径中的横杠为斜杠
    actual_report_type = report_type.replace("-", "/")
    return await PlaybackReportService.get_breakdown_report(actual_report_type, days, user_id)

@router.post("/query", summary="自定义 SQL 查询")
async def custom_query(query: str = Body(..., embed=True)):
    return await PlaybackReportService.submit_custom_query(query)

@router.get("/playlist", summary="获取用户播放清单统计")
async def get_playlist(days: int = Query(28, description="统计天数")):
    return await PlaybackReportService.get_user_playlist(days)

@router.get("/library-summary", summary="获取媒体库质量统计信息")
async def get_library_summary():
    return await PlaybackReportService.get_library_summary()

@router.get("/image-proxy", summary="图片代理")
async def image_proxy(item_id: Optional[str] = None, name: Optional[str] = None, type: str = "item"):
    from fastapi.responses import Response
    from app.services.emby import get_emby_service
    import httpx
    
    service = get_emby_service()
    if not service:
        return Response(status_code=404)
        
    actual_id = item_id
    
    # 核心增强：支持按名称搜索 ID
    if name:
        try:
            search_url = f"{service.base_url}/Items"
            # 这里的 type 映射：Series 或 Movie
            item_types = "Series" if type == "Series" else "Movie"
            async with httpx.AsyncClient(timeout=5.0) as client:
                search_resp = await client.get(search_url, params={
                    "api_key": service.api_key,
                    "SearchTerm": name,
                    "IncludeItemTypes": item_types,
                    "Recursive": "true",
                    "Limit": 1
                })
                if search_resp.status_code == 200:
                    items = search_resp.json().get("Items", [])
                    if items:
                        actual_id = items[0].get("Id")
        except Exception:
            pass

    # 原有的数字 ID 解析逻辑
    elif item_id and item_id.isdigit():
        try:
            search_url = f"{service.base_url}/Items"
            async with httpx.AsyncClient(timeout=5.0) as client:
                search_resp = await client.get(search_url, params={
                    "api_key": service.api_key,
                    "Ids": item_id
                })
                if search_resp.status_code == 200:
                    items = search_resp.json().get("Items", [])
                    if items:
                        actual_id = items[0].get("Id")
        except Exception:
            pass
            
    if not actual_id:
        return Response(status_code=404)

    # 构建原生 Emby 图片请求
    image_type = "user" if type == "user" else "item"
    path = f"/Items/{actual_id}/Images/Primary" if image_type == "item" else f"/Users/{actual_id}/Images/Primary"
    url = f"{service.base_url}{path}"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params={"api_key": service.api_key, "maxWidth": 400})
            if resp.status_code == 200:
                return Response(content=resp.content, media_type=resp.headers.get("Content-Type", "image/jpeg"))
        except Exception:
            pass
            
    return Response(status_code=404)
