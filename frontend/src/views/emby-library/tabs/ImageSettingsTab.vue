<template>
  <div class="image-settings-tab">
    <n-alert type="info" size="small" style="margin-bottom: 16px;">
      配置各媒体类型所使用的图片下载器及图片参数。开启开关后可设置下载数量与最小宽度。
    </n-alert>
    <n-collapse :default-expanded-names="activeTypes">
      <n-collapse-item v-for="typeKey in activeTypes" :key="typeKey" :title="getTypeLabel(typeKey)" :name="typeKey">
        <n-space vertical size="large">
          <!-- 图片下载器选择 -->
          <n-form-item :label="'图片下载器 (ImageFetchers)'" size="small">
            <n-checkbox-group :value="getTypeOption(typeKey).ImageFetchers" @update:value="(val) => updateTypeOption(typeKey, 'ImageFetchers', val)">
              <n-space>
                <n-checkbox v-for="fetcher in getAvailableFetchers(typeKey)" :key="fetcher" :value="fetcher">
                  {{ fetcher }}
                </n-checkbox>
              </n-space>
            </n-checkbox-group>
          </n-form-item>

          <!-- 图片参数设置 (仿 Web UI 逻辑) -->
          <div v-if="hasImageOptions(typeKey)">
            <n-text depth="3" strong style="display: block; margin-bottom: 12px;">图片参数配置 (ImageOptions)</n-text>
            <n-grid :cols="1" :y-gap="12">
              <n-gi v-for="imgType in getAllowedImages(typeKey)" :key="imgType">
                <n-card size="small" embedded :bordered="false">
                  <n-space align="center" justify="space-between">
                    <n-space align="center">
                      <n-switch 
                        :value="isImageEnabled(typeKey, imgType)" 
                        @update:value="(val) => handleImageToggle(typeKey, imgType, val)"
                      />
                      <n-text strong>{{ imgType }}</n-text>
                    </n-space>
                    
                    <n-space v-if="isImageEnabled(typeKey, imgType)" align="center">
                      <n-text depth="3">数量限制:</n-text>
                      <n-input-number 
                        size="tiny" 
                        style="width: 80px"
                        :value="getImageOptionValue(typeKey, imgType, 'Limit')" 
                        :min="1" :max="10"
                        @update:value="(val) => updateImageOption(typeKey, imgType, 'Limit', val)"
                      />
                      <n-divider vertical />
                      <n-text depth="3">最小宽度:</n-text>
                      <n-input-number 
                        size="tiny" 
                        style="width: 100px"
                        :value="getImageOptionValue(typeKey, imgType, 'MinWidth')" 
                        :min="0" :step="100"
                        @update:value="(val) => updateImageOption(typeKey, imgType, 'MinWidth', val)"
                      />
                    </n-space>
                  </n-space>
                </n-card>
              </n-gi>
            </n-grid>
          </div>
        </n-space>
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
  Movie: ["TheMovieDb", "TheTVDB", "FanArt", "The Open Movie Database", "Image Capture"],
  Series: ["TheMovieDb", "The Open Movie Database", "FanArt", "TheTVDB"],
  Season: ["TheMovieDb", "FanArt", "TheTVDB"],
  Episode: ["TheMovieDb", "TheTVDB", "The Open Movie Database", "Image Capture"]
}

const UI_IMAGE_OPTS_FILTER: any = {
  Movie: ["Primary", "Art", "Banner", "Disc", "Logo", "Thumb", "Backdrop"],
  Series: ["Primary", "Art", "Banner", "Logo", "Thumb", "Backdrop"],
  Season: ["Primary", "Banner", "Thumb"],
  Episode: []
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

const hasImageOptions = (typeKey: string) => {
  return UI_IMAGE_OPTS_FILTER[typeKey]?.length > 0
}

const getAllowedImages = (typeKey: string) => {
  return UI_IMAGE_OPTS_FILTER[typeKey] || []
}

// 检查某个图片类型是否“启用”（Limit > 0 即为启用）
const isImageEnabled = (typeKey: string, imgType: string) => {
  const typeOpt = getTypeOption(typeKey)
  const imgOpt = typeOpt.ImageOptions?.find((i: any) => i.Type === imgType)
  return imgOpt ? imgOpt.Limit > 0 : false
}

const getImageOptionValue = (typeKey: string, imgType: string, field: 'Limit' | 'MinWidth') => {
  const typeOpt = getTypeOption(typeKey)
  const imgOpt = typeOpt.ImageOptions?.find((i: any) => i.Type === imgType)
  if (imgOpt) return imgOpt[field]
  return field === 'Limit' ? 1 : 0
}

const handleImageToggle = (typeKey: string, imgType: string, enabled: boolean) => {
  updateImageOption(typeKey, imgType, 'Limit', enabled ? 1 : 0)
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

const updateImageOption = (typeKey: string, imgType: string, field: string, value: any) => {
  const data = JSON.parse(JSON.stringify(props.modelValue))
  if (!data.LibraryOptions) data.LibraryOptions = {}
  if (!data.LibraryOptions.TypeOptions) data.LibraryOptions.TypeOptions = []

  let typeOpt = data.LibraryOptions.TypeOptions.find((o: any) => o.Type === typeKey)
  if (!typeOpt) {
    typeOpt = { Type: typeKey, MetadataFetchers: [], ImageFetchers: [], ImageOptions: [] }
    data.LibraryOptions.TypeOptions.push(typeOpt)
  }
  
  if (!typeOpt.ImageOptions) typeOpt.ImageOptions = []
  let imgOpt = typeOpt.ImageOptions.find((i: any) => i.Type === imgType)
  if (!imgOpt) {
    imgOpt = { Type: imgType, Limit: 0, MinWidth: 0 }
    typeOpt.ImageOptions.push(imgOpt)
  }
  
  imgOpt[field] = value
  emit('update:modelValue', data)
}
</script>