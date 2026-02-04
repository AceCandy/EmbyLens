import request from '@/utils/request'

export function listEmbyBackups(category: 'users' | 'libraries') {
  return request({
    url: '/api/emby-backup/list',
    method: 'get',
    params: { category }
  })
}

export function createEmbyBackup(category: 'users' | 'libraries', id: string, name: string, serverId?: string) {
  return request({
    url: '/api/emby-backup/create',
    method: 'post',
    params: { category, id, name, server_id: serverId }
  })
}

export function restoreEmbyBackup(category: 'users' | 'libraries', filename: string, serverId?: string) {
  return request({
    url: '/api/emby-backup/restore',
    method: 'post',
    params: { category, filename, server_id: serverId }
  })
}

export function deleteEmbyBackup(category: 'users' | 'libraries', filename: string) {
  return request({
    url: '/api/emby-backup/delete',
    method: 'delete',
    params: { category, filename }
  })
}

export function clearEmbyBackups(category: 'users' | 'libraries') {
  return request({
    url: '/api/emby-backup/clear',
    method: 'delete',
    params: { category }
  })
}
