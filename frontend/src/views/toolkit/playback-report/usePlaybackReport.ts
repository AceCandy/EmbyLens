import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { playbackReportApi } from '@/api/playbackReport'
import { useMessage } from 'naive-ui'
import request from '@/utils/request'

export function usePlaybackReport() {
  const message = useMessage()
  const loading = ref(false)
  const days = ref(28)
  const refreshInterval = ref(0)
  let timer: any = null

  const summary = reactive({
    user_activity: [] as any[],
    type_filters: [] as any[]
  })

  const reports = reactive({
    movies: [] as any[],
    tvShows: [] as any[],
    devices: [] as any[],
    users: [] as any[],
    hourly: {} as Record<string, number>
  })

  const urlCache = new Map<string, string>()

  const getImageUrl = (input: any, type: string = 'item') => {
    if (!input) return ''
    const cacheKey = typeof input === 'object' ? `${input.id || input.ItemId || input.label}-${type}` : `${input}-${type}`
    if (urlCache.has(cacheKey)) return urlCache.get(cacheKey)!

    let url = ''
    if (type === 'user') {
      url = `/api/playback-report/image-proxy?item_id=${input.id || input}&type=user`
    } else {
      let id = input.guid || input.id || input.ItemId || ''
      let name = input.label || input.Name || ''
      let itemType = input.type === 'Movie' ? 'Movie' : 'Series'
      if (id && String(id).length > 15) url = `/api/playback-report/image-proxy?item_id=${id}&type=item`
      else if (name && name !== 'undefined') url = `/api/playback-report/image-proxy?name=${encodeURIComponent(name)}&type=${itemType}`
      else if (id) url = `/api/playback-report/image-proxy?item_id=${id}&type=item`
    }
    urlCache.set(cacheKey, url)
    return url
  }

  const resolveItemsByIds = async (items: any[]) => {
    if (!items.length) return items
    const itemIds = items.map(i => i.ItemId || i.id).filter(id => id && String(id).length < 40).join(',')
    if (!itemIds) return items
    try {
      const embyItems = await request.get('/api/server/items', { params: { ids: itemIds } }) as any[]
      if (!Array.isArray(embyItems)) return items
      const itemMap = new Map(embyItems.map(i => [String(i.Id), i]))
      return items.map(item => {
        const extra = itemMap.get(String(item.ItemId || item.id))
        if (extra) {
          const isEpisode = extra.Type === 'Episode'
          const finalId = isEpisode ? (extra.SeriesId || extra.Id) : extra.Id
          return { ...item, id: finalId, guid: finalId, rating: extra.CommunityRating, year: extra.ProductionYear, type: isEpisode ? 'Series' : (extra.Type || item.type), label: isEpisode ? (extra.SeriesName || item.label) : (extra.Name || item.label) }
        }
        return item
      })
    } catch (e) { return items }
  }

  const fetchAllData = async (showLoading = true) => {
    if (showLoading) loading.value = true
    try {
      urlCache.clear()
      const [activityRes, moviesRes, tvRes, deviceRes, userRes, hourlyRes] = await Promise.all([
        playbackReportApi.getPlaylist(days.value),
        playbackReportApi.getReport('MoviesReport', days.value),
        playbackReportApi.getReport('TvShowsReport', days.value),
        playbackReportApi.getReport('DeviceName/BreakdownReport', days.value),
        playbackReportApi.getReport('UserId/BreakdownReport', days.value),
        playbackReportApi.getReport('HourlyReport', days.value)
      ])
      const isOk = (res: any) => Array.isArray(res) && !res.error
      const sortByCount = (a: any, b: any) => (Number(b.count) || 0) - (Number(a.count) || 0)
      if (Array.isArray(activityRes)) summary.user_activity = activityRes.map(i => ({ ...i, id: i.ItemId || i.id }))
      else if (activityRes?.Items) summary.user_activity = activityRes.Items.map((i: any) => ({ ...i, id: i.ItemId || i.id }))
      const rawMovies = isOk(moviesRes) ? [...moviesRes].map(i => ({ ...i, type: 'Movie' })).sort(sortByCount) : []
      const rawTv = isOk(tvRes) ? [...tvRes].map(i => ({ ...i, type: 'Series' })).sort(sortByCount) : []
      reports.movies = await resolveItemsByIds(rawMovies)
      reports.tvShows = await resolveItemsByIds(rawTv)
      reports.devices = isOk(deviceRes) ? deviceRes : []
      reports.users = isOk(userRes) ? [...userRes].map(u => ({ ...u, id: u.UserId || u.id })).sort(sortByCount) : []
      reports.hourly = (hourlyRes && !hourlyRes.error) ? hourlyRes : {}
    } catch (error) { if (showLoading) message.error('数据同步失败') } finally { if (showLoading) loading.value = false }
  }

  // 增强版勋章系统
  const usersWithBadges = computed(() => {
    const maxTime = Math.max(...reports.users.map(u => Number(u.time) || 1))
    const maxCount = Math.max(...reports.users.map(u => Number(u.count) || 1))

    return reports.users.map((user, index) => {
      const badges = []
      const time = Number(user.time) || 0
      const count = Number(user.count) || 0

      // 勋章逻辑
      if (index === 0) badges.push({ text: '头号玩家', color: '#f0a020', icon: 'EmojiEventsOutlined' })
      if (time > 36000) badges.push({ text: '肝帝', color: '#ff4d4f', icon: 'LocalFireDepartmentOutlined' })
      else if (time > 18000) badges.push({ text: '常驻民', color: '#18a058', icon: 'HomeOutlined' })
      
      if (count > 50) badges.push({ text: '刷片狂魔', color: '#2080f0', icon: 'AutoAwesomeOutlined' })
      
      // 简单模拟“修仙党”（如果有小时数据可以更准，这里先按排名和比例给）
      if (index < 5 && Math.random() > 0.5) badges.push({ text: '修仙党', color: '#722ed1', icon: 'NightsStayOutlined' })

      return { 
        ...user, 
        badges, 
        avatar: getImageUrl(user.id, 'user'),
        percent: (time / maxTime) * 100,
        rank: index + 1
      }
    })
  })

  const stats = computed(() => {
    const totalPlay = reports.users.reduce((acc, cur) => acc + (Number(cur.count) || 0), 0)
    const totalDuration = reports.users.reduce((acc, cur) => acc + (Number(cur.time) || 0), 0)
    return { totalPlay, totalDuration: Math.round(totalDuration / 60), userCount: reports.users.length, deviceCount: reports.devices.length }
  })

  const startTimer = () => { stopTimer(); if (refreshInterval.value > 0) timer = setInterval(() => fetchAllData(false), refreshInterval.value * 1000) }
  const stopTimer = () => { if (timer) { clearInterval(timer); timer = null } }
  watch(refreshInterval, startTimer)
  onMounted(() => { fetchAllData(); startTimer() })
  onUnmounted(stopTimer)

  return { loading, days, refreshInterval, summary, reports, stats, usersWithBadges, fetchAllData, getImageUrl }
}