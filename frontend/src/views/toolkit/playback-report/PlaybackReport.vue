<template>
  <div class="pulse-dashboard">
    <div class="dashboard-bg-glow"></div>

    <n-space vertical size="large" class="dashboard-content">
      <!-- 顶部 Header -->
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
              <n-select v-model:value="days" :options="dayOptions" class="pulse-select" @update:value="fetchAllData" />
              <n-button circle secondary type="primary" :loading="loading" @click="fetchAllData">
                <template #icon><n-icon><RefreshOutlined /></n-icon></template>
              </n-button>
            </n-space>
          </div>
        </n-space>
      </div>

      <!-- 第一行：核心指标 -->
      <OverviewStats :stats="stats" />

      <!-- 第二行：用户排行 (左) + 最近播放 (右) -->
      <n-grid :cols="24" :x-gap="20">
        <n-gi :span="15">
          <div class="glass-card full-height-card">
            <UserLeaderboard :users="usersWithBadges" />
          </div>
        </n-gi>
        <n-gi :span="9">
          <div class="glass-card activity-panel full-height-card">
            <div class="card-header">
              <n-icon><HistoryOutlined /></n-icon>
              <span>最近播放活动</span>
            </div>
            <n-scrollbar style="height: 600px">
              <div class="activity-list">
                <div v-for="(activity, index) in summary.user_activity.slice(0, 15)" :key="index" class="activity-row">
                  <div class="activity-poster">
                    <img 
                      :src="getImageUrl(activity)" 
                      class="mini-poster-img"
                      onerror="this.src='/fallback-poster.png'"
                    />
                  </div>
                  <div class="activity-info">
                    <div class="name">{{ activity.label }}</div>
                    <div class="user-line">
                      <n-icon><PeopleOutlined /></n-icon>
                      {{ activity.user_name || activity.UserName }}
                    </div>
                    <div class="date-line">{{ activity.DateCreated?.split(' ')[0] || activity.date }}</div>
                  </div>
                  <div class="activity-badge" :class="{ 'is-live': !activity.duration }">
                    {{ activity.duration ? Math.round(activity.duration / 60) + 'm' : 'LIVE' }}
                  </div>
                </div>
              </div>
            </n-scrollbar>
          </div>
        </n-gi>
      </n-grid>

      <!-- 第三行：媒体排行 (横排海报流) -->
      <div class="glass-card no-padding">
        <MediaLeaderboard :movies="reports.movies" :tv-shows="reports.tvShows" :get-image-url="getImageUrl" />
      </div>

      <!-- 第四行：24小时播放热度脉冲 (底座图表) -->
      <div class="glass-card">
        <ActivityHeatmap :hourly-data="reports.hourly" />
      </div>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { NSpace, NIcon, NButton, NSelect, NGrid, NGi, NScrollbar } from 'naive-ui'
import { BarChartOutlined, RefreshOutlined, HistoryOutlined, PeopleOutlined } from '@vicons/material'
import { usePlaybackReport } from './usePlaybackReport'

import OverviewStats from './components/OverviewStats.vue'
import ActivityHeatmap from './components/ActivityHeatmap.vue'
import UserLeaderboard from './components/UserLeaderboard.vue'
import MediaLeaderboard from './components/MediaLeaderboard.vue'

const { loading, days, reports, stats, usersWithBadges, summary, fetchAllData, getImageUrl } = usePlaybackReport()

const dayOptions = [
  { label: '最近一周', value: 7 },
  { label: '最近双周', value: 14 },
  { label: '最近一月', value: 28 },
  { label: '最近一季', value: 90 },
  { label: '所有数据', value: 3650 }
]
</script>

<style scoped>
.pulse-dashboard { position: relative; padding: 24px; background-color: #0c0c0e; min-height: 100vh; color: #fff; overflow-x: hidden; }
.dashboard-bg-glow { position: absolute; top: -100px; right: -100px; width: 600px; height: 600px; background: radial-gradient(circle, rgba(0, 120, 212, 0.15) 0%, transparent 70%); pointer-events: none; }
.dashboard-content { position: relative; z-index: 1; }
.glass-header { background: rgba(24, 24, 28, 0.7); backdrop-filter: blur(20px); padding: 20px 24px; border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 8px; }
.pulse-logo { background: linear-gradient(135deg, #0078d4, #00bcf2); width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(0, 120, 212, 0.4); }
.main-title { font-size: 24px; font-weight: 800; letter-spacing: -0.5px; background: linear-gradient(to right, #fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.sub-title { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 2px; margin-top: 2px; }
.glass-card { background: rgba(24, 24, 28, 0.6); backdrop-filter: blur(10px); border-radius: 20px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 10px; }
.glass-card.no-padding { padding: 20px; }
.card-header { display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: bold; margin-bottom: 24px; color: #0078d4; }
.pulse-select { width: 140px; }

.full-height-card {
  height: 720px;
  display: flex;
  flex-direction: column;
}

/* 最近播放活动样式 */
.activity-list { display: flex; flex-direction: column; gap: 16px; }
.activity-row { display: flex; align-items: center; gap: 16px; padding: 12px; background: rgba(255, 255, 255, 0.02); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.03); transition: all 0.2s; }
.activity-row:hover { background: rgba(255, 255, 255, 0.05); transform: translateX(5px); }
.activity-poster { width: 45px; height: 68px; flex-shrink: 0; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
.mini-poster-img { width: 100%; height: 100%; object-fit: cover; }
.activity-info { flex: 1; min-width: 0; }
.activity-info .name { font-weight: bold; font-size: 14px; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px; }
.activity-info .user-line { font-size: 12px; color: #0078d4; display: flex; align-items: center; gap: 4px; }
.activity-info .date-line { font-size: 11px; color: #555; margin-top: 4px; }
.activity-badge { padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: bold; background: rgba(255, 255, 255, 0.05); color: #888; }
.activity-badge.is-live { background: rgba(24, 160, 88, 0.1); color: #18a058; box-shadow: 0 0 10px rgba(24, 160, 88, 0.2); }
</style>