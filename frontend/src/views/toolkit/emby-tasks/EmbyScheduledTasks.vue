<template>
  <div class="emby-tasks-container">
    <div class="dashboard-bg-glow"></div>

    <div class="glass-header">
      <n-space align="center" justify="space-between">
        <n-space align="center" :size="20">
          <div class="header-icon">
            <n-icon size="32" color="#fff"><AssignmentOutlined /></n-icon>
          </div>
          <div>
            <div class="main-title">Emby 任务计划中心</div>
            <div class="sub-title">Scheduled Tasks • Server Maintenance</div>
          </div>
        </n-space>
        <n-button circle secondary type="primary" :loading="loading" @click="fetchTasks(true)">
          <template #icon><n-icon><RefreshOutlined /></n-icon></template>
        </n-button>
      </n-space>
    </div>

    <!-- 分组任务列表 -->
    <div class="task-groups-wrapper">
      <div v-for="(group, category) in groupedTasks" :key="category" class="category-section">
        <!-- 分类标题 -->
        <div class="category-header">
          <div class="category-title">{{ category }}</div>
          <div class="category-line"></div>
        </div>

        <!-- 任务列表项 -->
        <div class="task-list">
          <div v-for="task in group" :key="task.Id" class="task-list-item" :class="{ 'is-running': task.State === 'Running' }">
            <!-- 左侧：图标与名称 -->
            <div class="item-leading">
              <div class="category-icon" :style="{ backgroundColor: getCategoryColor(task.Category) + '20', color: getCategoryColor(task.Category) }">
                <n-icon size="24"><component :is="getTaskIcon(task.Category)" /></n-icon>
              </div>
              <div class="name-box">
                <div class="task-name">{{ task.Name }}</div>
                <div class="task-desc">{{ task.Description || '无描述' }}</div>
              </div>
            </div>

            <!-- 中间：进度与状态 -->
            <div class="item-content">
              <div class="status-box">
                <template v-if="task.State === 'Running'">
                  <div class="progress-container">
                    <div class="progress-label">正在运行 - {{ task.CurrentProgressPercentage?.toFixed(1) }}%</div>
                    <n-progress
                      type="line"
                      :percentage="task.CurrentProgressPercentage"
                      :show-indicator="false"
                      color="#18a058"
                      rail-color="rgba(255,255,255,0.05)"
                      processing
                      style="width: 200px"
                    />
                  </div>
                </template>
                <template v-else>
                  <div class="idle-label">
                    <div class="label">上次运行于</div>
                    <div class="value">{{ formatTaskDate(task.LastExecutionResult?.EndTimeUtc) }}</div>
                  </div>
                </template>
              </div>
            </div>

            <!-- 右侧：操作按钮 -->
            <div class="item-actions">
              <n-button
                v-if="task.State !== 'Running'"
                secondary
                circle
                type="primary"
                title="启动任务"
                @click="handleRun(task.Id)"
              >
                <template #icon><n-icon><PlayArrowFilled /></n-icon></template>
              </n-button>
              <n-button
                v-else
                secondary
                circle
                type="error"
                title="停止任务"
                @click="handleStop(task.Id)"
              >
                <template #icon><n-icon><StopFilled /></n-icon></template>
              </n-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { 
  NSpace, NIcon, NButton, NProgress, useMessage 
} from 'naive-ui'
import { 
  AssignmentOutlined, RefreshOutlined, PlayArrowFilled, StopFilled,
  StorageOutlined, SettingsSuggestOutlined, PhotoFilterOutlined, BuildCircleOutlined, HelpOutlineOutlined
} from '@vicons/material'
import { embyTasksApi } from '@/api/embyTasks'

const message = useMessage()
const tasks = ref<any[]>([])
const loading = ref(false)
let timer: any = null

