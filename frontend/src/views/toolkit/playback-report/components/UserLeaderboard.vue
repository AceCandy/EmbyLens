<template>
  <div class="user-pulse-leaderboard">
    <div class="section-title">
      <n-icon :size="24"><PeopleOutlined /></n-icon>
      <span>活跃用户排行榜</span>
    </div>

    <!-- 领奖台 (Top 3) -->
    <div class="podium-container">
      <div v-for="user in podiumUsers" :key="user.id" class="podium-item" :class="'rank-' + user.rank">
        <div class="avatar-wrapper">
          <div class="rank-crown" v-if="user.rank === 1">👑</div>
          <div class="glow-ring"></div>
          <n-avatar
            round
            :size="user.rank === 1 ? 100 : 80"
            :src="user.avatar"
            fallback-src="/fallback-avatar.png"
            class="user-avatar"
          />
          <div class="rank-badge">{{ user.rank }}</div>
        </div>
        <div class="user-name">{{ user.label }}</div>
        <div class="user-stats">
          <span class="count">{{ user.count }}次</span>
          <span class="divider">/</span>
          <span class="time">{{ formatDuration(user.time) }}</span>
        </div>
        <div class="badge-row">
          <div v-for="badge in user.badges" :key="badge.text" class="achievement-chip" :style="{ backgroundColor: badge.color + '20', color: badge.color }">
            <n-icon><component :is="badge.icon" /></n-icon>
            {{ badge.text }}
          </div>
        </div>
      </div>
    </div>

    <!-- 列表区 (4-10) -->
    <div class="list-container">
      <div v-for="user in listUsers" :key="user.id" class="user-list-row">
        <div class="rank-num">#{{ user.rank }}</div>
        <n-avatar
          round
          size="medium"
          :src="user.avatar"
          fallback-src="/fallback-avatar.png"
        />
        <div class="main-info">
          <div class="name-line">
            <span class="name">{{ user.label }}</span>
            <div class="mini-badges">
              <span v-for="badge in user.badges" :key="badge.text" :style="{ color: badge.color }">
                <n-icon><component :is="badge.icon" /></n-icon>
              </span>
            </div>
          </div>
          <!-- 活跃度进度条 -->
          <div class="progress-track">
            <div class="progress-bar" :style="{ width: user.percent + '%', backgroundColor: getRankColor(user.rank) }"></div>
          </div>
        </div>
        <div class="data-info">
          <div class="val">{{ user.count }} <small>回</small></div>
          <div class="sub">{{ formatDuration(user.time) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NAvatar, NIcon } from 'naive-ui'
import { 
  PeopleOutlined, 
  EmojiEventsOutlined, 
  LocalFireDepartmentOutlined, 
  HomeOutlined, 
  AutoAwesomeOutlined,
  NightsStayOutlined
} from '@vicons/material'

const props = defineProps<{
  users: any[]
}>()

const podiumUsers = computed(() => {
  const top3 = props.users.slice(0, 3)
  // 顺序调整为：2, 1, 3 这种经典领奖台布局
  const result = []
  if (top3[1]) result.push(top3[1])
  if (top3[0]) result.push(top3[0])
  if (top3[2]) result.push(top3[2])
  return result
})

const listUsers = computed(() => props.users.slice(3, 10))

const formatDuration = (seconds: number) => {
  const s = Number(seconds) || 0
  if (s < 3600) return `${Math.round(s / 60)}m`
  return `${(s / 3600).toFixed(1)}h`
}

const getRankColor = (rank: number) => {
  if (rank === 1) return '#f0a020'
  if (rank === 2) return '#c0c0c0'
  if (rank === 3) return '#b87333'
  return '#0078d4'
}
</script>

<style scoped>
.user-pulse-leaderboard {
  padding: 10px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 30px;
}

/* 领奖台样式 */
.podium-container {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 40px;
  margin-bottom: 50px;
  padding-top: 20px;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.3s ease;
}
.podium-item:hover { transform: translateY(-10px); }

.avatar-wrapper {
  position: relative;
  margin-bottom: 15px;
}

.rank-1 { order: 2; margin-top: -30px; }
.rank-2 { order: 1; }
.rank-3 { order: 3; }

.rank-crown {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%) rotate(-10deg);
  font-size: 30px;
  z-index: 10;
  filter: drop-shadow(0 0 10px rgba(240, 160, 32, 0.8));
}

.glow-ring {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border-radius: 50%;
  border: 2px solid transparent;
  animation: rotate 4s linear infinite;
}
.rank-1 .glow-ring { border-color: #f0a020; box-shadow: 0 0 20px rgba(240, 160, 32, 0.4); }
.rank-2 .glow-ring { border-color: #c0c0c0; }
.rank-3 .glow-ring { border-color: #b87333; }

.rank-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  background: #333;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 2px solid #18181c;
}
.rank-1 .rank-badge { background: #f0a020; color: #000; }

.user-name {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  margin-bottom: 5px;
}

.user-stats {
  font-size: 13px;
  color: #aaa;
  margin-bottom: 12px;
}
.user-stats .count { color: #0078d4; font-weight: bold; }

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}

.achievement-chip {
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 列表样式 */
.list-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.user-list-row {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}
.user-list-row:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: scale(1.01);
}

.rank-num {
  font-size: 14px;
  font-weight: 900;
  font-style: italic;
  color: #666;
  width: 30px;
}

.main-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.name-line {
  display: flex;
  align-items: center;
  gap: 10px;
}
.name-line .name { font-weight: bold; color: #efeff5; }
.mini-badges { display: flex; gap: 4px; font-size: 14px; }

.progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  width: 100%;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 1s ease-out;
}

.data-info {
  text-align: right;
}
.data-info .val { font-size: 16px; font-weight: bold; color: #fff; }
.data-info .val small { font-size: 10px; color: #666; }
.data-info .sub { font-size: 11px; color: #666; }

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
