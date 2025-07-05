<template>
  <div class="chat-interface">
    <div class="messages-container" ref="messagesContainer">
      <div 
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="{ 'user': message.role === 'user', 'assistant': message.role === 'assistant' }"
      >
        <template v-if="message && typeof message.content === 'string' && message.id">
          <div class="message-content">
            <template v-if="message.role === 'assistant'">
              <div v-html="marked(typeof message.content === 'string' ? message.content : String(message.content))"></div>
            </template>
            <template v-else>
              <p>{{ message.content }}</p>
            </template>
            <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
          </div>
        </template>
      </div>
      
      <div v-if="isProcessing" class="message assistant">
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="input-container">
      <div class="input-wrapper">
        <input 
          v-model="inputText"
          type="text" 
          placeholder="Type your message..."
          @keypress.enter="sendMessage"
          @input="handleUserTyping"
          @focus="handleUserTyping"
          @keydown="handleUserTyping"
          :disabled="isProcessing"
          class="message-input"
        />
        <button 
          @click="sendMessage"
          :disabled="!inputText.trim() || isProcessing"
          class="send-button"
        >
          <svg viewBox="0 0 22 32" fill="currentColor" class="send-icon">
            <path d="M3,28L29,16L3,4V12L23,16L3,20V28Z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import type { Message } from '../types'
import { marked } from 'marked'

// Configure marked for better rendering
marked.setOptions({
  breaks: true,  // Convert \n to <br>
  gfm: true,     // GitHub Flavored Markdown
  headerIds: false,
  mangle: false
})

const props = defineProps<{
  messages: Message[]
  isProcessing: boolean
  isSpeaking: boolean
}>()

const emit = defineEmits<{
  sendMessage: [content: string]
  userTyping: []
}>()

const inputText = ref('')
const messagesContainer = ref<HTMLElement>()
const hasTyped = ref(false)

const sendMessage = () => {
  if (!inputText.value.trim() || props.isProcessing) return
  
  emit('sendMessage', inputText.value.trim())
  inputText.value = ''
  hasTyped.value = false // Reset typing flag when message is sent
}

const formatTime = (ts: any) => {
  if (!ts) return '';
  const date = typeof ts === 'string' || typeof ts === 'number' ? new Date(ts) : ts;
  if (!(date instanceof Date) || isNaN(date.getTime())) return '';
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Watch for new messages and scroll to bottom
watch(() => props.messages.length, scrollToBottom)
watch(() => props.isProcessing, scrollToBottom)

// Reset typing flag when processing starts
watch(() => props.isProcessing, (isProcessing) => {
  if (isProcessing) {
    hasTyped.value = false
  }
})

const handleUserTyping = () => {
  if (!hasTyped.value) {
    console.log('User typing detected - emitting userTyping event')
    emit('userTyping')
    hasTyped.value = true
  }
}
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  max-height: calc(100vh - 200px);
}

.chat-header {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.dark .chat-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.chat-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.dark .chat-header h3 {
  color: #f9fafb;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  animation: fadeIn 0.3s ease-out;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  position: relative;
}

.message.user .message-content {
  background: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
  margin-right: 1rem;
}

.message.assistant .message-content {
  background: #f3f4f6;
  color: #1f2937;
  border-bottom-left-radius: 4px;
}

.dark .message.assistant .message-content {
  background: #374151;
  color: #f9fafb;
}

.message-content p {
  margin: 0;
  line-height: 1.5;
}

.timestamp {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
  display: block;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #6b7280;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

.input-container {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.dark .input-container {
  border-top-color: rgba(255, 255, 255, 0.1);
}

.input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 20px;
  outline: none;
  transition: all 0.2s ease;
  background: white;
  color: #1f2937;
}

.message-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dark .message-input {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}

.dark .message-input:focus {
  border-color: #3b82f6;
}

.send-button {
  background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
  color: #fff;
  border: none;
  border-radius: 18px;
  width: 54px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s, filter 0.18s;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.10);
  font-size: 1.15rem;
  outline: none;
  overflow: visible;
  padding:0
}

.send-button:hover:not(:disabled), .send-button:focus-visible:not(:disabled) {
  filter: brightness(1.15);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.18);
  transform: scale(1.08);
}

.send-button:active:not(:disabled) {
  filter: brightness(0.95);
  transform: scale(0.98);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.3);
  box-shadow: none;
  transform: none;
}

.dark .send-button {
  background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%);
  color: #f9fafb;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.13);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

.send-icon {
  width: 28px;
  height: 18px;
  display: block;
  margin: 0 auto;
}

/* Markdown Content Styles */
.message.assistant .message-content :deep(h1),
.message.assistant .message-content :deep(h2),
.message.assistant .message-content :deep(h3),
.message.assistant .message-content :deep(h4),
.message.assistant .message-content :deep(h5),
.message.assistant .message-content :deep(h6) {
  margin: 0.5rem 0 0.25rem 0;
  font-weight: 600;
  line-height: 1.3;
}

.message.assistant .message-content :deep(h1) { font-size: 1.5rem; }
.message.assistant .message-content :deep(h2) { font-size: 1.25rem; }
.message.assistant .message-content :deep(h3) { font-size: 1.125rem; }
.message.assistant .message-content :deep(h4) { font-size: 1rem; }

.message.assistant .message-content :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.6;
}

.message.assistant .message-content :deep(ul),
.message.assistant .message-content :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.message.assistant .message-content :deep(li) {
  margin: 0.25rem 0;
  line-height: 1.5;
}

.message.assistant .message-content :deep(blockquote) {
  margin: 0.5rem 0;
  padding: 0.5rem 1rem;
  border-left: 3px solid #3b82f6;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 0 4px 4px 0;
}

.dark .message.assistant .message-content :deep(blockquote) {
  background: rgba(59, 130, 246, 0.1);
}

.message.assistant .message-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 0.125rem 0.25rem;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
}

.dark .message.assistant .message-content :deep(code) {
  background: rgba(255, 255, 255, 0.1);
}

.message.assistant .message-content :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  padding: 0.75rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0.5rem 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.dark .message.assistant .message-content :deep(pre) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.message.assistant .message-content :deep(pre code) {
  background: none;
  padding: 0;
}

.message.assistant .message-content :deep(a) {
  color: #3b82f6;
  text-decoration: none;
}

.message.assistant .message-content :deep(a:hover) {
  text-decoration: underline;
}

.message.assistant .message-content :deep(strong) {
  font-weight: 600;
}

.message.assistant .message-content :deep(em) {
  font-style: italic;
}

.message.assistant .message-content :deep(hr) {
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  margin: 1rem 0;
}

.dark .message.assistant .message-content :deep(hr) {
  border-top-color: rgba(255, 255, 255, 0.1);
}

/* Source link styling for converted results */
.message.assistant .message-content :deep(.source-link) {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
  display: block;
}

.dark .message.assistant .message-content :deep(.source-link) {
  color: #9ca3af;
}
</style>