<template>
  <div class="pulse-dashboard">
    <!-- 全景大背景装饰 -->
    <div class="dashboard-bg-glow"></div>

    <n-space vertical size="large" class="dashboard-content">
      <!-- 顶部沉浸式 Header -->
      <div class="glass-header">
        <n-space align="center" justify="space-between">
          <n-space align="center" :size="20">
            <div class="pulse-logo">
              <n-icon size="32" color="#fff"><BarChartOutlined /></n-icon>
            </div>
            <div>
              <div class="main-title">播放洞察全景控制台</div>
              <div class="sub-title">Pulse Analytics • Real-time Insights</div>
            </div>
          </n-space>
          
          <div class="header-controls">
            <n-space align="center">
              <div class="refresh-status" v-if="loading">同步中...</div>
              <n-select
                v-model:value="days"
                :options="dayOptions"
                class="pulse-select"
                @update:value="fetchAllData"
              />
              <n-button circle secondary type="primary" :loading="loading" @click="fetchAllData">
                <template #icon><n-icon><RefreshOutlined /></n-icon></template>
              </n-button>
            </n-space>
          </div>
        </n-space>
      </div>

      <!-- 核心指标行 -->
      <OverviewStats :stats="stats" />

      <!-- 中间混合区域：热力图 + 最近活动 -->
      <n-grid :cols="24" :x-gap="20" :y-gap="20">
        <n-gi :span="17">
          <div class="glass-card">
            <ActivityHeatmap :hourly-data="reports.hourly" />
          </div>
        </n-gi>
        <n-gi :span="7">
          <div class="glass-card activity-panel">
            <div class="card-header">
              <n-icon><HistoryOutlined /></n-icon>
              <span>实时动态</span>
            </div>
            <n-scrollbar style="max-height: 280px">
              <div v-for="(activity, index) in summary.user_activity.slice(0, 8)" :key="index" class="activity-row">
                <n-image
                  width="36"
                  height="54"
                  lazy
                  class="mini-poster"
                  :src="getImageUrl(activity.id || activity.item_id || activity.ItemId)"
                  fallback-src="/fallback-poster.png"
                  object-fit="cover"
                  preview-disabled
                />
                <div class="activity-info">
                  <div class="name">{{ activity.item_name || activity.ItemName }}</div>
                  <div class="user">{{ activity.user_name || activity.UserName }}</div>
                </div>
                <div class="time-badge">{{ activity.duration ? Math.round(activity.duration / 60) + 'm' : 'LIVE' }}</div>
              </div>
            </n-scrollbar>
          </div>
        </n-gi>
      </n-grid>

      <!-- 媒体排行海报流 (重头戏) -->
      <div class="glass-card no-padding">
        <MediaLeaderboard 
          :movies="reports.movies" 
          :tv-shows="reports.tvShows" 
          :get-image-url="getImageUrl"
        />
      </div>

      <!-- 底部用户排行榜 -->
      <div class="glass-card">
        <UserLeaderboard :users="usersWithBadges" />
      </div>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { 
  NSpace, NIcon, NButton, NSelect, NGrid, NGi, NScrollbar, NImage 
} from 'naive-ui'
import { BarChartOutlined, RefreshOutlined, HistoryOutlined } from '@vicons/material'
import { usePlaybackReport } from './usePlaybackReport'

import OverviewStats from './components/OverviewStats.vue'
import ActivityHeatmap from './components/ActivityHeatmap.vue'
import UserLeaderboard from './components/UserLeaderboard.vue'
import MediaLeaderboard from './components/MediaLeaderboard.vue'

const {
  loading,
  days,
  reports,
  stats,
  usersWithBadges,
  summary,
  fetchAllData,
  getImageUrl
} = usePlaybackReport()

const dayOptions = [
  { label: '最近一周', value: 7 },
  { label: '最近双周', value: 14 },
  { label: '最近一月', value: 28 },
  { label: '最近一季', value: 90 },
  { label: '所有数据', value: 3650 }
]
</script>

<style scoped>
.pulse-dashboard {
  position: relative;
  padding: 24px;
  background-color: #0c0c0e;
  min-height: 100vh;
  color: #fff;
  overflow: hidden;
}

.dashboard-bg-glow {
  position: absolute;
  top: -100px;
  right: -100px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 120, 212, 0.15) 0%, transparent 70%);
  pointer-events: none;
}

.dashboard-content {
  position: relative;
  z-index: 1;
}

.glass-header {
  background: rgba(24, 24, 28, 0.7);
  backdrop-filter: blur(20px);
  padding: 20px 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 8px;
}

.pulse-logo {
  background: linear-gradient(135deg, #0078d4, #00bcf2);
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 16px rgba(0, 120, 212, 0.4);
}

.main-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(to right, #fff, #aaa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sub-title {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-top: 2px;
}

.glass-card {
  background: rgba(24, 24, 28, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.glass-card.no-padding {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #0078d4;
}

.pulse-select {
  width: 140px;
}
:deep(.n-base-selection) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: none !important;
}

/* 活动列表样式 */
.activity-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 12px;
  transition: background 0.2s;
}
.activity-row:hover {
  background: rgba(255, 255, 255, 0.03);
}
.mini-poster {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.activity-info {
  flex: 1;
  overflow: hidden;
}
.activity-info .name {
  font-size: 13px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.activity-info .user {
  font-size: 11px;
  color: #666;
}
.time-badge {
  font-size: 10px;
  background: rgba(0, 120, 212, 0.1);
  color: #0078d4;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: bold;
}
</style>