<template>
  <div class="metadata-fetchers-tab">
    <n-alert type="info" size="small" style="margin-bottom: 16px;">
      请选择各媒体类型所使用的元数据刮削器。
    </n-alert>
    <n-collapse :default-expanded-names="activeTypes">
      <n-collapse-item v-for="typeKey in activeTypes" :key="typeKey" :title="getTypeLabel(typeKey)" :name="typeKey">
        <n-form-item :label="'元数据下载器 (MetadataFetchers)'" size="small">
          <n-checkbox-group :value="getTypeOption(typeKey).MetadataFetchers" @update:value="(val) => updateTypeOption(typeKey, 'MetadataFetchers', val)">
            <n-space>
              <n-checkbox v-for="fetcher in getAvailableFetchers(typeKey)" :key="fetcher" :value="fetcher">
                {{ fetcher }}
              </n-checkbox>
            </n-space>
          </n-checkbox-group>
        </n-form-item>
      </n-collapse-item>
    </n-collapse>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits(['update:modelValue'])

const STRICT_FETCHERS: any = {
  Movie: ["TheMovieDb", "The Open Movie Database", "TheTVDB"],
  Series: ["TheMovieDb", "The Open Movie Database", "TheTVDB"],
  Season: ["TheMovieDb", "TheTVDB"],
  Episode: ["TheMovieDb", "The Open Movie Database", "TheTVDB"]
}

const TYPE_TRANS: any = {
  Movie: "电影 (Movie)",
  Series: "剧集 (Series)",
  Season: "季 (Season)",
  Episode: "集 (Episode)"
}

const activeTypes = computed(() => {
  const contentType = props.modelValue.LibraryOptions?.ContentType
  if (contentType === 'tvshows') return ["Series", "Season", "Episode"]
  if (contentType === 'movies') return ["Movie"]
  return ["Movie", "Series", "Season", "Episode"]
})

const getTypeLabel = (key: string) => TYPE_TRANS[key] || key

const getTypeOption = (typeKey: string) => {
  const options = props.modelValue.LibraryOptions?.TypeOptions || []
  return options.find((o: any) => o.Type === typeKey) || { Type: typeKey, MetadataFetchers: [], ImageFetchers: [], ImageOptions: [] }
}

const getAvailableFetchers = (typeKey: string) => {
  return STRICT_FETCHERS[typeKey] || []
}

const updateTypeOption = (typeKey: string, key: string, value: any) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  if (!data.LibraryOptions.TypeOptions) data.LibraryOptions.TypeOptions = []
  
  let typeOpt = data.LibraryOptions.TypeOptions.find((o: any) => o.Type === typeKey)
  if (!typeOpt) {
    typeOpt = { Type: typeKey, MetadataFetchers: [], ImageFetchers: [], ImageOptions: [] }
    data.LibraryOptions.TypeOptions.push(typeOpt)
  }
  
  typeOpt[key] = value
  emit('update:modelValue', data)
}
</script>
