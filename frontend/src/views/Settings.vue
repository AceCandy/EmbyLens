<template>
  <div class="toolkit-container">
    <n-space vertical size="large">
      <div class="page-header">
        <n-h2 prefix="bar" align-text><n-text type="primary">系统集成配置</n-text></n-h2>
        <n-text depth="3">统一管理您的 Emby 核心凭据与第三方扩展 API 密钥。</n-text>
      </div>

      <n-grid :x-gap="12" :y-gap="12" :cols="24" item-responsive responsive="screen">
        <!-- 左侧：核心凭据管理 -->
        <n-gi span="24 m:16">
          <n-space vertical size="large">
            <!-- 1. Emby 服务端管理 -->
            <n-card title="Emby 服务端管理" size="small" segmented>
              <template #header-extra>
                <n-button type="primary" size="small" @click="openAddModal">
                  <template #icon><n-icon><AddIcon /></n-icon></template>
                  添加服务器
                </n-button>
              </template>
              
              <n-table :single-line="false" size="small">
                <thead>
                  <tr>
                    <th>名称</th>
                    <th>服务器地址</th>
                    <th>状态</th>
                    <th style="width: 160px">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in servers" :key="s.id" :class="{ 'active-row': s.id === activeServerId }">
                    <td><strong>{{ s.name }}</strong></td>
                    <td><n-text depth="3">{{ s.url }}</n-text></td>
                    <td>
                      <n-tag v-if="s.id === activeServerId" type="success" size="small" round quaternary>当前激活</n-tag>
                      <n-tag v-else depth="3" size="small" round quaternary>闲置</n-tag>
                    </td>
                    <td>
                      <n-space>
                        <n-button size="tiny" secondary @click="openEditModal(s)">配置</n-button>
                        <n-button v-if="s.id !== activeServerId" size="tiny" type="primary" secondary @click="handleActivate(s.id)">激活</n-button>
                        <n-popconfirm @positive-click="handleDelete(s.id)" positive-text="确认" negative-text="取消">
                          <template #trigger>
                            <n-button size="tiny" type="error" quaternary>删除</n-button>
                          </template>
                          确定删除？
                        </n-popconfirm>
                      </n-space>
                    </td>
                  </tr>
                  <tr v-if="servers.length === 0">
                    <td colspan="4" style="text-align: center; padding: 30px">
                      <n-empty description="暂无服务器配置" />
                    </td>
                  </tr>
                </tbody>
              </n-table>
            </n-card>

            <!-- 2. 全局 API 服务集成 -->
            <n-card title="第三方 API 扩展集成" size="small" segmented>
              <template #header-extra>
                <n-icon size="20" color="var(--primary-color)"><ApiIcon /></n-icon>
              </template>
              <n-form label-placement="left" label-width="140" size="small">
                <n-form-item label="TMDB API Key">
                  <n-input v-model:value="globalConfig.tmdb_api_key" type="password" show-password-on="mousedown" placeholder="The Movie Database V3 Key" />
                </n-form-item>
                <n-form-item label="Bangumi API Token">
                  <n-input v-model:value="globalConfig.bangumi_api_token" type="password" show-password-on="mousedown" placeholder="Bangumi Access Token" />
                </n-form-item>
              </n-form>
              <template #action>
                <n-space justify="end">
                  <n-button type="primary" size="small" @click="handleSaveGlobal" :loading="savingGlobal">保存 API 配置</n-button>
                </n-space>
              </template>
            </n-card>

            <!-- 3. HTTP 代理配置 -->
            <n-card title="网络代理设置" size="small" segmented>
              <template #header-extra>
                <n-icon size="20" color="var(--primary-color)"><ProxyIcon /></n-icon>
              </template>
              <n-form label-placement="top" size="small">
                <n-grid :cols="2" :x-gap="24">
                  <n-form-item-gi label="启用全局代理">
                    <n-switch v-model:value="globalConfig.proxy.enabled" />
                  </n-form-item-gi>
                  <n-form-item-gi label="排除 Emby 服务器">
                    <n-switch v-model:value="globalConfig.proxy.exclude_emby" />
                  </n-form-item-gi>
                  <n-form-item-gi span="2" label="代理服务器地址 (Proxy URL)">
                    <n-input v-model:value="globalConfig.proxy.url" placeholder="http://127.0.0.1:7890" :disabled="!globalConfig.proxy.enabled" />
                  </n-form-item-gi>
                </n-grid>
              </n-form>
              <template #action>
                <n-space justify="end">
                  <n-button type="primary" size="small" @click="handleSaveGlobal" :loading="savingGlobal">保存代理配置</n-button>
                </n-space>
              </template>
            </n-card>
          </n-space>
        </n-gi>

        <!-- 右侧：维护与快照 -->
        <n-gi span="24 m:8">
          <n-space vertical size="large">
            <!-- 4. 配置备份与恢复 -->
            <n-card title="数据备份与迁移" size="small" segmented>
              <template #header-extra>
                <n-icon size="20" color="var(--primary-color)"><BackupIcon /></n-icon>
              </template>
              <n-text depth="3" style="font-size: 13px; display: block; margin-bottom: 16px;">
                您可以导出当前的全局配置文件 (config.json) 进行备份，或在迁移环境时导入旧配置。
              </n-text>
              <n-space vertical>
                <n-button block secondary @click="handleExportConfig">
                  <template #icon><n-icon><ExportIcon /></n-icon></template>
                  导出 config.json
                </n-button>
                <n-button block type="primary" ghost @click="triggerImportConfig">
                  <template #icon><n-icon><ImportIcon /></n-icon></template>
                  导入备份文件
                </n-button>
                <input 
                  type="file" 
                  ref="fileInputRef" 
                  style="display: none" 
                  accept=".json" 
                  @change="handleImportConfig" 
                />
              </n-space>
            </n-card>

            <!-- 5. 调试：全局配置快照 -->
            <n-card title="实时配置快照 (JSON)" size="small" segmented>
              <template #header-extra>
                <n-button quaternary size="tiny" @click="copyConfig">复制</n-button>
              </template>
              <div class="debug-code-wrapper">
                <n-code :code="JSON.stringify(globalConfig, null, 2)" language="json" word-wrap />
              </div>
            </n-card>

            <n-card title="配置贴士" size="small" segmented>
              <n-text depth="3" style="font-size: 13px">
                - &lt;b&gt;TMDB&lt;/b&gt;：元数据抓取的核心，建议配置 V3 Key.&lt;br/&gt;
                - &lt;b&gt;代理&lt;/b&gt;：如果您无法连接外网，请在此配置 HTTP/SOCKS 代理。&lt;br/&gt;
                - &lt;b&gt;多服务器&lt;/b&gt;：Lens 支持管理多个 Emby，您可以随时切换当前激活的服务器。
              </n-text>
            </n-card>
          </n-space>
        </n-gi>
      </n-grid>
    </n-space>

    <!-- 抽离出的服务器配置弹窗 -->
    <EmbyServerModal 
      v-model:show="showServerModal" 
      :server-data="editingServer" 
      @on-success="fetchCurrent"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { 
  useMessage, NSpace, NH2, NText, NCard, NTag, NIcon, 
  NForm, NGrid, NFormItemGi, NInput, NSwitch, NCode, 
  NButton, NFormItem, NTable, NEmpty, NPopconfirm, NDivider
} from 'naive-ui'
import { 
  DnsOutlined as ServerIcon,
  ApiOutlined as ApiIcon,
  LanguageOutlined as ProxyIcon,
  AddOutlined as AddIcon,
  CloudDownloadOutlined as ExportIcon,
  CloudUploadOutlined as ImportIcon,
  SaveAsOutlined as BackupIcon
} from '@vicons/material'
import { servers, activeServerId } from '../store/serverStore'
import { copyElementContent } from '../utils/clipboard'
import EmbyServerModal from '../components/EmbyServerModal.vue'

// 导入提取的逻辑
import { useSettings } from '../hooks/useSettings'

const message = useMessage()
const { 
  globalConfig, savingGlobal, showServerModal, editingServer, fileInputRef,
  handleExportConfig, triggerImportConfig, handleImportConfig, fetchCurrent, 
  handleActivate, handleDelete, handleSaveGlobal
} = useSettings()

onMounted(fetchCurrent)

const openAddModal = () => {
  editingServer.value = null
  showServerModal.value = true
}

const openEditModal = (s: any) => {
  editingServer.value = s
  showServerModal.value = true
}

const copyConfig = () => {
  const selector = document.querySelector('.debug-code-wrapper pre') ? '.debug-code-wrapper pre' : '.debug-code-wrapper'
  if (copyElementContent(selector)) {
    message.info('配置快照已复制')
  } else {
    message.error('复制失败')
  }
}
</script>

<style scoped>
.debug-code-wrapper { 
  background-color: rgba(0, 0, 0, 0.3); 
  padding: 12px; 
  border-radius: 8px; 
  border: 1px solid var(--border-color); 
}
.active-row {
  background-color: rgba(var(--primary-color-rgb), 0.1);
}
</style>
