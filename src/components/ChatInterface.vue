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
              <div v-html="marked(cleanMarkdown(typeof message.content === 'string' ? message.content : String(message.content)))"></div>
            </template>
            <template v-else>
              <div class="user-message-wrapper">
                <p>{{ message.content }}</p>
                <button 
                  @click="copyMessage(message.content)"
                  class="copy-button"
                  :title="copyStatus === message.id ? 'Скопировано!' : 'Копировать сообщение'"
                >
                  <svg v-if="copyStatus !== message.id" viewBox="0 0 24 24" fill="currentColor" class="copy-icon">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="currentColor" class="copy-icon">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                  </svg>
                </button>
              </div>
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
        <button 
          class="fix-layout-btn"
          :disabled="isProcessing || !inputText.trim() || isFixingLayout"
          @click="fixLayout"
          title="Fix keyboard layout"
        >
          <span v-if="!isFixingLayout" style="font-size: 1.25em; line-height: 1;">⇄</span>
          <span v-else style="font-size: 0.9em;">...</span>
        </button>
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
          <svg viewBox="0 0 26 32" fill="currentColor" class="send-icon">
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
  gfm: true     // GitHub Flavored Markdown
})

// Определяем API_URL для запросов к backend
const API_URL = (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '')

const props = defineProps<{
  messages: Message[]
  isProcessing: boolean
  isSpeaking: boolean
  lang?: string
}>()

const emit = defineEmits<{
  sendMessage: [content: string]
  userTyping: []
}>()

const inputText = ref('')
const messagesContainer = ref<HTMLElement>()
const hasTyped = ref(false)
const copyStatus = ref<string | null>(null)
const isFixingLayout = ref(false)

const scrollToLatest = () => {
  nextTick(() => {
    if (!messagesContainer.value) return
    const messageEls = messagesContainer.value.querySelectorAll('.message')
    if (messageEls.length === 0) return
    const lastMessageEl = messageEls[messageEls.length - 1] as HTMLElement
    // Scroll the last message into view at the top of the container
    lastMessageEl.scrollIntoView({ block: 'start', behavior: 'smooth' })
    // Optionally, also scroll inner content to top
    const contentEl = lastMessageEl.querySelector('.message-content')
    if (contentEl) contentEl.scrollTop = 0
    const preEls = lastMessageEl.querySelectorAll('pre')
    preEls.forEach(pre => { pre.scrollTop = 0 })
  })
}

const sendMessage = () => {
  if (!inputText.value.trim() || props.isProcessing) return
  emit('sendMessage', inputText.value.trim())
  inputText.value = ''
  hasTyped.value = false // Reset typing flag when message is sent
  scrollToLatest() // Focus on the new user message
}

const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    copyStatus.value = content
    setTimeout(() => {
      copyStatus.value = null
    }, 2000)
  } catch (err) {
    console.error('Failed to copy message:', err)
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = content
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    copyStatus.value = content
    setTimeout(() => {
      copyStatus.value = null
    }, 2000)
  }
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

async function fixLayout() {
  if (!inputText.value.trim() || isFixingLayout.value) return
  isFixingLayout.value = true
  try {
    let lang = props.lang
    if (!lang || lang === 'system') {
      lang = navigator.language.split('-')[0] // e.g., 'en-US' -> 'en'
    }
    const res = await fetch(`${API_URL}/fix-layout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: inputText.value, lang })
    })
    const data = await res.json()
    if (data && typeof data.fixed_text === 'string') {
      inputText.value = data.fixed_text
    }
  } catch (e) {
    console.error('Failed to fix layout:', e)
  } finally {
    isFixingLayout.value = false
  }
}

// Watch for new messages and scroll to latest
watch(() => props.messages.length, scrollToLatest)

// Функция для очистки табуляций и лишних отступов
function cleanMarkdown(text: string): string {
  // 1. Заменить все \t, \n, \r на соответствующие символы
  let cleaned = text.replace(/\\t/g, '    ')
    .replace(/\\n/g, '\n')
    .replace(/\\r/g, '\r')
    .replace(/\t/g, '    ')

  // 2. Удалить ведущие 4+ пробела вне code block
  let inCodeBlock = false
  cleaned = cleaned.split('\n').map(line => {
    if (line.trim().startsWith('```')) inCodeBlock = !inCodeBlock
    if (!inCodeBlock) return line.replace(/^ {4,}/, '')
    return line
  }).join('\n')

  return cleaned
}
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 238px);
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
  word-break: break-word;
  overflow-x: auto;
  overflow-wrap: anywhere;
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

.user-message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.user-message-wrapper p {
  margin: 0;
  line-height: 1.5;
  flex: 1;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.copy-button {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
}

.copy-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.copy-icon {
  width: 16px;
  height: 16px;
}

.message-content p {
  margin: 0;
  line-height: 1.5;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.message-content code {
  max-width: 100%;
  overflow-x: auto;
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  box-sizing: border-box;
}

.message-content pre {
  background: #23272e;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 0.75em 1em;
  font-size: 0.95em;
  margin: 0.5em 0;
  max-width: 100%;
  overflow-x: auto;
  word-break: break-word;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
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
  border-radius: 12px;
  font-size: 0.875rem;
  background: white;
  transition: border-color 0.2s ease;
  outline: none;
}

.dark .message-input {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}

.message-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dark .message-input:focus {
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.message-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  height: 44px;
}

.send-button:hover:not(:disabled) {
  background: #2563eb;
  transform: scale(1.05);
}

.send-button:active:not(:disabled) {
  transform: scale(0.95);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.send-icon {
  width: 20px;
  height: 20px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.fix-layout-btn {
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  border: none;
  border-radius: 14px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  margin-left: 0;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s, color 0.18s;
  box-shadow: 0 1px 4px rgba(100, 116, 139, 0.08);
  outline: none;
  font-size: 0.8em;
  position: relative;
}
.dark .fix-layout-btn {
  background: linear-gradient(90deg, #374151 0%, #4b5563 100%);
  color: #f3f4f6;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.13);
}
.fix-layout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.3);
  box-shadow: none;
  transform: none;
}
.fix-layout-btn:hover:not(:disabled), .fix-layout-btn:focus-visible:not(:disabled) {
  background: linear-gradient(90deg, #e5e7eb 0%, #d1d5db 100%);
  color: #111827;
  box-shadow: 0 4px 16px rgba(100, 116, 139, 0.13);
  transform: scale(1.08);
}
.dark .fix-layout-btn:hover:not(:disabled), .dark .fix-layout-btn:focus-visible:not(:disabled) {
  background: linear-gradient(90deg, #4b5563 0%, #6b7280 100%);
  color: #fff;
}
.fix-layout-btn span {
  font-size: 0.9em;
  line-height: 1;
}
</style>