// 分组计算属性
const groupedTasks = computed(() => {
  const visible = tasks.value.filter(t => !t.IsHidden)
  const groups: Record<string, any[]> = {}
  
  visible.forEach(task => {
    const cat = task.Category || 'Other'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push(task)
  })
  
  return groups
})

const fetchTasks = async (showLoading = false) => {
  if (showLoading) loading.value = true
  try {
    const res = await embyTasksApi.list()
    tasks.value = res as any[]
  } catch (err) {
    console.error(err)
  } finally {
    if (showLoading) loading.value = false
  }
}

const handleRun = async (id: string) => {
  try {
    await embyTasksApi.run(id)
    message.success('任务已启动')
    fetchTasks()
  } catch (err) {
    message.error('启动失败')
  }
}

const handleStop = async (id: string) => {
  try {
    await embyTasksApi.stop(id)
    message.warning('已发送停止指令')
    fetchTasks()
  } catch (err) {
    message.error('停止失败')
  }
}

const getCategoryColor = (category: string) => {
  const colors: any = {
    'Library': '#0078d4',
    'System': '#f0a020',
    'Media': '#18a058',
    'Maintenance': '#d03050',
    'Danmu': '#722ed1',
    'Bangumi': '#ff4d4f'
  }
  return colors[category] || '#888'
}

const getTaskIcon = (category: string) => {
  const icons: any = {
    'Library': StorageOutlined,
    'System': SettingsSuggestOutlined,
    'Media': PhotoFilterOutlined,
    'Maintenance': BuildCircleOutlined,
    'Danmu': PhotoFilterOutlined,
    'Bangumi': BuildCircleOutlined
  }
  return icons[category] || HelpOutlineOutlined
}

const formatTaskDate = (dateStr: string) => {
  if (!dateStr) return '从未运行'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins} 分钟前`
  if (diffHours < 24) return `${diffHours} 小时前`
  return date.toLocaleDateString()
}

onMounted(() => {
  fetchTasks(true)
  timer = setInterval(() => fetchTasks(false), 5000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.emby-tasks-container {
  padding: 24px;
  background-color: #0c0c0e;
  min-height: 100vh;
  color: #fff;
  position: relative;
}

.dashboard-bg-glow {
  position: absolute;
  top: -100px;
  right: -100px;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(0, 120, 212, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.glass-header {
  background: rgba(24, 24, 28, 0.7);
  backdrop-filter: blur(20px);
  padding: 20px 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: 40px;
}

.header-icon {
  background: linear-gradient(135deg, #0078d4, #00bcf2);
  width: 56px; height: 56px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 8px 16px rgba(0, 120, 212, 0.3);
}

.main-title { font-size: 24px; font-weight: 800; }
.sub-title { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 2px; }

.task-groups-wrapper {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 0 8px;
}

.category-title {
  font-size: 16px;
  font-weight: 900;
  color: #0078d4;
  text-transform: uppercase;
  letter-spacing: 2px;
  white-space: nowrap;
}

.category-line {
  height: 1px;
  flex: 1;
  background: linear-gradient(to right, rgba(0, 120, 212, 0.3), transparent);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-list-item {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
}

.task-list-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.is-running {
  border-color: rgba(24, 160, 88, 0.3);
  background: rgba(24, 160, 88, 0.05);
}

.item-leading {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.category-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}

.name-box {
  display: flex;
  flex-direction: column;
}

.task-name { font-size: 15px; font-weight: bold; color: #efeff5; }
.task-desc { font-size: 12px; color: #555; }

.item-content {
  flex: 0 0 250px;
  display: flex;
  justify-content: center;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.progress-label { font-size: 11px; color: #18a058; font-weight: bold; text-align: center; }

.idle-label {
  text-align: center;
}
.idle-label .label { font-size: 10px; color: #444; text-transform: uppercase; }
.idle-label .value { font-size: 12px; color: #666; }

.item-actions {
  flex: 0 0 80px;
  display: flex;
  justify-content: flex-end;
}
</style>