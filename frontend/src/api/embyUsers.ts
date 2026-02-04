import request from '@/utils/request'

export function listEmbyUsers(serverId?: string) {
  return request({
    url: '/api/emby-users/list',
    method: 'get',
    params: { server_id: serverId }
  })
}

export function createEmbyUser(name: string, serverId?: string) {
  return request({
    url: '/api/emby-users/create',
    method: 'post',
    params: { name, server_id: serverId }
  })
}

export function deleteEmbyUser(userId: string, serverId?: string) {
  return request({
    url: `/api/emby-users/${userId}`,
    method: 'delete',
    params: { server_id: serverId }
  })
}

export function getEmbyUserInfo(userId: string, serverId?: string) {
  return request({
    url: `/api/emby-users/${userId}/info`,
    method: 'get',
    params: { server_id: serverId }
  })
}

export function updateEmbyUserPolicy(userId: string, policy: any, serverId?: string) {
  return request({
    url: `/api/emby-users/${userId}/policy`,
    method: 'post',
    data: policy,
    params: { server_id: serverId }
  })
}

export function updateEmbyUserPassword(userId: string, password: string, serverId?: string) {
  return request({
    url: `/api/emby-users/${userId}/password`,
    method: 'post',
    data: { password },
    params: { server_id: serverId }
  })
}
