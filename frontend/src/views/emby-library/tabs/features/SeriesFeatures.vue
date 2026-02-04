<template>
  <div class="series-features">
    <n-grid :cols="2" :x-gap="24">
      <n-gi span="2">
        <n-divider title-placement="left">电视节目库专属选项</n-divider>
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
  { label: '自动将剧集分组 (EnableAutomaticSeriesGrouping)', key: 'EnableAutomaticSeriesGrouping' },
  { label: '合并顶级文件夹内容 (MergeTopLevelFolders)', key: 'MergeTopLevelFolders' },
  { label: '折叠单项目录 (CollapseSingleItemFolders)', key: 'CollapseSingleItemFolders' },
  { label: '强制折叠单项目录 (ForceCollapseSingleItemFolders)', key: 'ForceCollapseSingleItemFolders' }
]

const getVal = (key: string) => !!props.modelValue.LibraryOptions?.[key]
const setVal = (key: string, val: boolean) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  data.LibraryOptions[key] = val
  emit('update:modelValue', data)
}
</script>