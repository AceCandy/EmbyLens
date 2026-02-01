import request from '../utils/request'

export const pgsqlApi = {
  getHosts: () => request.get('/api/pgsql/hosts'),
  getDatabases: (config: any) => request.post('/api/pgsql/databases', config),
}
