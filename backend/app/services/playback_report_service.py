from typing import List, Dict, Any, Optional
from app.services.emby import get_emby_service, EmbyService
from app.utils.logger import logger

class PlaybackReportService:
    @staticmethod
    async def _get_service() -> Optional[EmbyService]:
        return get_emby_service()

    @classmethod
    async def get_report_data(cls, endpoint: str, params: Dict[str, Any] = None) -> Any:
        service = await cls._get_service()
        if not service:
            return {"error": "Emby service not configured"}
        
        custom_headers = {
            "X-Emby-Token": service.api_key,
            "X-Emby-Client": "Emby Web",
            "X-Emby-Device-Name": "Chrome Windows",
            "X-Emby-Device-Id": "lens-web-client",
            "X-Emby-Client-Version": "4.9.3.0",
            "X-Emby-Language": "zh-cn"
        }
        
        full_endpoint = f"/user_usage_stats/{endpoint}"
        if endpoint.startswith("/"):
            full_endpoint = endpoint
            
        url = f"{service.base_url}{full_endpoint}"
        full_params = {"api_key": service.api_key}
        if params:
            full_params.update(params)

        try:
            async with service._get_client() as client:
                response = await client.request("GET", url, params=full_params, headers=custom_headers)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    async def post_report_data(cls, endpoint: str, json_data: Dict[str, Any] = None, params: Dict[str, Any] = None) -> Any:
        service = await cls._get_service()
        if not service:
            return {"error": "Emby service not configured"}
            
        custom_headers = {
            "X-Emby-Token": service.api_key,
            "X-Emby-Client": "Emby Web",
            "X-Emby-Device-Name": "Chrome Windows",
            "X-Emby-Device-Id": "lens-web-client",
            "X-Emby-Client-Version": "4.9.3.0"
        }

        full_endpoint = f"/user_usage_stats/{endpoint}"
        if endpoint.startswith("/"):
            full_endpoint = endpoint
            
        url = f"{service.base_url}{full_endpoint}"
        full_params = {"api_key": service.api_key}
        if params:
            full_params.update(params)

        try:
            async with service._get_client() as client:
                resp = await client.request("POST", url, params=full_params, json=json_data, headers=custom_headers)
                if resp.status_code in [200, 204]:
                    return resp.json() if resp.content else {"success": True}
                return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    async def get_user_activity(cls, days: int = 28):
        return await cls.get_report_data("user_activity", {"days": days})

    @classmethod
    async def get_user_list(cls):
        return await cls.get_report_data("user_list")

    @classmethod
    async def get_play_activity(cls, item_type: str = "Episode", days: int = 28):
        return await cls.get_report_data("PlayActivity", {"filter": item_type, "days": days, "data_type": "time"})

    @classmethod
    async def get_session_list(cls):
        return await cls.get_report_data("session_list")

    @classmethod
    async def get_plugin_config(cls):
        return await cls.get_report_data("/System/Configuration/playback_reporting")

    @classmethod
    async def get_type_filters(cls):
        return await cls.get_report_data("type_filter_list")

    @classmethod
    async def get_user_playlist(cls, days: int = 28):
        return await cls.get_report_data("UserPlaylist", {"aggregate_data": "true", "days": days})

    @classmethod
    async def get_user_info(cls, user_id: str):
        service = await cls._get_service()
        if not service: return None
        resp = await service._request("GET", f"/Users/{user_id}")
        return resp.json() if resp and resp.status_code == 200 else None

    @classmethod
    async def get_report_items(cls, parent_id: str = "0"):
        return await cls.get_report_data("get_items", {"parent": parent_id})

    @classmethod
    async def update_plugin_config(cls, config_data: Dict[str, Any]):
        return await cls.post_report_data("/System/Configuration/playback_reporting", json_data=config_data)

    @classmethod
    async def get_breakdown_report(cls, report_type: str, days: int = 28, user_id: str = None):
        params = {"days": days}
        if user_id:
            params["user_id"] = user_id
        if report_type == "HourlyReport":
            params["filter"] = "Episode"
        return await cls.get_report_data(report_type, params)

    @classmethod
    async def submit_custom_query(cls, query: str):
        return await cls.post_report_data("submit_custom_query", json_data={"CustomQueryString": query})

    @classmethod
    async def get_library_summary(cls):
        service = await cls._get_service()
        if not service: return None
        try:
            async def get_count(params):
                resp = await service._request("GET", "/Items", params={"Recursive": "true", "IncludeItemTypes": "Movie,Episode", **params})
                return resp.json().get("TotalRecordCount", 0) if resp and resp.status_code == 200 else 0
            return {
                "total": await get_count({}),
                "is4k": await get_count({"VideoResolution": "4000"}),
                "isHdr": await get_count({"HasHdr": "true"}),
                "isDv": await get_count({"HasDolbyVision": "true"}),
                "movies": await get_count({"IncludeItemTypes": "Movie"}),
                "episodes": await get_count({"IncludeItemTypes": "Episode"})
            }
        except Exception:
            return {"total": 0, "is4k": 0, "isHdr": 0, "isDv": 0, "movies": 0, "episodes": 0}