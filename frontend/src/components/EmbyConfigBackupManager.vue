<template>
  <div class="backup-manager">
    <n-button size="small" secondary @click="showModal = true">
      <template #icon><n-icon><HistoryIcon /></n-icon></template>
      配置备份管理
    </n-button>

    <n-modal v-model:show="showModal" preset="card" title="配置备份历史" style="width: 700px">
      <template #header-extra>
        <n-popconfirm @positive-click="handleClearAll" positive-text="确定清空" negative-text="取消">
          <template #trigger>
            <n-button size="tiny" type="error" quaternary :disabled="backups.length === 0">
              清空所有备份
            </n-button>
          </template>
          确定要删除当前分类下的所有备份文件吗？此操作不可撤销。
        </n-popconfirm>
      </template>
      <n-space vertical size="large">
        <n-alert type="info" size="small">
          备份将保存当前选定对象的完整原始 JSON 配置。还原操作将直接覆盖服务器上的现有设置，请谨慎操作。
        </n-alert>
        
        <n-data-table
          :columns="columns"
          :data="backups"
          :loading="loading"
          size="small"
          :pagination="{ pageSize: 8 }"
        />
      </n-space>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, h } from 'vue'
import { NButton, NSpace, NPopconfirm, useMessage, NTag, NIcon } from 'naive-ui'
import { listEmbyBackups, restoreEmbyBackup, deleteEmbyBackup, clearEmbyBackups } from '@/api/embyBackup'
import { HistoryOutlined as HistoryIcon } from '@vicons/material'

const props = defineProps<{
  category: 'users' | 'libraries'
  serverId: string
}>()

const emit = defineEmits(['restored'])
const message = useMessage()
const showModal = ref(false)
const loading = ref(false)
const backups = ref<any[]>([])

const columns = [
  { 
    title: '备份名称', 
    key: 'filename',
    render: (row: any) => h('span', { style: 'font-weight: 500' }, row.filename.split('_20')[0])
  },
  { 
    title: '备份时间', 
    key: 'mtime',
    render: (row: any) => new Date(row.mtime * 1000).toLocaleString()
  },
  {
    title: '操作',
    key: 'actions',
    render(row: any) {
      return h(NSpace, null, {
        default: () => [
          h(NPopconfirm, {
            onPositiveClick: () => handleRestore(row.filename),
            positiveText: '确认还原',
            negativeText: '取消'
          }, {
            trigger: () => h(NButton, { size: 'tiny', type: 'warning', secondary: true }, { default: () => '还原' }),
            default: () => '确定要将此配置还原到服务器吗？当前设置将被覆盖。'
          }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDelete(row.filename),
            positiveText: '删除',
            negativeText: '取消'
          }, {
            trigger: () => h(NButton, { size: 'tiny', type: 'error', quaternary: true }, { default: () => '删除' }),
            default: () => '确定删除此备份文件吗？'
          })
        ]
      })
    }
  }
]

const loadBackups = async () => {
  loading.value = true
  try {
    const res = await listEmbyBackups(props.category)
    backups.value = res as any
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleRestore = async (filename: string) => {
  try {
    await restoreEmbyBackup(props.category, filename, props.serverId)
    message.success('配置还原成功')
    emit('restored')
    showModal.value = false
  } catch (e) {
    console.error(e)
  }
}

const handleDelete = async (filename: string) => {
  try {
    await deleteEmbyBackup(props.category, filename)
    message.success('备份已删除')
    loadBackups()
  } catch (e) {
    console.error(e)
  }
}

const handleClearAll = async () => {
  try {
    await clearEmbyBackups(props.category)
    message.success('所有备份已清空')
    loadBackups()
  } catch (e) {
    console.error(e)
  }
}

watch(showModal, (val) => {
  if (val) loadBackups()
})
</script>
