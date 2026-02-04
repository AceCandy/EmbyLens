<template>
  <div class="type-options-tab">
    <n-collapse :default-expanded-names="activeTypes">
      <n-collapse-item v-for="typeKey in activeTypes" :key="typeKey" :title="getTypeLabel(typeKey)" :name="typeKey">
        <n-space vertical size="large">
          <!-- 元数据刮削器 -->
          <n-form-item :label="'元数据下载器 (MetadataFetchers)'" size="small">
            <n-checkbox-group :value="getTypeOption(typeKey).MetadataFetchers" @update:value="(val) => updateTypeOption(typeKey, 'MetadataFetchers', val)">
              <n-space>
                <n-checkbox v-for="fetcher in getAvailableFetchers(typeKey, 'Metadata')" :key="fetcher" :value="fetcher">
                  {{ fetcher }}
                </n-checkbox>
              </n-space>
            </n-checkbox-group>
          </n-form-item>

          <!-- 图片下载器 -->
          <n-form-item :label="'图片下载器 (ImageFetchers)'" size="small">
            <n-checkbox-group :value="getTypeOption(typeKey).ImageFetchers" @update:value="(val) => updateTypeOption(typeKey, 'ImageFetchers', val)">
              <n-space>
                <n-checkbox v-for="fetcher in getAvailableFetchers(typeKey, 'Image')" :key="fetcher" :value="fetcher">
                  {{ fetcher }}
                </n-checkbox>
              </n-space>
            </n-checkbox-group>
          </n-form-item>

          <!-- 图片参数设置 -->
          <div v-if="hasImageOptions(typeKey)">
            <n-text depth="3" strong style="display: block; margin-bottom: 8px;">图片参数 (ImageOptions)</n-text>
            <n-table size="small" :single-line="false">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>数量限制 (Limit)</th>
                  <th>最小宽度 (MinWidth)</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="imgType in getAllowedImages(typeKey)" :key="imgType">
                  <td>{{ imgType }}</td>
                  <td>
                    <n-input-number 
                      size="tiny" 
                      :value="getImageOption(typeKey, imgType).Limit" 
                      :min="0" :max="10"
                      @update:value="(val) => updateImageOption(typeKey, imgType, 'Limit', val)"
                    />
                  </td>
                  <td>
                    <n-input-number 
                      size="tiny" 
                      :value="getImageOption(typeKey, imgType).MinWidth" 
                      :min="0" :step="100"
                      @update:value="(val) => updateImageOption(typeKey, imgType, 'MinWidth', val)"
                    />
                  </td>
                </tr>
              </tbody>
            </n-table>
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
  Movie: {
    Metadata: ["TheMovieDb", "The Open Movie Database", "TheTVDB"],
    Image: ["TheMovieDb", "TheTVDB", "FanArt", "The Open Movie Database", "Image Capture"]
  },
  Series: {
    Metadata: ["TheMovieDb", "The Open Movie Database", "TheTVDB"],
    Image: ["TheMovieDb", "The Open Movie Database", "FanArt", "TheTVDB"]
  },
  Season: {
    Metadata: ["TheMovieDb", "TheTVDB"],
    Image: ["TheMovieDb", "FanArt", "TheTVDB"]
  },
  Episode: {
    Metadata: ["TheMovieDb", "The Open Movie Database", "TheTVDB"],
    Image: ["TheMovieDb", "TheTVDB", "The Open Movie Database", "Image Capture"]
  }
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

const getAvailableFetchers = (typeKey: string, category: 'Metadata' | 'Image') => {
  return STRICT_FETCHERS[typeKey]?.[category] || []
}

const hasImageOptions = (typeKey: string) => {
  return UI_IMAGE_OPTS_FILTER[typeKey]?.length > 0
}

const getAllowedImages = (typeKey: string) => {
  return UI_IMAGE_OPTS_FILTER[typeKey] || []
}

const getImageOption = (typeKey: string, imgType: string) => {
  const typeOpt = getTypeOption(typeKey)
  const imgOpts = typeOpt.ImageOptions || []
  return imgOpts.find((i: any) => i.Type === imgType) || { Type: imgType, Limit: 1, MinWidth: 0 }
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
  let typeOpt = data.LibraryOptions.TypeOptions.find((o: any) => o.Type === typeKey)
  if (!typeOpt) {
    typeOpt = { Type: typeKey, MetadataFetchers: [], ImageFetchers: [], ImageOptions: [] }
    data.LibraryOptions.TypeOptions.push(typeOpt)
  }
  
  if (!typeOpt.ImageOptions) typeOpt.ImageOptions = []
  let imgOpt = typeOpt.ImageOptions.find((i: any) => i.Type === imgType)
  if (!imgOpt) {
    imgOpt = { Type: imgType, Limit: 1, MinWidth: 0 }
    typeOpt.ImageOptions.push(imgOpt)
  }
  
  imgOpt[field] = value
  emit('update:modelValue', data)
}
</script>
