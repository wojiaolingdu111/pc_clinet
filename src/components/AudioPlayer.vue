<script setup lang="ts">
import { computed } from 'vue';
import type { GenerateSpeechResult } from '../api/tauri';

const props = defineProps<{
  audioPath: string;
  result: GenerateSpeechResult | null;
}>();

const canPreview = computed(() => props.audioPath.startsWith('http://') || props.audioPath.startsWith('https://') || props.audioPath.startsWith('asset:') || props.audioPath.startsWith('/'));
</script>

<template>
  <section class="section-block">
    <div class="section-head">
      <div>
        <p class="section-kicker">生成结果</p>
        <h2>播放与导出</h2>
      </div>
      <span v-if="result" class="result-chip" :class="result.status">{{ result.status }}</span>
    </div>

    <div v-if="audioPath" class="player-card">
      <audio v-if="canPreview" :src="audioPath" controls preload="metadata" />
      <p v-else>当前音频路径由桌面端生成，浏览器预览模式下无法直接播放：{{ audioPath }}</p>
      <a v-if="canPreview" class="download-btn" :href="audioPath" download>导出 wav</a>
    </div>
    <p v-else class="empty-copy">生成完成后会在这里显示音频播放器和导出入口。</p>

    <p v-if="result?.error" class="error-text">{{ result.error }}</p>
  </section>
</template>

<style scoped>
.section-block {
  display: grid;
  gap: 16px;
  margin-top: 28px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.section-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #0d9488;
}

h2 {
  margin: 0;
}

.result-chip {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(20, 33, 61, 0.08);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.result-chip.success {
  background: rgba(22, 163, 74, 0.12);
  color: #166534;
}

.result-chip.failed {
  background: rgba(176, 42, 55, 0.12);
  color: #8a1c28;
}

.player-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 20px;
  background: rgba(20, 33, 61, 0.05);
}

audio {
  width: 100%;
}

.download-btn {
  display: inline-flex;
  width: fit-content;
  padding: 10px 16px;
  border-radius: 12px;
  background: #14213d;
  color: #fff;
  text-decoration: none;
}

.empty-copy,
.error-text {
  margin: 0;
}

.error-text {
  color: #8a1c28;
}
</style>
