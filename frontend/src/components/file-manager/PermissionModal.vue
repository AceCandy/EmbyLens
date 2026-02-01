<template>
  <n-modal :show="show" @update:show="$emit('update:show', $event)" preset="dialog" title="设置权限与所有者" style="width: 500px">
    <n-form label-placement="top" style="margin-top: 10px">
      <n-form-item label="当前路径">
        <n-text depth="3" code>{{ item?.path }}</n-text>
      </n-form-item>
      
      <n-table :bordered="false" :single-column="false" size="small">
        <thead>
          <tr><th>对象</th><th>读取</th><th>写入</th><th>执行</th></tr>
        </thead>
        <tbody>
          <tr v-for="role in (['owner', 'group', 'public'] as const)" :key="role">
            <td>{{ role === 'owner' ? '所有者' : role === 'group' ? '用户组' : '公共' }}</td>
            <td><n-checkbox v-model:checked="permMatrix[role].read" @update:checked="calcMode" /></td>
            <td><n-checkbox v-model:checked="permMatrix[role].write" @update:checked="calcMode" /></td>
            <td><n-checkbox v-model:checked="permMatrix[role].execute" @update:checked="calcMode" /></td>
          </tr>
        </tbody>
      </n-table>

      <n-grid :cols="2" :x-gap="12" style="margin-top: 15px">
        <n-gi>
          <n-form-item label="权限代码"><n-input v-model:value="form.mode" placeholder="0755" /></n-form-item>
        </n-gi>
        <n-gi>
          <n-form-item label="所有者:用户组">
            <n-input-group>
              <n-input v-model:value="form.owner" placeholder="root" />
              <n-input-group-label>:</n-input-group-label>
              <n-input v-model:value="form.group" placeholder="root" />
            </n-input-group>
          </n-form-item>
        </n-gi>
      </n-grid>

      <n-form-item v-if="item?.is_dir">
        <n-checkbox v-model:checked="form.recursive">递归应用到子项</n-checkbox>
      </n-form-item>
    </n-form>
    <template #action>
      <n-space justify="end">
        <n-button @click="$emit('update:show', false)">取消</n-button>
        <n-button type="primary" :loading="submitting" @click="submit">确定应用</n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { 
  NModal, NForm, NFormItem, NText, NTable, NCheckbox, NGrid, NGi, NInput, 
  NInputGroup, NInputGroupLabel, NSpace, NButton, useMessage 
} from 'naive-ui'

const props = defineProps<{
  show: boolean
  item: any
  hostId: number | string
  provider: any
}>()

const emit = defineEmits(['update:show', 'success'])
const message = useMessage()
const submitting = ref(false)

const form = reactive({
  mode: '0755', owner: 'root', group: 'root', recursive: false
})

const permMatrix = reactive({
  owner: { read: true, write: true, execute: true },
  group: { read: true, write: false, execute: true },
  public: { read: true, write: false, execute: true }
})

watch(() => props.show, (val) => {
  if (val && props.item) {
    const mode = props.item.mode || (props.item.is_dir ? '0755' : '0644')
    form.mode = mode.startsWith('0') ? mode : '0' + mode
    const code = form.mode.slice(-3)
    const parse = (char: string) => {
      const n = parseInt(char)
      return { read: !!(n & 4), write: !!(n & 2), execute: !!(n & 1) }
    }
    permMatrix.owner = parse(code[0])
    permMatrix.group = parse(code[1])
    permMatrix.public = parse(code[2])
  }
})

const calcMode = () => {
  const getVal = (role: 'owner' | 'group' | 'public') => {
    let val = 0
    if (permMatrix[role].read) val += 4
    if (permMatrix[role].write) val += 2
    if (permMatrix[role].execute) val += 1
    return val
  }
  form.mode = `0${getVal('owner')}${getVal('group')}${getVal('public')}`
}

const submit = async () => {
  submitting.value = true
  try {
    await props.provider.chmod(props.hostId, {
      path: props.item.path,
      mode: form.mode.slice(-3),
      owner: form.owner,
      group: form.group,
      recursive: form.recursive
    })
    message.success('更新成功')
    emit('success')
    emit('update:show', false)
  } catch (e) {
    message.error('更新失败')
  } finally {
    submitting.value = false
  }
}
</script>
