<script setup lang="ts">
import { ref } from 'vue';
import { useTtsStore } from '../stores/tts';
import { useVoicesStore } from '../stores/voices';

const ttsStore = useTtsStore();
const voicesStore = useVoicesStore();
const localError = ref('');

async function handleGenerate() {
  localError.value = '';

  try {
    await ttsStore.submitGeneration(voicesStore.selectedVoiceId);
  } catch (error) {
    localError.value = error instanceof Error ? error.message : '生成失败。';
  }
}
</script>

<template>
  <section class="section-block">
    <div class="section-head">
      <div>
        <p class="section-kicker">文本转语音</p>
        <h2>生成本地语音</h2>
      </div>
      <button class="primary-btn" :disabled="ttsStore.isGenerating" @click="handleGenerate">
        {{ ttsStore.isGenerating ? '生成中...' : '开始生成' }}
      </button>
    </div>

    <label class="field">
      <span>文本内容</span>
      <textarea
        v-model="ttsStore.currentText"
        rows="8"
        placeholder="输入要合成的文本，建议先用较短文本做测试。"
      />
    </label>

    <div class="inline-grid">
      <label class="field">
        <span>语速</span>
        <input v-model.number="ttsStore.currentSpeed" type="range" min="0.5" max="1.5" step="0.05" />
        <strong>{{ ttsStore.currentSpeed.toFixed(2) }}x</strong>
      </label>

      <label class="field">
        <span>语言</span>
        <select v-model="ttsStore.currentLanguage">
          <option value="zh">中文</option>
          <option value="en">English</option>
        </select>
      </label>
    </div>

    <p v-if="localError" class="error-text">{{ localError }}</p>
  </section>
</template>

<style scoped>
.section-block {
  display: grid;
  gap: 18px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: start;
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
  font-size: 1.6rem;
}

.primary-btn {
  min-width: 128px;
  padding: 12px 18px;
  background: linear-gradient(135deg, #ff9f1c, #ffbf69);
  color: #14213d;
  font-weight: 800;
  box-shadow: 0 12px 30px rgba(255, 159, 28, 0.28);
}

.primary-btn:disabled {
  cursor: wait;
  opacity: 0.65;
}

.field {
  display: grid;
  gap: 10px;
}

.field span {
  font-size: 14px;
  font-weight: 700;
}

textarea,
select,
input[type='range'] {
  width: 100%;
}

textarea,
select {
  border: 1px solid rgba(20, 33, 61, 0.12);
  border-radius: 18px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
}

textarea {
  resize: vertical;
  min-height: 188px;
}

.inline-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.error-text {
  margin: 0;
  color: #8a1c28;
}

@media (max-width: 640px) {
  .section-head,
  .inline-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
