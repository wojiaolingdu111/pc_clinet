<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import AudioPlayer from './components/AudioPlayer.vue';
import CloneVoicePanel from './components/CloneVoicePanel.vue';
import TaskList from './components/TaskList.vue';
import TextInputPanel from './components/TextInputPanel.vue';
import VoiceSelector from './components/VoiceSelector.vue';
import { useSettingsStore } from './stores/settings';
import { useTtsStore } from './stores/tts';
import { useVoicesStore } from './stores/voices';

const settingsStore = useSettingsStore();
const ttsStore = useTtsStore();
const voicesStore = useVoicesStore();
const runtimeError = ref('');

const serviceBadge = computed(() => {
  if (settingsStore.serviceStatus.running) {
    return '服务运行中';
  }
  if (settingsStore.serviceStatus.mode === 'offline') {
    return '浏览器预览模式';
  }
  return '服务未连接';
});

async function bootstrap() {
  runtimeError.value = '';
  try {
    await Promise.all([settingsStore.refreshServiceStatus(), voicesStore.refreshVoices()]);
  } catch (error) {
    runtimeError.value = error instanceof Error ? error.message : '初始化失败。';
  }
}

onMounted(() => {
  void bootstrap();
});
</script>

<template>
  <div class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">PC 端本地语音合成</p>
        <h1>AI ToReder</h1>
        <p class="hero-copy">
          使用 Tauri + Rust + Python 构建的桌面式本地 TTS 工作台。当前版本已具备 V0.1
          的交互骨架，可继续接入真实 Coqui TTS 推理和声音克隆能力。
        </p>
      </div>
      <div class="status-panel">
        <span class="status-chip">{{ serviceBadge }}</span>
        <p>{{ settingsStore.serviceStatus.message }}</p>
        <p>输出目录：{{ settingsStore.outputDirectory }}</p>
      </div>
    </header>

    <p v-if="runtimeError" class="runtime-error">{{ runtimeError }}</p>

    <main class="workspace-grid">
      <section class="panel panel-main">
        <TextInputPanel />
        <AudioPlayer :audio-path="ttsStore.currentAudioPath" :result="ttsStore.currentResult" />
      </section>

      <section class="panel panel-side">
        <VoiceSelector />
        <CloneVoicePanel />
      </section>

      <section class="panel panel-wide">
        <TaskList :tasks="ttsStore.tasks" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.shell {
  max-width: 1240px;
  margin: 0 auto;
  padding: 40px 20px 56px;
}

.hero {
  display: grid;
  gap: 24px;
  grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.9fr);
  align-items: end;
  margin-bottom: 28px;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #117864;
}

h1 {
  margin: 0;
  font-size: clamp(2.8rem, 5vw, 4.8rem);
  line-height: 0.95;
}

.hero-copy {
  max-width: 760px;
  margin: 18px 0 0;
  font-size: 1.05rem;
  color: rgba(20, 33, 61, 0.8);
}

.status-panel {
  padding: 22px;
  border: 1px solid rgba(20, 33, 61, 0.08);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 18px 45px rgba(20, 33, 61, 0.09);
}

.status-chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: #14213d;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.status-panel p {
  margin: 12px 0 0;
  color: rgba(20, 33, 61, 0.74);
}

.runtime-error {
  margin: 0 0 18px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(176, 42, 55, 0.12);
  color: #8a1c28;
}

.workspace-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 0.95fr);
}

.panel {
  border: 1px solid rgba(20, 33, 61, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: 0 20px 50px rgba(20, 33, 61, 0.08);
  backdrop-filter: blur(12px);
}

.panel-main,
.panel-side,
.panel-wide {
  padding: 24px;
}

.panel-side {
  display: grid;
  gap: 20px;
  align-content: start;
}

.panel-wide {
  grid-column: 1 / -1;
}

@media (max-width: 960px) {
  .hero,
  .workspace-grid {
    grid-template-columns: 1fr;
  }

  .shell {
    padding: 24px 16px 40px;
  }
}
</style>
