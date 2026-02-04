<template>
  <div class="basic-info-tab">
    <n-form label-placement="left" label-width="200" size="small">
      <n-form-item label="显示名称">
        <n-input :value="modelValue.Name" @update:value="(val) => updateRoot('Name', val)" />
      </n-form-item>
      
      <n-form-item label="内容类型">
        <n-tag type="info">{{ modelValue.CollectionType }}</n-tag>
      </n-form-item>

      <n-divider title-placement="left">语言与国家</n-divider>
      <n-form-item label="元数据语言 (PreferredMetadataLanguage)">
        <n-input :value="modelValue.LibraryOptions?.PreferredMetadataLanguage" @update:value="(val) => updateLibOpt('PreferredMetadataLanguage', val)" placeholder="zh" />
      </n-form-item>
      <n-form-item label="图片语言 (PreferredImageLanguage)">
        <n-input :value="modelValue.LibraryOptions?.PreferredImageLanguage" @update:value="(val) => updateLibOpt('PreferredImageLanguage', val)" placeholder="zh" />
      </n-form-item>
      <n-form-item label="国家代码 (MetadataCountryCode)">
        <n-input :value="modelValue.LibraryOptions?.MetadataCountryCode" @update:value="(val) => updateLibOpt('MetadataCountryCode', val)" placeholder="CN" />
      </n-form-item>
      
      <n-divider title-placement="left">媒体路径</n-divider>
      <n-dynamic-input
        :value="pathList"
        placeholder="请输入路径"
        @update:value="handlePathsChange"
      >
        <template #create-button-default>添加路径</template>
      </n-dynamic-input>

      <n-divider title-placement="left">刮削设置</n-divider>
      <n-form-item label="本地元数据读取器 (NFO)">
        <n-checkbox-group :value="readerOrder" @update:value="handleReaderChange">
          <n-space>
            <n-checkbox value="Nfo">Nfo</n-checkbox>
            <n-checkbox value="Emby Xml">Emby Xml</n-checkbox>
          </n-space>
        </n-checkbox-group>
      </n-form-item>
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits(['update:modelValue'])

const pathList = computed(() => {
  return (props.modelValue.LibraryOptions?.PathInfos || []).map((p: any) => p.Path)
})

const readerOrder = computed(() => {
  const disabled = props.modelValue.LibraryOptions?.DisabledLocalMetadataReaders || []
  const all = ["Nfo", "Emby Xml"]
  return all.filter(r => !disabled.includes(r))
})

const updateRoot = (key: string, val: any) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  data[key] = val
  emit('update:modelValue', data)
}

const updateLibOpt = (key: string, val: any) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  data.LibraryOptions[key] = val
  emit('update:modelValue', data)
}

const handlePathsChange = (paths: string[]) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  data.LibraryOptions.PathInfos = paths.filter(p => p).map(p => ({ Path: p }))
  emit('update:modelValue', data)
}

const handleReaderChange = (val: string[]) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  const all = ["Nfo", "Emby Xml"]
  data.LibraryOptions.DisabledLocalMetadataReaders = all.filter(r => !val.includes(r))
  data.LibraryOptions.LocalMetadataReaderOrder = val
  emit('update:modelValue', data)
}
</script>
