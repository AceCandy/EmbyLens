import request from '@/utils/request'

export const actorLabApi = {
  analyze: (params: any) => request.get('/api/actor-lab/analyze', { params })
}
