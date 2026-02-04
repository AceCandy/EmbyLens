<template>
  <div class="common-features">
    <n-grid :cols="2" :x-gap="24">
      <n-gi span="2">
        <n-divider title-placement="left">核心扫描与监控</n-divider>
      </n-gi>
      <n-gi v-for="opt in scanOptions" :key="opt.key">
        <n-form-item :label="opt.label">
          <n-switch :value="getVal(opt.key)" @update:value="(val) => setVal(opt.key, val)" />
        </n-form-item>
      </n-gi>

      <n-gi span="2">
        <n-divider title-placement="left">元数据与保存设置</n-divider>
      </n-gi>
      <n-gi v-for="opt in saveOptions" :key="opt.key">
        <n-form-item :label="opt.label">
          <n-switch :value="getVal(opt.key)" @update:value="(val) => setVal(opt.key, val)" />
        </n-form-item>
      </n-gi>

      <n-gi span="2">
        <n-divider title-placement="left">高级播放与刮削控制</n-divider>
      </n-gi>
      <n-gi v-for="opt in otherOptions" :key="opt.key">
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

const scanOptions = [
  { label: '启用实时监控 (EnableRealtimeMonitor)', key: 'EnableRealtimeMonitor' },
  { label: '提取章节图片 (EnableChapterImageExtraction)', key: 'EnableChapterImageExtraction' },
  { label: '库扫描期间提取章节图 (ExtractChapterImagesDuringLibraryScan)', key: 'ExtractChapterImagesDuringLibraryScan' },
  { label: '启用标记检测 (EnableMarkerDetection)', key: 'EnableMarkerDetection' },
  { label: '库扫描期间检测标记 (EnableMarkerDetectionDuringLibraryScan)', key: 'EnableMarkerDetectionDuringLibraryScan' },
  { label: '忽略隐藏文件和文件夹 (IgnoreHiddenFiles)', key: 'IgnoreHiddenFiles' },
  { label: '启用压缩媒体文件读取 (EnableArchiveMediaFiles)', key: 'EnableArchiveMediaFiles' }
]

const saveOptions = [
  { label: '将媒体元数据保存到媒体文件夹 (SaveLocalMetadata)', key: 'SaveLocalMetadata' },
  { label: '将元数据文件设为隐藏 (SaveMetadataHidden)', key: 'SaveMetadataHidden' },
  { label: '在本地保存缩略图集 (SaveLocalThumbnailSets)', key: 'SaveLocalThumbnailSets' },
  { label: '将歌词保存到媒体文件夹 (SaveLyricsWithMedia)', key: 'SaveLyricsWithMedia' },
  { label: '将字幕保存到媒体文件夹 (SaveSubtitlesWithMedia)', key: 'SaveSubtitlesWithMedia' },
  { label: '启用本地图片缓存 (CacheImages)', key: 'CacheImages' },
  { label: '提前下载图像 (DownloadImagesInAdvance)', key: 'DownloadImagesInAdvance' }
]

const otherOptions = [
  { label: '启用按文件多版本合并 (EnableMultiVersionByFiles)', key: 'EnableMultiVersionByFiles' },
  { label: '启用按元数据多版本合并 (EnableMultiVersionByMetadata)', key: 'EnableMultiVersionByMetadata' },
  { label: '允许刮削互联网元数据 (EnableInternetProviders)', key: 'EnableInternetProviders' },
  { label: '优先使用内嵌标题 (EnableEmbeddedTitles)', key: 'EnableEmbeddedTitles' },
  { label: '从搜索结果中排除此库 (ExcludeFromSearch)', key: 'ExcludeFromSearch' },
  { label: '启用照片支持 (EnablePhotos)', key: 'EnablePhotos' },
  { label: '启用 .plexignore 支持 (EnablePlexIgnore)', key: 'EnablePlexIgnore' }
]

const getVal = (key: string) => !!props.modelValue.LibraryOptions?.[key]
const setVal = (key: string, val: boolean) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  data.LibraryOptions[key] = val
  emit('update:modelValue', data)
}
</script>