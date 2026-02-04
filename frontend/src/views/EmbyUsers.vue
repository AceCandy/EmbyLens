<template>
  <div class="emby-users-container">
    <n-space vertical size="large">
      <div class="page-header">
        <n-h2 prefix="bar" align-text><n-text type="primary">Emby 用户管理</n-text></n-h2>
        <n-text depth="3">管理您的 Emby 服务器用户、权限策略及密码。</n-text>
      </div>

      <n-card size="small" segmented>
        <template #header>
          <n-space align="center">
            <span>当前服务器:</span>
            <n-select
              v-model:value="selectedServerId"
              :options="serverOptions"
              size="small"
              style="width: 200px"
              @update:value="loadUsers"
            />
            <n-button size="small" @click="loadUsers" :loading="loading">
              刷新
            </n-button>
          </n-space>
        </template>
        <template #header-extra>
          <n-input-group>
            <n-input v-model:value="newUserName" placeholder="新用户名" size="small" @keyup.enter="handleCreateUser" />
            <n-button type="primary" size="small" @click="handleCreateUser" :loading="creating">
              新增用户
            </n-button>
          </n-input-group>
        </template>

        <n-data-table
          :columns="columns"
          :data="users"
          :loading="loading"
          size="small"
          :pagination="{ pageSize: 10 }"
        />
      </n-card>
    </n-space>

    <!-- 用户设置模态框 -->
    <n-modal
      v-model:show="showEditModal"
      preset="card"
      :title="'设置: ' + editingUser?.Name"
      style="width: 800px"
      segmented
    >
      <n-tabs type="line" animated>
        <n-tab-pane name="account" tab="账户与访问">
          <n-form label-placement="left" label-width="200" size="small">
            <n-form-item label="禁用此账户">
              <n-switch v-model:value="policy.IsDisabled" />
            </n-form-item>
            <n-form-item label="管理员权限">
              <n-switch v-model:value="policy.IsAdministrator" />
            </n-form-item>
            <n-form-item label="登录时隐藏">
              <n-switch v-model:value="policy.IsHidden" />
            </n-form-item>
            <n-form-item label="远程访问时隐藏">
              <n-switch v-model:value="policy.IsHiddenRemotely" />
            </n-form-item>
            <n-form-item label="从未使用的设备上隐藏">
              <n-switch v-model:value="policy.IsHiddenFromUnusedDevices" />
            </n-form-item>
            <n-form-item label="允许远程访问">
              <n-switch v-model:value="policy.EnableRemoteAccess" />
            </n-form-item>
            <n-form-item label="同时播放数量限制">
              <n-input-number v-model:value="policy.SimultaneousStreamLimit" :min="0" />
              <template #feedback>0 为无限制</template>
            </n-form-item>
            <n-form-item label="远程比特率限制 (bps)">
              <n-input-number v-model:value="policy.RemoteClientBitrateLimit" :min="0" :step="1000000" />
              <template #feedback>0 为无限制</template>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="playback" tab="播放与转码">
          <n-form label-placement="left" label-width="200" size="small">
            <n-form-item label="允许媒体播放">
              <n-switch v-model:value="policy.EnableMediaPlayback" />
            </n-form-item>
            <n-form-item label="允许音频转码">
              <n-switch v-model:value="policy.EnableAudioPlaybackTranscoding" />
            </n-form-item>
            <n-form-item label="允许视频转码">
              <n-switch v-model:value="policy.EnableVideoPlaybackTranscoding" />
            </n-form-item>
            <n-form-item label="允许封装转换 (Remux)">
              <n-switch v-model:value="policy.EnablePlaybackRemuxing" />
            </n-form-item>
            <n-form-item label="允许媒体转换">
              <n-switch v-model:value="policy.EnableMediaConversion" />
            </n-form-item>
            <n-form-item label="允许同步转码">
              <n-switch v-model:value="policy.EnableSyncTranscoding" />
            </n-form-item>
            <n-form-item label="自动远程质量 (Mbps)">
              <n-input-number v-model:value="policy.AutoRemoteQuality" :min="0" />
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="features" tab="功能权限">
          <n-form label-placement="left" label-width="200" size="small">
            <n-divider title-placement="left">文件与下载</n-divider>
            <n-form-item label="允许删除媒体文件">
              <n-switch v-model:value="policy.EnableContentDeletion" />
            </n-form-item>
            <n-form-item label="允许下载媒体">
              <n-switch v-model:value="policy.EnableContentDownloading" />
            </n-form-item>
            <n-form-item label="允许下载字幕">
              <n-switch v-model:value="policy.EnableSubtitleDownloading" />
            </n-form-item>
            <n-form-item label="允许管理字幕">
              <n-switch v-model:value="policy.EnableSubtitleManagement" />
            </n-form-item>
            <n-form-item label="允许相机上传">
              <n-switch v-model:value="policy.AllowCameraUpload" />
            </n-form-item>

            <n-divider title-placement="left">社交与远程</n-divider>
            <n-form-item label="允许公开分享">
              <n-switch v-model:value="policy.EnablePublicSharing" />
            </n-form-item>
            <n-form-item label="允许远程控制其他用户">
              <n-switch v-model:value="policy.EnableRemoteControlOfOtherUsers" />
            </n-form-item>
            <n-form-item label="允许控制共享设备">
              <n-switch v-model:value="policy.EnableSharedDeviceControl" />
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="library" tab="媒体库范围">
          <n-form label-placement="left" label-width="200" size="small">
            <n-divider title-placement="left">访问范围</n-divider>
            <n-form-item label="允许访问所有媒体库">
              <n-switch v-model:value="policy.EnableAllFolders" />
            </n-form-item>
            <n-form-item label="允许访问所有频道">
              <n-switch v-model:value="policy.EnableAllChannels" />
            </n-form-item>
            <n-form-item label="允许在所有设备上登录">
              <n-switch v-model:value="policy.EnableAllDevices" />
            </n-form-item>
            
            <n-divider title-placement="left">直播电视</n-divider>
            <n-form-item label="允许观看直播电视">
              <n-switch v-model:value="policy.EnableLiveTvAccess" />
            </n-form-item>
            <n-form-item label="允许管理直播电视">
              <n-switch v-model:value="policy.EnableLiveTvManagement" />
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="password" tab="修改密码">
          <n-form label-placement="left" label-width="100" size="small">
            <n-form-item label="新密码">
              <n-input v-model:value="newPassword" type="password" show-password-on="click" placeholder="留空则不修改" />
            </n-form-item>
            <n-form-item>
              <n-button type="warning" @click="handleUpdatePassword" :disabled="!newPassword">
                单独更新密码
              </n-button>
            </n-form-item>
          </n-form>
        </n-tab-pane>

        <n-tab-pane name="json" tab="原始数据 (JSON)">
          <n-space vertical>
            <n-alert type="info" size="small">
              高级操作：您可以直接编辑下方的原始 JSON 数据。请确保格式正确，非法 JSON 将无法保存。
            </n-alert>
            <n-input
              v-model:value="jsonRaw"
              type="textarea"
              :autosize="{ minRows: 15, maxRows: 25 }"
              placeholder="请输入有效的 Policy JSON"
              style="font-family: monospace"
              @update:value="handleJsonInput"
            />
          </n-space>
        </n-tab-pane>
      </n-tabs>

      <template #action>
        <n-space justify="end">
          <n-button @click="showEditModal = false">取消</n-button>
          <n-button type="primary" @click="handleSavePolicy" :loading="savingPolicy">保存设置</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, h } from 'vue'
