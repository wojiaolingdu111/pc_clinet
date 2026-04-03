<script setup lang="ts">
import { ref } from 'vue';
import { cloneVoice } from '../api/tauri';
import { useVoicesStore } from '../stores/voices';

const name = ref('');
const audioPath = ref('');
const language = ref('zh');
const busy = ref(false);
const statusText = ref('首版先保留声音克隆入口，后续接入真实参考音频驱动的 voice cloning。');
const voicesStore = useVoicesStore();

async function submitClone() {
  if (!name.value.trim() || !audioPath.value.trim()) {
    statusText.value = '请填写 profile 名称和参考音频路径。';
    return;
  }

  busy.value = true;
  try {
    const result = await cloneVoice({
      name: name.value.trim(),
      audioPath: audioPath.value.trim(),
      language: language.value,
    });
    await voicesStore.refreshVoices();
    voicesStore.selectedVoiceId = result.voiceProfileId;
    statusText.value = `已创建 profile：${result.voiceProfileId}`;
    name.value = '';
    audioPath.value = '';
  } catch (error) {
    statusText.value = error instanceof Error ? error.message : '创建 profile 失败。';
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="section-block">
    <div>
      <p class="section-kicker">声音克隆</p>
      <h2>准备自定义音色</h2>
    </div>

    <label class="field">
      <span>Profile 名称</span>
      <input v-model="name" type="text" placeholder="例如：my_voice" />
    </label>

    <label class="field">
      <span>参考音频路径</span>
      <input v-model="audioPath" type="text" placeholder="例如：/path/to/reference.wav" />
    </label>

    <label class="field">
      <span>语言</span>
      <select v-model="language">
        <option value="zh">中文</option>
        <option value="en">English</option>
      </select>
    </label>

    <button class="primary-btn" :disabled="busy" @click="submitClone">
      {{ busy ? '处理中...' : '创建音色 Profile' }}
    </button>

    <p class="helper-text">{{ statusText }}</p>
  </section>
</template>

<style scoped>
.section-block {
  display: grid;
  gap: 14px;
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
  font-size: 1.4rem;
}

.field {
  display: grid;
  gap: 8px;
}

.field span {
  font-size: 14px;
  font-weight: 700;
}

input,
select {
  border: 1px solid rgba(20, 33, 61, 0.12);
  border-radius: 14px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.9);
}

.primary-btn {
  padding: 12px 16px;
  background: linear-gradient(135deg, #14b8a6, #6ee7b7);
  color: #083344;
  font-weight: 800;
}

.helper-text {
  margin: 0;
  color: rgba(20, 33, 61, 0.72);
}
</style>
