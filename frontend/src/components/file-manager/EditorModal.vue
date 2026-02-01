<template>
  <n-modal :show="show" @update:show="$emit('update:show', $event)" preset="card" :title="'编辑文件: ' + item?.name" style="width: 90vw; max-width: 1000px">
    <div class="editor-container">
      <n-spin :show="loading">
        <n-input
          v-model:value="content"
          type="textarea"
          placeholder="文件内容加载中..."
          :autosize="{ minRows: 15, maxRows: 25 }"
          style="font-family: monospace"
        />
      </n-spin>
    </div>
    <template #footer>
      <n-space justify="end">
        <n-button @click="$emit('update:show', false)">关闭</n-button>
        <n-button type="primary" :loading="saving" @click="save">保存修改</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NInput, NSpace, NButton, NSpin, useMessage } from 'naive-ui'

const props = defineProps<{
  show: boolean
  item: any
  hostId: number | string
  provider: any
}>()

const emit = defineEmits(['update:show'])
const message = useMessage()

const content = ref('')
const loading = ref(false)
const saving = ref(false)

watch(() => props.show, async (val) => {
  if (val && props.item) {
    loading.value = true
    try {
      const res = await props.provider.read(props.hostId, props.item.path)
      content.value = res.content
    } catch (e) {
      message.error('读取失败')
    } finally {
      loading.value = false
    }
  }
})

const save = async () => {
  saving.value = true
  try {
    await props.provider.write(props.hostId, props.item.path, content.value)
    message.success('已保存')
    emit('update:show', false)
  } catch (e) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.editor-container { margin-top: 10px; border: 1px solid var(--border-color); border-radius: 4px; overflow: hidden; }
</style>
