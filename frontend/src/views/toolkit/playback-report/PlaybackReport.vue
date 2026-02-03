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

      <!-- 图表区域 -->
      <n-grid :cols="2" :x-gap="12" :y-gap="12">
        <n-gi>
          <n-card title="24小时活跃趋势" size="small">
            <v-chart class="chart" :option="hourlyChartOption" autoresize />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="设备/平台比例" size="small">
            <v-chart class="chart" :option="deviceChartOption" autoresize />
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 用户排行榜 -->
      <n-grid :cols="3" :x-gap="12" :y-gap="12">
        <n-gi :span="2">
          <n-card title="用户播放活跃度排行 (TOP 20)" size="small">
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>用户名称</th>
                  <th>播放次数</th>
                  <th>时长 (分钟)</th>
                  <th>均时</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(user, index) in reports.users.slice(0, 20)" :key="index">
                  <td>{{ index + 1 }}</td>
                  <td><n-text strong color="#0078d4">{{ user.label }}</n-text></td>
                  <td>{{ user.count }}</td>
                  <td>{{ user.time }}</td>
                  <td>{{ user.count > 0 ? Math.round(user.time / user.count) : 0 }}m</td>
                </tr>
              </tbody>
            </n-table>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="最近播放活动" size="small" content-style="padding: 0">
            <n-scrollbar style="max-height: 400px">
              <n-list hoverable clickable>
                <n-list-item v-for="(activity, index) in summary.user_activity" :key="index">
                  <n-thing :title="activity.item_name || '未知项目'" :description="activity.user_name || '未知用户'">
                    <template #header-extra>
                      <n-tag size="small" type="success">
                        {{ activity.total_play_time || '播放中' }}
                      </n-tag>
                    </template>
                    <div style="font-size: 12px; color: #888">
                      {{ activity.last_seen }} | {{ activity.client_name }}
                    </div>
                  </n-thing>
                </n-list-item>
                <n-empty v-if="summary.user_activity.length === 0" description="暂无活动数据" style="padding: 20px" />
              </n-list>
            </n-scrollbar>
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 排行榜区域 -->
      <n-grid :cols="2" :x-gap="12" :y-gap="12">
        <n-gi>
          <n-card title="电影播放排行 (Top 10)" size="small">
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th>名称</th>
                  <th>播放次数</th>
                  <th>播放时长 (分钟)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in reports.movies.slice(0, 10)" :key="index">
                  <td>{{ item.label }}</td>
                  <td>{{ item.count }}</td>
                  <td>{{ item.time }}</td>
                </tr>
              </tbody>
            </n-table>
          </n-card>
        </n-gi>
        <n-gi>
          <n-card title="剧集播放排行 (Top 10)" size="small">
            <n-table :bordered="false" :single-line="false" size="small">
              <thead>
                <tr>
                  <th>名称</th>
                  <th>播放次数</th>
                  <th>播放时长 (分钟)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in reports.tvShows.slice(0, 10)" :key="index">
                  <td>{{ item.label }}</td>
                  <td>{{ item.count }}</td>
                  <td>{{ item.time }}</td>
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
import { BarChartOutlined } from '@vicons/material'
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
</script>

<style scoped>
.playback-report-container {
  padding: 12px;
}
.chart {
  height: 300px;
}
</style>
