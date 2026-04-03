<script setup lang="ts">
import type { SpeechTask } from '../stores/tts';

defineProps<{
  tasks: SpeechTask[];
}>();
</script>

<template>
  <section class="section-block">
    <div>
      <p class="section-kicker">任务管理</p>
      <h2>最近任务</h2>
    </div>

    <div v-if="tasks.length" class="task-grid">
      <article v-for="task in tasks" :key="task.id" class="task-card">
        <header>
          <strong>{{ task.id }}</strong>
          <span class="task-status" :class="task.status">{{ task.status }}</span>
        </header>
        <p>{{ task.text }}</p>
        <small>voiceId: {{ task.voiceId }}</small>
        <small>createdAt: {{ task.createdAt }}</small>
        <small v-if="task.audioPath">audioPath: {{ task.audioPath }}</small>
        <small v-if="task.error" class="error-text">{{ task.error }}</small>
      </article>
    </div>
    <p v-else class="empty-copy">还没有任务，点击“开始生成”后会在这里记录状态。</p>
  </section>
</template>

<style scoped>
.section-block {
  display: grid;
  gap: 18px;
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

.task-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.task-card {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(20, 33, 61, 0.05);
}

.task-card header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.task-card p,
.task-card small {
  margin: 0;
}

.task-status {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(20, 33, 61, 0.08);
  font-size: 12px;
  font-weight: 800;
}

.task-status.success {
  background: rgba(22, 163, 74, 0.12);
  color: #166534;
}

.task-status.failed {
  background: rgba(176, 42, 55, 0.12);
  color: #8a1c28;
}

.error-text {
  color: #8a1c28;
}
</style>
