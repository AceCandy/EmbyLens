<template>
  <div class="pulse-stats-grid">
    <div v-for="stat in statItems" :key="stat.title" class="stat-glass-card" :style="{ '--stat-color': stat.color }">
      <div class="stat-icon-box">
        <n-icon size="28"><component :is="stat.icon" /></n-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">
          <n-number-animation :from="0" :to="stat.value" />
          <span class="unit">{{ stat.unit }}</span>
        </div>
        <div class="stat-label">{{ stat.title }}</div>
      </div>
      <!-- 装饰背景光 -->
      <div class="stat-glow"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon, NNumberAnimation } from 'naive-ui'
import { 
  PlayArrowOutlined, 
  AccessTimeOutlined, 
  PeopleOutlined, 
  DevicesOutlined 
} from '@vicons/material'

const props = defineProps<{
  stats: {
    totalPlay: number
    totalDuration: number
    userCount: number
    deviceCount: number
  }
}>()

const statItems = computed(() => [
  {
    title: '累计播放次数',
    value: props.stats.totalPlay,
    icon: PlayArrowOutlined,
    color: '#0078d4',
    unit: '次'
  },
  {
    title: '累计播放时长',
    value: props.stats.totalDuration,
    icon: AccessTimeOutlined,
    color: '#18a058',
    unit: '分钟'
  },
  {
    title: '累计活跃用户',
    value: props.stats.userCount,
    icon: PeopleOutlined,
    color: '#f0a020',
    unit: '人'
  },
  {
    title: '覆盖设备终端',
    value: props.stats.deviceCount,
    icon: DevicesOutlined,
    color: '#d03050',
    unit: '台'
  }
])
</script>

<style scoped>
.pulse-stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 10px;
}

.stat-glass-card {
  position: relative;
  background: rgba(24, 24, 28, 0.6);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.stat-glass-card:hover {
  transform: translateY(-5px);
  border-color: var(--stat-color);
}

.stat-icon-box {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--stat-color);
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.05);
}

.stat-info {
  display: flex;
  flex-direction: column;
  z-index: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.unit {
  font-size: 14px;
  font-weight: 400;
  color: #666;
}

.stat-label {
  font-size: 13px;
  color: #aaa;
  margin-top: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 50% 50%, var(--stat-color) 0%, transparent 20%);
  opacity: 0.05;
  pointer-events: none;
}
</style>