import httpx
import json
from typing import List, Dict, Any, Optional
from app.utils.logger import logger
from app.utils.http_client import get_async_client
from app.core.config_manager import get_config

class EmbyLibraryService:
    def __init__(self, url: str, api_key: str):
        self.url = url.strip().rstrip('/')
        if self.url.endswith('/emby'):
            self.base_url = self.url
        else:
            self.base_url = f"{self.url}/emby"
            
        self.api_key = api_key.strip() if api_key else ""
        self.headers = {
            "X-Emby-Token": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Emby-Client": "Emby Web",
            "X-Emby-Device-Name": "Lens Manager",
            "X-Emby-Client-Version": "4.10.0.2"
        }

    def _get_client(self) -> httpx.AsyncClient:
        config = get_config()
        proxy_cfg = config.get("proxy", {})
        use_proxy = not proxy_cfg.get("exclude_emby", True)
        return get_async_client(timeout=30.0, headers=self.headers, use_proxy=use_proxy)

    async def _request(self, method: str, endpoint: str, params: Dict = None, json_data: Dict = None):
        url = f"{self.base_url}{endpoint}"
        full_params = {"api_key": self.api_key}
        if params:
            full_params.update(params)
            
        logger.info(f"┃  ┣ 🚀 [Emby Library API 执行] {method} {url}")
        if params:
            logger.info(f"┃  ┃  📍 Params: {params}")
        if json_data:
            logger.info(f"┃  ┃  📦 Payload: {json_data}")

        try:
            async with self._get_client() as client:
                response = await client.request(method, url, params=full_params, json=json_data)
                res_text = response.text if response.text else "(No Content)"
                logger.info(f"┃  ┃  📥 [Emby 响应] Status: {response.status_code} | Body: {res_text[:200]}")
                return response
        except Exception as e:
            logger.error(f"┃  ┃  ❌ Emby Library API 异常 ({type(e).__name__}): {str(e)}")
            return None

    async def get_libraries(self) -> List[Dict[str, Any]]:
        resp = await self._request("GET", "/Library/VirtualFolders")
        return resp.json() if resp and resp.status_code == 200 else []

    async def add_library(self, name: str, collection_type: str, path: str = None) -> bool:
        params = {
            "Name": name, 
            "CollectionType": collection_type, 
            "RefreshLibrary": "true"
        }
        body = {
            "LibraryOptions": {
                "PathInfos": [{"Path": path}] if path else []
            }
        }
        resp = await self._request("POST", "/Library/VirtualFolders", params=params, json_data=body)
        return resp is not None and resp.status_code in [200, 204]

    async def update_library_options(self, library_data: Dict[str, Any]) -> bool:
        resp = await self._request("POST", "/Library/VirtualFolders", params={"refreshLibrary": "true"}, json_data=library_data)
        return resp is not None and resp.status_code in [200, 204]

    async def delete_library(self, name: str, library_id: str) -> bool:
        """
        根据抓包修正的删除逻辑:
        Method: POST
        URL: /Library/VirtualFolders/Delete
        Params: refreshLibrary=true, id=xxx, name=xxx
        """
        params = {
            'refreshLibrary': 'true',
            'id': library_id,
            'name': name
        }
        resp = await self._request("POST", "/Library/VirtualFolders/Delete", params=params)
        return resp is not None and resp.status_code in [200, 204]

def get_emby_library_service(server_id: str = None) -> Optional[EmbyLibraryService]:
    config = get_config()
    servers = config.get("emby_servers", [])
    
    target_server = None
    if server_id:
        target_server = next((s for s in servers if s.get("id") == server_id), None)
    else:
        active_id = config.get("active_server_id")
        target_server = next((s for s in servers if s.get("id") == active_id), None)
    
    if not target_server and servers:
        target_server = servers[0]
        
    if not target_server:
        return None
        
    token = target_server.get("session_token") or target_server.get("api_key")
    return EmbyLibraryService(
        url=target_server.get("url", ""),
        api_key=token
    )
