<template>
  <div class="playback-report-container">
    <n-space vertical size="large">
      <!-- 头部控制栏 -->
      <n-card size="small">
        <n-space align="center" justify="space-between">
          <n-space align="center">
            <n-icon size="24" color="#0078d4">
              <BarChartOutlined />
            </n-icon>
            <n-text strong style="font-size: 18px">播放统计报表 (Playback Reporting)</n-text>
          </n-space>
          <n-space align="center">
            <n-text depth="3" style="font-size: 13px; margin-right: 20px;">
              💡 注意：此功能依赖于 Emby 服务器安装 <b>Playback Reporting</b> 插件。
            </n-text>
            <n-text>自动刷新：</n-text>
            <n-input-number
              v-model:value="refreshInterval"
              :min="0"
              :max="3600"
              placeholder="0禁用"
              style="width: 100px"
              size="small"
            >
              <template #suffix>s</template>
            </n-input-number>
            <n-text>周期：</n-text>
            <n-select
              v-model:value="days"
              :options="dayOptions"
              style="width: 110px"
              size="small"
              @update:value="fetchAllData"
            />
            <n-button type="primary" size="small" :loading="loading" @click="fetchAllData">
              刷新
            </n-button>
          </n-space>
        </n-space>
      </n-card>

      <!-- 核心指标卡片 -->
      <n-grid :cols="4" :x-gap="12" :y-gap="12">
        <n-gi>
          <n-card title="总播放次数" size="small">
            <n-statistic :value="stats.totalPlay" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="播放总时长 (分钟)" size="small">
            <n-statistic :value="stats.totalDuration" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="活跃用户数" size="small">
            <n-statistic :value="stats.userCount" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="覆盖设备数" size="small">
            <n-statistic :value="stats.deviceCount" />
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 图表与用户排行区域 (三列并排) -->
      <n-grid :cols="3" :x-gap="12" :y-gap="12">
        <n-gi>
          <n-card title="24小时播放热度" size="small" class="fixed-height-card">
            <v-chart class="chart" :option="hourlyChartOption" autoresize />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="设备/平台比例" size="small" class="fixed-height-card">
            <v-chart class="chart" :option="deviceChartOption" autoresize />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="用户播放活跃度排行 (TOP 20)" size="small" class="fixed-height-card" content-style="padding: 0">
            <n-scrollbar style="max-height: 430px">
              <n-table :bordered="false" :single-line="false" size="small">
                <thead>
                  <tr>
                    <th>排名</th>
                    <th>用户</th>
                    <th>次数</th>
                    <th>时长</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(user, index) in reports.users.slice(0, 20)" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td><n-text strong color="#0078d4" depth="2">{{ user.label }}</n-text></td>
                    <td>{{ user.count }}</td>
                    <td>{{ typeof user.time === 'number' ? Math.round(user.time / 60) : user.time }}m</td>
                  </tr>
                </tbody>
              </n-table>
            </n-scrollbar>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 最近活动与排行榜区域 (三列并排) -->
      <n-grid :cols="3" :x-gap="12" :y-gap="12">
        <n-gi>
          <n-card size="small" class="fixed-height-card" content-style="padding: 0">
            <template #header>
              <n-space align="center" :size="4">
                <n-icon><HistoryOutlined /></n-icon>
                <span>最近播放活动</span>
              </n-space>
            </template>
            <n-scrollbar style="max-height: 430px">
              <n-list hoverable clickable>
                <n-list-item v-for="(activity, index) in summary.user_activity" :key="index">
                  <n-thing :title="activity.item_name || '未知项目'" :description="activity.user_name || '未知用户'">
                    <template #header-extra>
                      <n-tag size="small" :type="activity.item_type === 'Movie' ? 'info' : 'success'">
                        {{ activity.duration ? Math.round(activity.duration / 60) + 'm' : '播放中' }}
                      </n-tag>
                    </template>
                    <div style="font-size: 12px; color: #888">
                      {{ activity.date }} {{ activity.time }} | {{ activity.item_type }}
                    </div>
                  </n-thing>
                </n-list-item>
                <n-empty v-if="summary.user_activity.length === 0" description="暂无播放记录" style="padding: 20px" />
              </n-list>
            </n-scrollbar>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card size="small" class="fixed-height-card" content-style="padding: 0">
            <template #header>
              <n-space align="center" :size="4">
                <n-icon><MovieOutlined /></n-icon>
                <span>电影播放排行 (Top 10)</span>
              </n-space>
            </template>
            <!-- 移除滚动条，直接显示 10 行 -->
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th style="width: 60%">名称</th>
                  <th>次数</th>
                  <th>时长</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in displayMovies" :key="index">
                  <td style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{ item.label }}</td>
                  <td>{{ item.count }}</td>
                  <td>{{ typeof item.time === 'number' ? Math.round(item.time / 60) : item.time }}m</td>
                </tr>
              </tbody>
            </n-table>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card size="small" class="fixed-height-card" content-style="padding: 0">
            <template #header>
              <n-space align="center" :size="4">
                <n-icon><LiveTvOutlined /></n-icon>
                <span>剧集播放排行 (Top 10)</span>
              </n-space>
            </template>
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th style="width: 60%">名称</th>
                  <th>次数</th>
                  <th>时长</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in displayTvShows" :key="index">
                  <td style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{{ item.label }}</td>
                  <td>{{ item.count }}</td>
                  <td>{{ typeof item.time === 'number' ? Math.round(item.time / 60) : item.time }}m</td>
                </tr>
              </tbody>
            </n-table>
          </n-card>
        </n-gi>
      </n-grid>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  NCard, NSpace, NText, NIcon, NButton, NSelect, NGrid, NGi, NStatistic, NTable,
  NList, NListItem, NThing, NTag, NScrollbar, NEmpty, NInputNumber
} from 'naive-ui'
import { 
  BarChartOutlined, 
  HistoryOutlined, 
  MovieOutlined, 
  LiveTvOutlined 
} from '@vicons/material'
import { usePlaybackReport } from './usePlaybackReport'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent
} from 'echarts/components'

// 注册 ECharts 必须的组件
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  DatasetComponent,
  TransformComponent
])

const {
  loading,
  days,
  refreshInterval,
  summary,
  reports,
  stats,
  fetchAllData,
  deviceChartOption,
  hourlyChartOption
} = usePlaybackReport()

const dayOptions = [
  { label: '最近 7 天', value: 7 },
  { label: '最近 14 天', value: 14 },
  { label: '最近 28 天', value: 28 },
  { label: '最近 90 天', value: 90 },
  { label: '全部历史', value: 3650 }
]

// 填充 10 行逻辑
const displayMovies = computed(() => {
  const list = [...reports.movies.slice(0, 10)]
  while (list.length < 10) {
    list.push({ label: '-', count: '-', time: '-' })
  }
  return list
})

const displayTvShows = computed(() => {
  const list = [...reports.tvShows.slice(0, 10)]
  while (list.length < 10) {
    list.push({ label: '-', count: '-', time: '-' })
  }
  return list
})
</script>

<style scoped>
.playback-report-container {
  padding: 12px;
}
.fixed-height-card {
  height: 480px;
}
.chart {
  height: 430px;
}
/* 确保表格布局固定 */
:deep(.n-table) {
  table-layout: fixed;
}
</style>
