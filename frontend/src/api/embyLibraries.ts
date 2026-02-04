import request from '@/utils/request'

export function listEmbyLibraries(serverId?: string) {
  return request({
    url: '/api/emby-libraries/list',
    method: 'get',
    params: { server_id: serverId }
  })
}

export function addEmbyLibrary(name: string, collectionType: string, path?: string, serverId?: string) {
  return request({
    url: '/api/emby-libraries/add',
    method: 'post',
    params: { name, collection_type: collectionType, path, server_id: serverId }
  })
}

export function updateEmbyLibrary(libraryData: any, server_id?: string) {
  return request({
    url: '/api/emby-libraries/update',
    method: 'post',
    data: libraryData,
    params: { server_id }
  })
}

export function removeEmbyLibrary(name: string, id: string, serverId?: string) {
  return request({
    url: '/api/emby-libraries/remove',
    method: 'delete',
    params: { name, id, server_id: serverId }
  })
}