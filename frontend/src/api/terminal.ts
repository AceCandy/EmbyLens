import request from '../utils/request'

export interface TerminalHost {
  id: number
  name: string
  host: string
  port: number
  username: string
  auth_type: string
  password?: string
  private_key?: string
}

export const terminalApi = {
  // 主机管理
  getHosts: () => request.get<TerminalHost[]>('/api/terminal/hosts'),
  createHost: (data: any) => request.post('/api/terminal/hosts', data),
  updateHost: (id: number, data: any) => request.put(`/api/terminal/hosts/${id}`, data),
  deleteHost: (id: number) => request.delete(`/api/terminal/hosts/${id}`),

  // 快速命令
  getCommands: () => request.get('/api/terminal/commands'),
  saveCommand: (data: any) => data.id ? request.put(`/api/terminal/commands/${data.id}`, data) : request.post('/api/terminal/commands', data),
  deleteCommand: (id: number) => request.delete(`/api/terminal/commands/${id}`),
  reorderCommands: (ids: number[]) => request.post('/api/terminal/commands/reorder', ids),

  // 文件管理 (统一函数名以匹配 FileManager Provider 规范)
  ls: (hostId: number | string, path: string) => 
    request.get(`/api/files/${hostId}/ls`, { params: { path } }),
  
  read: (hostId: number | string, path: string) => 
    request.get(`/api/files/${hostId}/read`, { params: { path } }),
  
  write: (hostId: number | string, path: string, content: string) => 
    request.post(`/api/files/${hostId}/write`, { path, content }),
  
  action: (hostId: number | string, action: string, path: string, target?: string) => 
    request.post(`/api/files/${hostId}/action`, { action, path, target }),
  
  chmod: (hostId: number | string, data: any) => 
    request.post(`/api/files/${hostId}/chmod`, data),

  upload: (hostId: number | string, path: string, files: File[]) => {
    const formData = new FormData()
    formData.append('path', path)
    files.forEach(file => formData.append('files', file))
    return request.post(`/api/files/${hostId}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 0 // 上传大文件不设超时
    })
  },

  downloadUrl: (hostId: number | string, path: string) => 
    `/api/files/${hostId}/download?path=${encodeURIComponent(path)}`
}