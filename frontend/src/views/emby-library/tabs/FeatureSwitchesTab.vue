<template>
  <div class="feature-switches-tab">
    <n-form label-placement="left" label-width="240" size="small">
      <!-- 1. 通用功能 -->
      <CommonFeatures v-model="localModel" />

      <!-- 2. 电影专属 -->
      <MovieFeatures v-if="isMovie" v-model="localModel" />

      <!-- 3. 电视节目专属 -->
      <SeriesFeatures v-if="isSeries" v-model="localModel" />
    </n-form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CommonFeatures from './features/CommonFeatures.vue'
import MovieFeatures from './features/MovieFeatures.vue'
import SeriesFeatures from './features/SeriesFeatures.vue'

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits(['update:modelValue'])

const localModel = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const collectionType = computed(() => 
  props.modelValue.CollectionType || props.modelValue.LibraryOptions?.ContentType
)

const isMovie = computed(() => collectionType.value === 'movies')
const isSeries = computed(() => collectionType.value === 'tvshows')
</script>
