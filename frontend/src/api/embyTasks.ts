import request from '../utils/request'

export const embyTasksApi = {
  // 获取任务列表
  list: () => request.get('/api/emby-tasks'),
  
  // 启动任务
  run: (id: string) => request.post(`/api/emby-tasks/${id}/run`),
  
  // 停止任务
  stop: (id: string) => request.delete(`/api/emby-tasks/${id}/run`)
}
