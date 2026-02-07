<template>
  <div class="media-pulse-container">
    <div v-for="section in sections" :key="section.title" class="pulse-section">
      <div class="section-title">
        <n-icon :size="24"><component :is="section.icon" /></n-icon>
        <span>{{ section.title }}</span>
      </div>
      
      <div class="pulse-row">
        <div v-for="(item, index) in section.data.slice(0, 10)" :key="item.id || index" class="pulse-item">
          <!-- 背景毛玻璃海报 -->
          <div class="pulse-bg-poster">
             <img :src="getImageUrl(item)" />
          </div>
          
          <!-- 前景排名与信息 -->
          <div class="pulse-content">
            <div class="rank-number">{{ index + 1 }}</div>
            <div class="main-poster-wrapper">
              <img :src="getImageUrl(item)" class="main-poster" onerror="this.src='/fallback-poster.png'" />
              
              <!-- 顶部浮层：年份和评分 -->
              <div class="top-info" v-if="item.year || item.rating">
                <span class="year" v-if="item.year">{{ item.year }}</span>
                <span class="rating" v-if="item.rating">⭐ {{ item.rating.toFixed(1) }}</span>
              </div>

              <div class="play-tag">{{ item.count }} 次播放</div>
            </div>
            <div class="item-name">{{ item.label }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NIcon } from 'naive-ui'
import { MovieOutlined, LiveTvOutlined } from '@vicons/material'

const props = defineProps<{
  movies: any[]
  tvShows: any[]
  getImageUrl: (item: any) => string
}>()

const sections = computed(() => [
  { title: '热门电影排行', icon: MovieOutlined, data: props.movies },
  { title: '热门剧集排行', icon: LiveTvOutlined, data: props.tvShows }
])
</script>

<style scoped>
/* 样式保持不变 */
.media-pulse-container { display: flex; flex-direction: column; gap: 40px; }
.section-title { display: flex; align-items: center; gap: 12px; font-size: 22px; font-weight: 900; color: #fff; margin-bottom: 24px; padding-left: 10px; border-left: 5px solid #0078d4; }
.pulse-row { display: flex; gap: 24px; overflow-x: auto; padding-bottom: 20px; scrollbar-width: none; }
.pulse-row::-webkit-scrollbar { display: none; }
.pulse-item { position: relative; flex: 0 0 180px; height: 320px; display: flex; flex-direction: column; align-items: center; transition: all 0.3s ease; }
.pulse-item:hover { transform: translateY(-10px); }
.pulse-bg-poster { position: absolute; top: 40px; left: 10px; right: 10px; bottom: 60px; z-index: 0; filter: blur(20px) opacity(0.3); overflow: hidden; border-radius: 20px; }
.pulse-bg-poster img { width: 100%; height: 100%; object-fit: cover; }
.pulse-content { position: relative; z-index: 1; width: 100%; text-align: center; }
.rank-number { font-size: 60px; font-weight: 900; line-height: 1; color: rgba(255, 255, 255, 0.1); font-style: italic; margin-bottom: -25px; margin-left: -120px; z-index: 2; position: relative; }
.main-poster-wrapper { position: relative; width: 160px; height: 240px; margin: 0 auto; border-radius: 12px; overflow: hidden; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); }
.main-poster { width: 100%; height: 100%; object-fit: cover; }
.top-info { position: absolute; top: 0; left: 0; right: 0; padding: 6px; background: linear-gradient(rgba(0,0,0,0.8), transparent); display: flex; justify-content: space-between; font-size: 10px; color: #fff; font-weight: bold; }
.rating { color: #f0a020; }
.play-tag { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0, 120, 212, 0.9); color: white; font-size: 12px; font-weight: bold; padding: 4px 0; }
.item-name { margin-top: 15px; font-size: 14px; font-weight: bold; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 5px; }
.pulse-item:nth-child(1) .main-poster-wrapper { border-color: #f0a020; box-shadow: 0 0 20px rgba(240, 160, 32, 0.3); }
.pulse-item:nth-child(1) .rank-number { color: rgba(240, 160, 32, 0.2); }
.pulse-item:nth-child(1) .play-tag { background: #f0a020; color: #000; }
</style>
