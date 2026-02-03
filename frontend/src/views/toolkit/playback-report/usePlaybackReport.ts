import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { playbackReportApi } from '@/api/playbackReport'
import { useMessage } from 'naive-ui'

export function usePlaybackReport() {
  const message = useMessage()
  const loading = ref(false)
  const days = ref(28)
  const refreshInterval = ref(0) // 自动刷新间隔 (秒)，0 为禁用
  let timer: any = null

  // 基础统计数据
  const summary = reactive({
    user_activity: [] as any[],
    type_filters: [] as any[]
  })

  // 报表数据
  const reports = reactive({
    movies: [] as any[],
    tvShows: [] as any[],
    devices: [] as any[],
    methods: [] as any[],
    itemTypes: [] as any[],
    users: [] as any[],
    hourly: {} as any
  })

  // 获取所有统计数据
  const fetchAllData = async (showLoading = true) => {
    if (showLoading) loading.value = true
    try {
      const [
        activityRes,
        moviesRes,
        tvRes,
        deviceRes,
        methodRes,
        itemTypeRes,
        userRes,
        hourlyRes
      ] = await Promise.all([
        playbackReportApi.getPlaylist(days.value), // 使用 UserPlaylist 接口
        playbackReportApi.getReport('MoviesReport', days.value),
        playbackReportApi.getReport('TvShowsReport', days.value),
        playbackReportApi.getReport('DeviceName/BreakdownReport', days.value),
        playbackReportApi.getReport('PlaybackMethod/BreakdownReport', days.value),
        playbackReportApi.getReport('ItemType/BreakdownReport', days.value),
        playbackReportApi.getReport('UserId/BreakdownReport', days.value),
        playbackReportApi.getReport('HourlyReport', days.value)
      ])

      // 调试：打印 Playlist 数据的原始结构
      console.log('DEBUG: Playlist Data Raw:', activityRes)

      const isOk = (res: any) => Array.isArray(res) && !res.error

      // 处理 Playlist 数据
      if (Array.isArray(activityRes)) {
        summary.user_activity = [...activityRes]
      } else if (activityRes && Array.isArray(activityRes.Items)) {
        summary.user_activity = [...activityRes.Items]
      } else {
        summary.user_activity = []
      }
      
      // 排序函数：优先按次数，其次按时长
      const sortByCount = (a: any, b: any) => {
        const countDiff = (Number(b.count) || 0) - (Number(a.count) || 0)
        if (countDiff !== 0) return countDiff
        return (Number(b.time) || 0) - (Number(a.time) || 0)
      }

      // 处理各项报表并强制排序
      reports.movies = isOk(moviesRes) ? [...moviesRes].sort(sortByCount) : []
      reports.tvShows = isOk(tvRes) ? [...tvRes].sort(sortByCount) : []
      reports.devices = isOk(deviceRes) ? deviceRes : []
      reports.methods = isOk(methodRes) ? methodRes : []
      reports.itemTypes = isOk(itemTypeRes) ? itemTypeRes : []
      reports.users = isOk(userRes) ? [...userRes].sort(sortByCount) : []
      reports.hourly = (hourlyRes && !hourlyRes.error) ? hourlyRes : {}

      console.log('📊 数据更新完毕:', { 
        活动: summary.user_activity.length, 
        用户: reports.users.length 
      })
    } catch (error) {
      console.error('❌ 获取播放统计失败:', error)
      if (showLoading) message.error('获取播放统计数据失败')
    } finally {
      if (showLoading) loading.value = false
    }
  }

  // 自动刷新逻辑
  const startTimer = () => {
    stopTimer()
    if (refreshInterval.value > 0) {
      console.log(`⏱️ 已开启自动刷新: ${refreshInterval.value}s`)
      timer = setInterval(() => {
        fetchAllData(false) // 自动刷新不显示全屏 loading
      }, refreshInterval.value * 1000)
    }
  }

  const stopTimer = () => {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  watch(refreshInterval, () => {
    startTimer()
  })

  // 核心统计指标计算
  const stats = computed(() => {
    const totalPlay = reports.users.reduce((acc, cur) => acc + (Number(cur.count) || 0), 0)
    const totalDuration = reports.users.reduce((acc, cur) => acc + (Number(cur.time) || 0), 0)
    return {
      totalPlay,
      totalDuration: Math.round(totalDuration / 60), // 从秒转换为分钟
      userCount: reports.users.length,
      deviceCount: reports.devices.length,
      itemTypeCount: reports.itemTypes.length
    }
  })

  // 图表配置
  const deviceChartOption = computed(() => {
    const data = reports.devices
      .sort((a, b) => (b.count || 0) - (a.count || 0))
      .slice(0, 10)
      .map((item: any) => ({ name: item.label || '未知', value: item.count || 0 }))
    return {
      title: { text: '播放设备排行 (TOP 10)', left: 'center', textStyle: { color: '#ccc', fontSize: 14 } },
      tooltip: { trigger: 'item', formatter: '{b}: {c}次 ({d}%)' },
      legend: { bottom: '0', textStyle: { color: '#aaa', fontSize: 10 } },
      series: [{ type: 'pie', radius: ['40%', '70%'], avoidLabelOverlap: false, itemStyle: { borderRadius: 10, borderColor: '#18181c', borderWidth: 2 }, label: { show: false }, data }]
    }
  })

  const hourlyChartOption = computed(() => {
    const hours = Array.from({ length: 24 }, (_, i) => `${i}h`)
    const data = new Array(24).fill(0)
    if (reports.hourly && typeof reports.hourly === 'object' && !Array.isArray(reports.hourly)) {
      Object.entries(reports.hourly).forEach(([key, val]) => {
        const parts = key.split('-')
        if (parts.length === 2) {
          const hour = parseInt(parts[1])
          if (!isNaN(hour) && hour >= 0 && hour < 24) data[hour] += Number(val) || 0
        }
      })
    }
    return {
      title: { text: '24小时播放热度', left: 'center', textStyle: { color: '#ccc', fontSize: 14 } },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: hours },
      yAxis: { type: 'value' },
      series: [{ data, type: 'line', smooth: true, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#0078d4' }, { offset: 1, color: 'transparent' }] } }, itemStyle: { color: '#0078d4' } }]
    }
  })

  onMounted(() => {
    fetchAllData()
    startTimer()
  })

  onUnmounted(() => {
    stopTimer()
  })

  return {
    loading,
    days,
    refreshInterval,
    summary,
    reports,
    stats,
    fetchAllData,
    deviceChartOption,
    hourlyChartOption
  }
}