import { NButton, NSpace, NTag, NPopconfirm, useMessage } from 'naive-ui'
import { 
  listEmbyUsers, 
  createEmbyUser, 
  deleteEmbyUser, 
  getEmbyUserInfo, 
  updateEmbyUserPolicy,
  updateEmbyUserPassword
} from '@/api/embyUsers'
import { servers, activeServerId, fetchServers } from '@/store/serverStore'

const message = useMessage()
const loading = ref(false)
const creating = ref(false)
const users = ref<any[]>([])
const selectedServerId = ref('')
const newUserName = ref('')

const showEditModal = ref(false)
const editingUser = ref<any>(null)
const policy = ref<any>({})
const jsonRaw = ref('')
const newPassword = ref('')
const savingPolicy = ref(false)

const serverOptions = computed(() => {
  return servers.value.map(s => ({
    label: s.name,
    value: s.id
  }))
})

// 处理 JSON 输入，尝试同步回 policy 对象以保持 UI 一致
const handleJsonInput = (value: string) => {
  try {
    const parsed = JSON.parse(value)
    policy.value = parsed
  } catch (e) {
    // 允许输入过程中的非法格式，仅在保存时强校验
  }
}

const columns = [
  { title: '用户名', key: 'Name' },
  { 
    title: '状态', 
    key: 'Policy',
    render(row: any) {
      const tags = []
      if (row.Policy?.IsDisabled) tags.push(h(NTag, { type: 'error', size: 'small' }, { default: () => '禁用' }))
      if (row.Policy?.IsAdministrator) tags.push(h(NTag, { type: 'warning', size: 'small' }, { default: () => '管理员' }))
      if (row.Policy?.IsHidden) tags.push(h(NTag, { type: 'default', size: 'small' }, { default: () => '隐藏' }))
      
      if (tags.length === 0) tags.push(h(NTag, { type: 'success', size: 'small' }, { default: () => '正常' }))
      
      return h(NSpace, null, { default: () => tags })
    }
  },
  {
    title: '操作',
    key: 'actions',
    render(row: any) {
      return h(NSpace, null, {
        default: () => [
          h(NButton, { 
            size: 'small', 
            secondary: true,
            onClick: () => openEdit(row)
          }, { default: () => '设置' }),
          h(NPopconfirm, {
            onPositiveClick: () => handleDeleteUser(row.Id),
            positiveText: '确认',
            negativeText: '取消'
          }, {
            trigger: () => h(NButton, { size: 'small', type: 'error', quaternary: true }, { default: () => '删除' }),
            default: () => `确定删除用户 ${row.Name}？`
          })
        ]
      })
    }
  }
]

