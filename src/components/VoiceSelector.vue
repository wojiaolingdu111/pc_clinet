<script setup lang="ts">
import { computed } from 'vue';
import { useVoicesStore } from '../stores/voices';

const voicesStore = useVoicesStore();

const groupedVoices = computed(() => [
  {
    title: '内置音色',
    items: voicesStore.builtinVoices,
  },
  {
    title: '自定义音色',
    items: voicesStore.customVoices,
  },
]);
</script>

<template>
  <section class="section-block">
    <div class="section-head">
      <div>
        <p class="section-kicker">音色配置</p>
        <h2>选择 Voice Profile</h2>
      </div>
      <button class="ghost-btn" :disabled="voicesStore.loading" @click="voicesStore.refreshVoices()">
        刷新
      </button>
    </div>

    <div v-for="group in groupedVoices" :key="group.title" class="voice-group">
      <h3>{{ group.title }}</h3>
      <label
        v-for="voice in group.items"
        :key="voice.id"
        class="voice-card"
        :class="{ active: voicesStore.selectedVoiceId === voice.id }"
      >
        <input v-model="voicesStore.selectedVoiceId" type="radio" name="voice" :value="voice.id" />
        <div>
          <strong>{{ voice.name }}</strong>
          <p>{{ voice.description || voice.id }}</p>
          <small>{{ voice.language.join(' / ') }}</small>
        </div>
      </label>
    </div>
  </section>
</template>

<style scoped>
.section-block {
  display: grid;
  gap: 16px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 12px;
}

.section-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #0d9488;
}

h2,
h3 {
  margin: 0;
}

.ghost-btn {
  padding: 10px 16px;
  background: rgba(20, 33, 61, 0.08);
  color: #14213d;
  font-weight: 700;
}

.voice-group {
  display: grid;
  gap: 10px;
}

.voice-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  border: 1px solid rgba(20, 33, 61, 0.1);
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
}

.voice-card.active {
  border-color: rgba(13, 148, 136, 0.42);
  background: rgba(13, 148, 136, 0.08);
}

.voice-card p,
.voice-card small {
  margin: 4px 0 0;
  color: rgba(20, 33, 61, 0.7);
}
</style>
