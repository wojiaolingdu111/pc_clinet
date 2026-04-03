import { computed, ref } from 'vue';
import { defineStore } from 'pinia';
import { deleteVoiceProfile, listVoices, type VoiceProfile } from '../api/tauri';

export const useVoicesStore = defineStore('voices', () => {
  const builtinVoices = ref<VoiceProfile[]>([]);
  const customVoices = ref<VoiceProfile[]>([]);
  const selectedVoiceId = ref('female_01');
  const loading = ref(false);

  const allVoices = computed(() => [...builtinVoices.value, ...customVoices.value]);
  const selectedVoice = computed(
    () => allVoices.value.find((voice) => voice.id === selectedVoiceId.value) ?? null,
  );

  async function refreshVoices() {
    loading.value = true;
    try {
      const response = await listVoices();
      builtinVoices.value = response.builtinVoices;
      customVoices.value = response.customVoices;
      if (!allVoices.value.some((voice) => voice.id === selectedVoiceId.value) && allVoices.value[0]) {
        selectedVoiceId.value = allVoices.value[0].id;
      }
    } finally {
      loading.value = false;
    }
  }

  async function removeVoiceProfile(voiceProfileId: string) {
    await deleteVoiceProfile(voiceProfileId);
    customVoices.value = customVoices.value.filter((voice) => voice.id !== voiceProfileId);
  }

  return {
    builtinVoices,
    customVoices,
    selectedVoiceId,
    loading,
    allVoices,
    selectedVoice,
    refreshVoices,
    removeVoiceProfile,
  };
});
