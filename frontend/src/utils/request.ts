import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { createDiscreteApi } from 'naive-ui'

// 使用 Naive UI 的脱离上下文 API 来在非组件文件中显示消息
const { message } = createDiscreteApi(['message'])

const service: AxiosInstance = axios.create({
  baseURL: '/',
  timeout: 60000 // 1分钟超时
})

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 Token (键名与 navigationStore.ts 中保持一致)
    const token = localStorage.getItem('lens_access_token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 这里的 response.data 直接就是后端返回的内容
    return response.data
  },
  (error) => {
    const { response } = error
    if (response) {
      const status = response.status
      const detail = response.data?.detail || response.data?.message || '服务器内部错误'

      switch (status) {
        case 401:
          // 未登录或 Token 过期
          // 清除无效 Token，防止后续请求继续携带失效 Token 导致死循环
          localStorage.removeItem('lens_access_token')
          
          if (!window.location.pathname.includes('/login')) {
            // 提示用户
            message.error('登录状态已失效，正在尝试重新加载...')
            // 给用户一点反应时间，然后尝试刷新或跳转
            setTimeout(() => {
              window.location.reload()
            }, 1500)
          }
          break
        case 403:
          message.error('权限不足，拒绝访问')
          break
        case 404:
          message.error('请求资源不存在')
          break
        case 500:
          message.error('后端服务异常: ' + detail)
          break
        default:
          message.error(detail)
      }
    } else {
      message.error('网络连接超时或异常，请检查后端服务是否启动')
    }
    return Promise.reject(error)
  }
)

export default service