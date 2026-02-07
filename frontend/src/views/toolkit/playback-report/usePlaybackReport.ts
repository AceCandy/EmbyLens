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

  // 核心修复：更鲁棒的图片生成器
  const getImageUrl = (input: any, type: string = 'item') => {
    if (!input) return ''
    const cacheKey = typeof input === 'object' 
      ? `${input.id || input.guid || input.searchName || input.label}-${type}`
      : `${input}-${type}`
    if (urlCache.has(cacheKey)) return urlCache.get(cacheKey)!

    let url = ''
    if (type === 'user') {
      const userId = typeof input === 'object' ? (input.id || input.UserId || input.user_id) : input
      url = `/api/playback-report/image-proxy?item_id=${userId}&type=user`
    } else {
      const id = input.guid || input.id || input.ItemId || input.item_id || ''
      // 关键：优先使用干净的搜索名称，避免使用带 S01E01 的装饰名称
      const name = input.searchName || input.label || input.Name || input.item_name || ''
      const itemType = input.type === 'Movie' ? 'Movie' : 'Series'

      if (id && String(id).length > 15) {
        url = `/api/playback-report/image-proxy?item_id=${id}&type=item`
      } else if (name && name !== 'undefined') {
        url = `/api/playback-report/image-proxy?name=${encodeURIComponent(name)}&type=${itemType}`
      } else if (id) {
        url = `/api/playback-report/image-proxy?item_id=${id}&type=item`
      }
    }
    urlCache.set(cacheKey, url)
    return url
  }

  // 拿着 itemid 去找对应的内容，并处理剧集穿透
  const resolveItemsByIds = async (items: any[]) => {
    if (!items.length) return items
    const itemIds = items.map(i => i.id || i.ItemId || i.item_id).filter(id => id).join(',')
    if (!itemIds) return items

    try {
      // 这里的返回结果 ID 是 Guid
      const embyItems = await request.get('/api/server/items', { params: { ids: itemIds } }) as any[]
      if (!Array.isArray(embyItems)) return items
      
      // 关键：由于输入的可能是数字 ID，返回的是 Guid，我们需要通过名称或其它方式匹配，或者让后端增强
      // 这里我们假设返回顺序或通过 search 匹配更稳妥，但最稳的是直接用这个 embyItems 里的数据。
      // 我们创建一个根据原始 ID 匹配的 Map。
      // Emby API /Items 如果传入 Ids，通常返回的顺序和 Ids 一致，或者我们可以通过匹配找到。
      
      return items.map(item => {
        const originalId = String(item.id || item.ItemId || item.item_id)
        // 尝试在返回结果中寻找（有些 Emby 版本会在返回中包含原始 ID，如果没有就靠名称匹配）
        const extra = embyItems.find(i => String(i.Id) === originalId || i.Name === (item.label || item.item_name))
        
        if (extra) {
          const isEpisode = extra.Type === 'Episode'
          const finalId = isEpisode ? (extra.SeriesId || extra.Id) : extra.Id
          
          let fullLabel = extra.Name || item.label || item.item_name
          let searchName = extra.Name // 默认搜索名
          
          if (isEpisode) {
            const season = String(extra.ParentIndexNumber || 1).padStart(2, '0')
            const episode = String(extra.IndexNumber || 1).padStart(2, '0')
            const seriesName = extra.SeriesName || ''
            fullLabel = `${seriesName} - S${season}E${episode} - ${extra.Name}`
            searchName = seriesName // 剧集应该搜索系列名
          }

          return {
            ...item,
            id: finalId,
            guid: finalId,
            rating: extra.CommunityRating,
            year: extra.ProductionYear,
            type: isEpisode ? 'Series' : (extra.Type || item.type),
            label: fullLabel,
            searchName: searchName // 存一个干净的名称用于搜图片
          }
        }
        return item
      })
    } catch (e) {
      return items
    }
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

      if (isOk(activityRes)) {
        const rawActivities = (activityRes as any[]).map(i => ({
          ...i,
          id: i.item_id || i.ItemId || i.id,
          label: i.item_name || i.label || i.Name,
          type: i.item_type || i.ItemType || i.type
        }))
        summary.user_activity = await resolveItemsByIds(rawActivities)
      }

      const rawMovies = isOk(moviesRes) ? [...moviesRes].map(i => ({ ...i, type: 'Movie' })).sort(sortByCount) : []
      const rawTv = isOk(tvRes) ? [...tvRes].map(i => ({ ...i, type: 'Series' })).sort(sortByCount) : []
      
      reports.movies = await resolveItemsByIds(rawMovies)
      reports.tvShows = await resolveItemsByIds(rawTv)
      
      reports.devices = isOk(deviceRes) ? deviceRes : []
      reports.users = isOk(userRes) ? [...userRes].map(u => ({ ...u, id: u.UserId || u.id })).sort(sortByCount) : []
      reports.hourly = (hourlyRes && !hourlyRes.error) ? hourlyRes : {}

    } catch (error) {
      if (showLoading) message.error('同步失败')
    } finally {
      if (showLoading) loading.value = false
    }
  }

  const usersWithBadges = computed(() => {
    const maxTime = Math.max(...reports.users.map(u => Number(u.time) || 1))
    return reports.users.map((user, index) => {
      const badges = []
      const time = Number(user.time) || 0
      if (index === 0) badges.push({ text: '头号玩家', color: '#f0a020', icon: 'EmojiEventsOutlined' })
      if (time > 36000) badges.push({ text: '肝帝', color: '#ff4d4f', icon: 'LocalFireDepartmentOutlined' })
      return { ...user, badges, avatar: getImageUrl(user.id, 'user'), percent: (time / maxTime) * 100, rank: index + 1 }
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
