<template>
  <div class="voice-controls">
    <button 
      class="voice-btn"
      :class="{ 'listening': isListening, 'processing': isProcessing }"
      @click="handleVoiceClick"
      :disabled="isProcessing && !isSpeaking"
    >
      <svg v-if="!isListening && !isProcessing && !isSpeaking" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z" />
      </svg>
      <svg v-else-if="isListening" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6,6H18V18H6V6Z" />
      </svg>
      <svg v-else-if="isSpeaking" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M6 6h12v12H6z"/>
      </svg>
      <div v-else class="spinner"></div>
    </button>
    <span class="voice-status">
      {{ statusText }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  isListening: boolean
  isProcessing: boolean
  isSpeaking?: boolean
}>()

const emit = defineEmits<{
  startListening: []
  stopListening: []
  stopSpeaking: []
}>()

const statusText = ''
//computed(() => {
 // if (props.isProcessing) return 'Processing...'
 // if (props.isListening) return 'Listening... (Click to stop)'
 // return 'Click to speak'
//})

const handleVoiceClick = () => {
  if (props.isSpeaking) {
    emit('stopSpeaking')
  } else if (props.isListening) {
    emit('stopListening')
  } else {
    emit('startListening')
  }
}
</script>

<style scoped>
.voice-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.voice-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.voice-btn:hover:not(:disabled) {
  cursor: pointer;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
}

.voice-btn.listening {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  animation: pulse 1.5s infinite;
}

.voice-btn.processing {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  cursor: not-allowed;
}

.voice-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.voice-status {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  font-weight: 500;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>