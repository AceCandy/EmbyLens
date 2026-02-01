<template>
  <div class="toolkit-container">
    <n-space vertical size="large">
      <div class="page-header">
        <n-h2 prefix="bar" align-text><n-text type="primary">AI 实验室</n-text></n-h2>
        <n-text depth="3">配置 OpenAI 兼容模型，利用大语言模型辅助元数据处理与语义分析。</n-text>
      </div>

      <n-grid :x-gap="12" :y-gap="12" :cols="24" item-responsive responsive="screen">
        <!-- 左侧：主要功能区 (AI 对话) -->
        <n-gi span="24 m:16">
          <AIChatModule />
        </n-gi>

        <!-- 右侧：配置与说明 -->
        <n-gi span="24 m:8">
          <n-space vertical size="large">
            <AIConfigModule />
            
            <n-card title="关于 AI 实验室" size="small" segmented>
              <n-text depth="3" style="font-size: 13px">
                <p>这是一个独立的 AI 功能演示模块。</p>
                <p>您可以在此配置 OpenAI 兼容的 API 服务，并在左侧进行对话测试。</p>
                <p><b>核心能力：</b></p>
                <ul>
                  <li>支持自定义 API Endpoint 与模型名。</li>
                  <li>支持系统提示词 (System Prompt) 定制。</li>
                  <li>实时语义理解与上下文对话。</li>
                </ul>
                <p>未来此模块的能力将被复用到系统的其他自动化功能中，如剧情简介自动润色、标签语义分类等。</p>
              </n-text>
            </n-card>
          </n-space>
        </n-gi>
      </n-grid>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { NGrid, NGi, NCard, NSpace, NH2, NText } from 'naive-ui'
import AIConfigModule from '@/components/ai/AIConfigModule.vue'
import AIChatModule from '@/components/ai/AIChatModule.vue'
</script>

<style scoped>
/* 移除局部样式，统一使用全局标准 */
</style>