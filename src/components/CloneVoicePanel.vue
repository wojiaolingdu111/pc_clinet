<script setup lang="ts">
import { ref } from 'vue';
import { cloneVoice } from '../api/tauri';
import { useVoicesStore } from '../stores/voices';

const name = ref('');
const audioPath = ref('');
const language = ref('zh');
const busy = ref(false);
const statusText = ref('上传 6 秒以上的清晰录音，即可克隆您的声音用于 TTS 合成。');
const voicesStore = useVoicesStore();

async function pickAudioFile() {
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    const path = await invoke<string | null>('pick_audio_file');
    if (path) audioPath.value = path;
  } catch {
    // 浏览器预览模式，用户可手动输入路径
  }
}

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
      <span>参考音频（WAV / MP3 / FLAC，建议 6 秒以上清晰录音）</span>
      <div class="file-picker-row">
        <input v-model="audioPath" type="text" placeholder="点击「浏览」选择文件" readonly />
        <button class="secondary-btn" :disabled="busy" @click="pickAudioFile">浏览…</button>
      </div>
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

.file-picker-row {
  display: flex;
  gap: 8px;
}

.file-picker-row input {
  flex: 1;
  cursor: default;
}

.secondary-btn {
  padding: 12px 16px;
  border: 1px solid rgba(20, 33, 61, 0.18);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.9);
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}

.secondary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