const loadUsers = async () => {
  if (!selectedServerId.value) return
  loading.value = true
  try {
    const res = await listEmbyUsers(selectedServerId.value)
    users.value = res as any
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleCreateUser = async () => {
  if (!newUserName.value) return
  creating.value = true
  try {
    await createEmbyUser(newUserName.value, selectedServerId.value)
    message.success('创建成功')
    newUserName.value = ''
    loadUsers()
  } catch (e) {
    console.error(e)
  } finally {
    creating.value = false
  }
}

const handleDeleteUser = async (userId: string) => {
  try {
    await deleteEmbyUser(userId, selectedServerId.value)
    message.success('删除成功')
    loadUsers()
  } catch (e) {
    console.error(e)
  }
}

const openEdit = async (user: any) => {
  editingUser.value = user
  newPassword.value = ''
  try {
    const info = await getEmbyUserInfo(user.Id, selectedServerId.value) as any
    policy.value = info.Policy || {}
    jsonRaw.value = JSON.stringify(policy.value, null, 2)
    showEditModal.value = true
  } catch (e) {
    console.error(e)
  }
}

const handleSavePolicy = async () => {
  if (!editingUser.value) return
  
  // 最终 JSON 校验
  try {
    policy.value = JSON.parse(jsonRaw.value)
  } catch (e) {
    message.error('JSON 格式非法，请检查后再试')
    return
  }

  savingPolicy.value = true
  try {
    await updateEmbyUserPolicy(editingUser.value.Id, policy.value, selectedServerId.value)
    message.success('设置已保存')
    showEditModal.value = false
    loadUsers()
  } catch (e) {
    console.error(e)
  } finally {
    savingPolicy.value = false
  }
}

const handleUpdatePassword = async () => {
  if (!editingUser.value || !newPassword.value) return
  try {
    await updateEmbyUserPassword(editingUser.value.Id, newPassword.value, selectedServerId.value)
    message.success('密码已更新')
    newPassword.value = ''
  } catch (e) {
    console.error(e)
  }
}

onMounted(async () => {
  await fetchServers()
  if (activeServerId.value) {
    selectedServerId.value = activeServerId.value
  } else if (servers.value.length > 0) {
    selectedServerId.value = servers.value[0].id
  }
  loadUsers()
})
</script>

<style scoped>
.emby-users-container {
  padding: 10px;
}
.page-header {
  margin-bottom: 20px;
}
</style>
