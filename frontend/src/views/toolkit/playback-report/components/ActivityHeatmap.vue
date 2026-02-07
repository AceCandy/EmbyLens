<template>
  <n-card title="24小时播放活跃度" size="small">
    <div class="heatmap-container">
      <v-chart class="chart" :option="chartOption" autoresize />
    </div>
  </n-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NCard } from 'naive-ui'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { VisualMapComponent, GridComponent, TooltipComponent } from 'echarts/components'
import { HeatmapChart } from 'echarts/charts'

use([CanvasRenderer, VisualMapComponent, GridComponent, TooltipComponent, HeatmapChart])

const props = defineProps<{
  hourlyData: Record<string, number>
}>()

const chartOption = computed(() => {
  const hours = Array.from({ length: 24 }, (_, i) => `${i}h`)
  const data: [number, number, number][] = []
  
  // 将 HourlyReport 数据转换为热力图格式 [x, y, value]
  // 这里我们只有一个维度（小时），所以 y 固定为 0
  for (let i = 0; i < 24; i++) {
    const val = props.hourlyData[`Hour-${i}`] || 0
    data.push([i, 0, val])
  }

  const maxValue = Math.max(...data.map(d => d[2]), 1)

  return {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        return `${params.data[0]}:00 - ${params.data[0]}:59<br/>播放量: <b>${params.data[2]}</b>`
      }
    },
    grid: {
      top: '10%',
      bottom: '15%',
      left: '5%',
      right: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: true },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'category',
      data: ['播放量'],
      splitArea: { show: true },
      axisLine: { show: false },
      axisTick: { show: false },
      show: false
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: {
        color: ['#18181c', '#0078d4']
      },
      textStyle: {
        color: '#888'
      }
    },
    series: [
      {
        name: '播放活跃度',
        type: 'heatmap',
        data: data,
        label: {
          show: false
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          borderRadius: 4,
          borderColor: '#18181c',
          borderWidth: 2
        }
      }
    ]
  }
})
</script>

<style scoped>
.heatmap-container {
  height: 200px;
}
.chart {
  height: 100%;
}
</style>
