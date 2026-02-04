<template>
  <div class="movie-features">
    <n-grid :cols="2" :x-gap="24">
      <n-gi span="2">
        <n-divider title-placement="left">电影库专属选项</n-divider>
      </n-gi>
      <n-gi v-for="opt in options" :key="opt.key">
        <n-form-item :label="opt.label">
          <n-switch :value="getVal(opt.key)" @update:value="(val) => setVal(opt.key, val)" />
        </n-form-item>
      </n-gi>
    </n-grid>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])

const options = [
  { label: '自动导入电影合集 (ImportCollections)', key: 'ImportCollections' },
  { label: '启用多分段项目合并 (EnableMultiPartItems)', key: 'EnableMultiPartItems' },
  { label: '允许成人元数据 (EnableAdultMetadata)', key: 'EnableAdultMetadata' }
]

const getVal = (key: string) => !!props.modelValue.LibraryOptions?.[key]
const setVal = (key: string, val: boolean) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  data.LibraryOptions[key] = val
  emit('update:modelValue', data)
}
</script>