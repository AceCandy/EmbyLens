import request from '../utils/request'

export const playbackReportApi = {
  // 获取播放活动流水
  getActivity: (days: number = 28) => 
    request.get('/api/playback-report/activity', { params: { days } }),

  // 获取用户统计名单
  getUsers: () => 
    request.get('/api/playback-report/users'),

  // 获取播放活跃度统计 (图表数据)
  getPlayActivity: (itemType: string = 'Episode', days: number = 28) => 
    request.get('/api/playback-report/play-activity', { params: { item_type: itemType, days } }),

  // 获取特定报表
  getReport: (reportType: string, days: number = 28, userId?: string) => {
    // 处理 reportType 中的斜杠，后端接收带横杠的参数
    const formattedType = reportType.replace(/\//g, '-')
    return request.get(`/api/playback-report/reports/${formattedType}`, { 
      params: { days, user_id: userId } 
    })
  },

  // 获取特定用户信息
  getUserInfo: (userId: string) =>
    request.get(`/api/playback-report/users/${userId}`),

  // 获取报表项
  getReportItems: (parentId: string = '0') =>
    request.get('/api/playback-report/report-items', { params: { parent_id: parentId } }),

  // 更新配置
  updateConfig: (config: any) =>
    request.post('/api/playback-report/config', config),

  // 获取播放概览
  getSummary: (days: number = 28) => 
    request.get('/api/playback-report/summary', { params: { days } }),

  // 自定义 SQL 查询
  customQuery: (query: string) => 
    request.post('/api/playback-report/query', { query }),

  // 获取用户播放清单统计
  getPlaylist: (days: number = 28) => 
    request.get('/api/playback-report/playlist', { params: { days } })
}