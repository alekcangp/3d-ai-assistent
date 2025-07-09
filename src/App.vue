<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <Header 
      :isDarkMode="isDarkMode" 
      :selectedLang="selectedLang"
      :selectedMcpServer="selectedMcpServer"
      :personalityConfig="personalityConfig"
      @updateLang="onUpdateLang"
      @toggleTheme="toggleTheme"
      @toggleCustomization="toggleCustomization"
    />
    
    <main class="main-content">
      <div class="app-container">
        <!-- 3D Avatar Section -->
        <div class="avatar-section">
          <AvatarCanvas 
            ref="avatarCanvas"
            :avatarConfig="avatarConfig"
            :isListening="isListening"
            :isSpeaking="isSpeaking"
            :mouthOpenLevel="mouthOpenLevel"
            :isDarkMode="isDarkMode"
          />
          
          <!-- Voice Control -->
          <VoiceControls
            :isListening="isListening"
            :isProcessing="isProcessing"
            :isSpeaking="isSpeaking"
            @startListening="startVoiceInput"
            @stopListening="stopVoiceInput"
            @stopSpeaking="handleStopSpeaking"
          />
        </div>

        <!-- Chat Interface -->
        <div class="chat-section">
          <div class="chat-header-row">
            <button class="reset-chat-btn" @click="resetChat" title="Clear all chat history" type="button">
              <svg viewBox="0 0 24 24" fill="currentColor" class="reset-icon">
                <path d="M9 3a3 3 0 0 1 6 0h5a1 1 0 1 1 0 2h-1.1l-.86 14.02A3 3 0 0 1 15.05 22h-6.1a3 3 0 0 1-2.99-2.98L5.1 5H4a1 1 0 1 1 0-2h5zm2 0a1 1 0 1 1 2 0h-2zm-3.9 2l.85 13.98A1 1 0 0 0 8.95 20h6.1a1 1 0 0 0 .99-.98L16.9 5H7.1z"/>
              </svg>
              Reset Chat
            </button>
          </div>
          <ChatInterface
            :messages="messages"
            :isProcessing="isProcessing"
            :isSpeaking="isSpeaking"
            :lang="selectedLang"
            @sendMessage="handleMessage"
            @userTyping="handleStopSpeaking"
          />
        </div>
      </div>

      <!-- Customization Panel -->
      <CustomizationPanel
        v-if="showCustomization"
        :avatarConfig="avatarConfig"
        :personalityConfig="personalityConfig"
        :selectedLang="selectedLang"
        :selectedMcpServer="selectedMcpServer"
        :selectedModel="selectedModel"
        :userMcpServers="userMcpServers"
        :allMcpServers="allMcpServers"
        @updateAvatar="updateAvatarConfig"
        @updatePersonality="updatePersonalityConfig"
        @close="toggleCustomization"
        @updateMcpServer="onUpdateMcpServer"
        @updateLang="onUpdateLang"
        @updateModel="onUpdateModel"
      />
    </main>

    <!-- Loading Screen -->
    <LoadingScreen v-if="isLoading" :progress="loadingProgress" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import Header from './components/Header.vue'
import AvatarCanvas from './components/AvatarCanvas.vue'
import ChatInterface from './components/ChatInterface.vue'
import CustomizationPanel from './components/CustomizationPanel.vue'
import VoiceControls from './components/VoiceControls.vue'
import LoadingScreen from './components/LoadingScreen.vue'
import { useLocalStorage } from './composables/useLocalStorage'
import { useAI } from './composables/useAI'
import { useSpeech, speechAmplitude } from './composables/useSpeech'
import type { AvatarConfig, PersonalityConfig, Message } from './types'
import gsap from 'gsap'
import { getDefaultMcpServers } from './constants/mcpServers'

// Reactive state
const isDarkMode = ref(false)
const showCustomization = ref(false)
const isLoading = ref(true)
const loadingProgress = ref(0)
const isListening = ref(false)
const isSpeaking = ref(false)
const isProcessing = ref(false)
const mouthOpenLevel = ref(0)
let mouthTween: gsap.core.Tween | null = null
const selectedLang = ref('system')
const selectedMcpServer = ref<string | null>(null)
const selectedModel = ref('')
const resetGenerationId = ref(0)

// Refs
const avatarCanvas = ref()

// Configurations
const defaultAvatarConfig: AvatarConfig = {
  model: 'default',
  gender: 'neutral',
  outfit: 'casual',
  hairColor: '#000000',
  skinTone: '#f5e0c0',
  eyeColor: '#333333',
}

const professionalPersonality: PersonalityConfig = {
  name: 'Professional AI',
  age: 35,
  role: 'Advisor',
  style: 'Formal',
  bio: 'An expert in business and productivity.',
  emotional_stability: 0.9,
  friendliness: 0.7,
  creativity: 0.6,
  curiosity: 0.7,
  formality: 0.9,
  empathy: 0.6,
  humor: 0.3,
  domain_knowledge: ['business', 'productivity'],
  quirks: 'Always on time',
  lore: 'Trained by top consultants.',
  personality: 'Efficient and direct',
  conversation_style: 'Formal',
  description: 'Focused on results.',
  lang: 'en'
}

const avatarConfig = ref<AvatarConfig>({ ...defaultAvatarConfig })
let personalityConfig = ref<PersonalityConfig>({ ...professionalPersonality })

const messages = ref<Message[]>([])

// Composables
const { saveToStorage, loadFromStorage, saveMessages, loadMessages } = useLocalStorage()
const { initializeAI } = useAI()
const { startListening, stopListening, speak, stopSpeaking } = useSpeech()

// Add at the top of the script setup
const API_URL = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000").replace(/\/$/, '')

// User MCP servers state
const userMcpServers = ref<{ name: string, value: string, description?: string }[]>([])
const allMcpServers = computed(() => [
  ...getDefaultMcpServers(),
  ...userMcpServers.value
])

// Methods
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  saveToStorage('theme', isDarkMode.value ? 'dark' : 'light')
}

const toggleCustomization = () => {
  showCustomization.value = !showCustomization.value
}

const updateAvatarConfig = (newConfig: Partial<AvatarConfig>) => {
  avatarConfig.value = { ...avatarConfig.value, ...newConfig }
  saveToStorage('avatarConfig', avatarConfig.value)
}

const updatePersonalityConfig = (newConfig: Partial<PersonalityConfig>) => {
  // Deep merge to ensure arrays/objects are updated
  personalityConfig.value = JSON.parse(JSON.stringify({ ...personalityConfig.value, ...newConfig }))
  saveToStorage('personalityConfig', personalityConfig.value)
}

async function sendToIOIntel(message: string) {
  // Prepare last 5 messages as history (only user questions and AI answers)
  const history = messages.value
    .filter(m => m.role === 'user' || m.role === 'assistant')
    .filter(m => typeof m.content === 'string' && m.content.trim() !== '')
    .map(m => ({ role: m.role, content: m.content }))
    .slice(-5) // Keep last 5 messages for better context
  
  // Use selectedLang.value as primary source, personalityConfig.value.lang as fallback
  let langToSend = selectedLang.value || personalityConfig.value.lang
  
  if (!langToSend || langToSend === 'system') {
    langToSend = navigator.language
  }
  
  if (langToSend.includes('-')) langToSend = langToSend.split('-')[0] // Normalize to 'ru', 'en', etc.
  
  // Exclude 'lang' from traits
  const { lang, ...traitsWithoutLang } = personalityConfig.value
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      traits: traitsWithoutLang,
      history,
      model: selectedModel.value,
      mcpServer: selectedMcpServer.value,
      lang: langToSend
    })
  });
  const data = await res.json();
  return data.response;
}

const handleMessage = async (content: string) => {
  if (!content || !content.trim()) {
    // Do not process empty messages (e.g., user stopped speaking)
    return;
  }
  const myGenId = resetGenerationId.value;
  const userMessage: Message = {
    id: Date.now().toString(),
    content,
    role: 'user',
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  isProcessing.value = true

  try {
    // Use IOIntel backend for persona-driven response
    const aiResponse = await sendToIOIntel(content);
    if (resetGenerationId.value !== myGenId) {
      isProcessing.value = false;
      return; // Chat was reset during processing, ignore this response
    }
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: aiResponse,
      role: 'assistant',
      timestamp: new Date()
    }
    messages.value.push(aiMessage)
    // Set processing to false after receiving response, before speaking
    isProcessing.value = false
    // Animate avatar and speak response as before
    if (avatarCanvas.value) {
      avatarCanvas.value.playAnimation('speaking')
    }
    isSpeaking.value = true
    await speak(aiResponse, () => {
      if (mouthTween) mouthTween.kill()
      mouthTween = gsap.to(mouthOpenLevel, {
        duration: 0.08,
        value: 0.5,
        overwrite: true,
        onComplete: () => {
          mouthTween = gsap.to(mouthOpenLevel, {
            duration: 0.18,
            value: 0,
            overwrite: true
          })
        }
      })
    }, getCurrentLang())
    if (mouthTween) mouthTween.kill()
    mouthTween = gsap.to(mouthOpenLevel, { value: 0, duration: 0.15 })
    isSpeaking.value = false
    if (avatarCanvas.value) {
      avatarCanvas.value.playAnimation('idle')
    }
  } catch (error: any) {
    // Ignore speech synthesis errors
    if (
      (typeof window !== 'undefined' && typeof window.SpeechSynthesisErrorEvent !== 'undefined' && error instanceof window.SpeechSynthesisErrorEvent) ||
      (error && error.error === 'interrupted')
    ) {
      // Do not show error message in chat
      return;
    }
    // Only show error if not user cancellation or AbortError
    if (!(error && (error.name === 'AbortError' || error.message === 'cancelled' || error.message === 'canceled'))) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'I encountered an error processing your request.',
        role: 'assistant',
        timestamp: new Date()
      }
      messages.value.push(errorMessage)
    }
  } finally {
    // Save only user and assistant messages, filter out system messages and empty content
    const messagesToSave = messages.value.filter(m => 
      (m.role === 'user' || m.role === 'assistant') && 
      typeof m.content === 'string' && 
      m.content.trim() !== ''
    )
    saveMessages(messagesToSave)
  }
}

const startVoiceInput = () => {
  isListening.value = true
  if (avatarCanvas.value) {
    avatarCanvas.value.playAnimation('listening')
  }
  startListening(
    (transcript: string) => {
      if (transcript && transcript.trim()) {
        handleMessage(transcript)
      }
      stopVoiceInput()
    },
    getCurrentLang(),
    () => {
      isListening.value = false
      if (avatarCanvas.value) {
        avatarCanvas.value.playAnimation('idle')
      }
    }
  )
}

const stopVoiceInput = () => {
  isListening.value = false
  stopListening()
  if (avatarCanvas.value) {
    avatarCanvas.value.playAnimation('idle')
  }
}

// Save MCP server selection to storage when changed
watch(selectedMcpServer, (newVal) => {
  saveToStorage('mcpServer', newVal)
})

// Add a flag to track if this is the first load
let isFirstLoad = true

// Initialize app
onMounted(async () => {
  // Load saved theme, default to dark
  const savedTheme = await loadFromStorage('theme', 'dark')
  isDarkMode.value = savedTheme === 'dark'
  
  const savedAvatarConfig = await loadFromStorage('avatarConfig', defaultAvatarConfig)
  avatarConfig.value = { ...defaultAvatarConfig, ...(savedAvatarConfig || {}) }
  
  const savedPersonalityConfig = await loadFromStorage('personalityConfig', null)
  if (savedPersonalityConfig) {
    // Remove any lingering 'lang' and 'model' property
    if ('lang' in savedPersonalityConfig) {
      delete savedPersonalityConfig.lang
    }
    if ('model' in savedPersonalityConfig) {
      delete savedPersonalityConfig.model
    }
    personalityConfig.value = { ...professionalPersonality, ...savedPersonalityConfig }
  } else {
    personalityConfig.value = { ...professionalPersonality }
  }
  
  const savedMessages = await loadMessages()
  // Filter loaded messages to ensure only user and assistant messages are loaded
  messages.value = (savedMessages || []).filter((m: Message) => 
    (m.role === 'user' || m.role === 'assistant') && 
    typeof m.content === 'string' && 
    m.content.trim() !== ''
  )

  // Load user MCP servers
  const savedUserMcp = await loadFromStorage('userMcpServers', [])
  if (Array.isArray(savedUserMcp)) userMcpServers.value = savedUserMcp

  // Load saved MCP server
  let savedMcpServer = await loadFromStorage('mcpServer', null)
  if (savedMcpServer === undefined || savedMcpServer === '') savedMcpServer = null
  // If no saved MCP server, default to Fetch
  if (!savedMcpServer) {
    const fetchServer = getDefaultMcpServers().find(s => s.value === 'https://remote.mcpservers.org/fetch/mcp')
    savedMcpServer = fetchServer ? fetchServer.value : null
  }
  selectedMcpServer.value = savedMcpServer

  // Load selectedLang and set it in personalityConfig
  const lang = await loadFromStorage('selectedLang')
  if (lang) {
    selectedLang.value = lang
    personalityConfig.value.lang = lang
  } else {
    selectedLang.value = 'system'
    personalityConfig.value.lang = 'system'
  }
  
  // Save the updated personalityConfig with the correct lang
  saveToStorage('personalityConfig', personalityConfig.value)

  // Fetch models and set default to second model if first load
  try {
    loadingProgress.value = 10
    const res = await fetch(`${API_URL}/models`)
    const data = await res.json()
    const models = data.models || []
    if (isFirstLoad && models.length > 1) {
      // Set professional preset and second model
      personalityConfig.value = {
        name: 'Professional AI',
        age: 35,
        role: 'Advisor',
        style: 'Formal',
        bio: 'An expert in business and productivity.',
        emotional_stability: 0.9,
        friendliness: 0.7,
        creativity: 0.6,
        curiosity: 0.7,
        formality: 0.9,
        empathy: 0.6,
        humor: 0.3,
        domain_knowledge: ['business', 'productivity'],
        quirks: 'Always on time',
        lore: 'Trained by top consultants.',
        personality: 'Efficient and direct',
        conversation_style: 'Formal',
        description: 'Focused on results.'
      }
      saveToStorage('personalityConfig', personalityConfig.value)
      isFirstLoad = false
    }
    loadingProgress.value = 20
    await initializeAI()
    loadingProgress.value = 100
    setTimeout(() => {
      isLoading.value = false
    }, 500)

    // On load, after fetching models, set selectedModel to models[1].id (or saved value)
    const savedModel = await loadFromStorage('selectedModel', '')
    if (models.length > 1) {
      selectedModel.value = savedModel || models[1].id
    } else if (models.length > 0) {
      selectedModel.value = savedModel || models[0].id
    }
    saveToStorage('selectedModel', selectedModel.value)
  } catch (error) {
    isLoading.value = false
  }
})

// Watch for theme changes
watch(isDarkMode, (newValue) => {
  document.documentElement.setAttribute('data-theme', newValue ? 'dark' : 'light')
})

watch([isSpeaking, speechAmplitude], ([speaking, amplitude]) => {
  if (speaking) {
    // Simulate syllabic mouth closure: fast sine wave (5-7 Hz) + amplitude + noise
    const now = performance.now() / 1000;
    const syllable = 0.5 + 0.5 * Math.abs(Math.sin(now * 6.5)); // 0..1, 6.5 Hz
    const noise = 0.08 * (Math.random() - 0.5); // small random jitter
    // Amplitude is scaled, but not always fully open
    mouthOpenLevel.value = Math.max(0, Math.min(1, amplitude * 1.2 * syllable + noise));
  } else {
    mouthOpenLevel.value = 0;
  }
})

// When opening settings, sync selected MCP server to panel
watch(showCustomization, (open) => {
  if (open) {
    // No-op, but ensures prop is up to date
  }
})

function onUpdateMcpServer(server: string | null) {
  selectedMcpServer.value = server || null
  saveToStorage('mcpServer', selectedMcpServer.value)
}

function onUpdateLang(lang: string) {
  selectedLang.value = lang
  personalityConfig.value.lang = lang
  saveToStorage('selectedLang', lang)
  saveToStorage('personalityConfig', personalityConfig.value)
}

function getCurrentLang() {
  // Use selectedLang.value as primary source
  let lang = selectedLang.value
  
  if (!lang || lang === 'system') {
    lang = navigator.language
  }
  
  // Convert language codes for STT/TTS
  if (lang === 'ru') {
    lang = 'ru-RU'
  } else if (lang === 'en') {
    lang = 'en-US'
  }
  
  return lang
}

function handleStopSpeaking() {
  stopSpeaking();
  isSpeaking.value = false;
  if (avatarCanvas.value) {
    avatarCanvas.value.playAnimation('idle');
  }
}

function onUpdateModel(model: string) {
  selectedModel.value = model
  saveToStorage('selectedModel', model)
}

const resetChat = () => {
  messages.value = [];
  saveMessages([]);
  // Also clear from settings store for backward compatibility
  saveToStorage('messages', []);
  isProcessing.value = false;
  isSpeaking.value = false;
  stopSpeaking();
  resetGenerationId.value++;
}
</script>

<style scoped>
:global(html), :global(body), :global(#app) {
  height: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  overflow-x: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.dark :global(body), .dark :global(#app) {
  background: linear-gradient(135deg, #2D3748 0%, #1A202C 100%);
}

.main-content {
  min-height: calc(100vh - 80px);
  transition: all 0.3s ease;
  width: 100%;
  min-width: 0;
}

.app-container {
  display: grid;
  grid-template-columns: 1fr minmax(0, 950px);
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 80px);
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.chat-section {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .chat-section {
  background: rgba(45, 55, 72, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-header-row {
  display: flex;
  align-items: ceenter;
  justify-content: flex-end;
  min-height: 24px;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0rem 0rem 1rem 0rem
}

.dark .chat-header-row {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.reset-chat-btn {
  background: linear-gradient(90deg, #f3f4f6 0%, #e5e7eb 100%);
  color: #374151;
  border: none;
  border-radius: 14px;
  padding: 0.22rem 0.7rem 0.22rem 0.6rem;
  font-size: 0.92rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s, box-shadow 0.18s, transform 0.18s, filter 0.18s, color 0.18s;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  box-shadow: 0 1px 4px rgba(100, 116, 139, 0.08);
  outline: none;
}

.reset-icon {
  width: 19px;
  height: 19px;
  display: block;
  color: #6b7280;
  transition: color 0.18s;
}

.reset-chat-btn:hover:not(:disabled), .reset-chat-btn:focus-visible:not(:disabled) {
  background: linear-gradient(90deg, #e5e7eb 0%, #d1d5db 100%);
  color: #111827;
  box-shadow: 0 4px 16px rgba(100, 116, 139, 0.13);
  transform: scale(1.08);
}

.reset-chat-btn:hover .reset-icon, .reset-chat-btn:focus-visible .reset-icon {
  color: #374151;
}

.reset-chat-btn:active:not(:disabled) {
  filter: brightness(0.97);
  transform: scale(0.98);
}

.reset-chat-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.3);
  box-shadow: none;
  transform: none;
}

.dark .reset-chat-btn {
  background: linear-gradient(90deg, #374151 0%, #4b5563 100%);
  color: #f3f4f6;
  box-shadow: 0 2px 8px rgba(100, 116, 139, 0.13);
}

.dark .reset-icon {
  color: #d1d5db;
}

@media (max-width: 1024px) {
  .app-container {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  .chat-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .app-container {
    padding: 1rem;
    gap: 1rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    min-width: 0;
  }
  .chat-section, .avatar-section {
    width: 100%;
    min-width: 0;
    margin: 0 auto;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    flex-shrink: 1;
  }
  .chat-section {
    overflow-x: hidden;
    max-width: 100%;
    width: 100%;
    box-sizing: border-box;
    padding-left: 10px;
    padding-right: 10px;
    min-width: 0;
    flex-shrink: 1;
  }
  .chat-section * {
    box-sizing: border-box;
    word-break: break-word;
    overflow-wrap: anywhere;
    min-width: 0;
    flex-shrink: 1;
  }
  .chat-section .message, .chat-section .assistant-message {
    margin-left: 4px;
    margin-right: 4px;
    padding-left: 8px;
    padding-right: 8px;
    width: 100%;
    min-width: 0;
    flex-shrink: 1;
  }
  .chat-section button {
    margin-left: 2px;
    margin-right: 2px;
    padding-left: 8px;
    padding-right: 8px;
    width: 100%;
    min-width: 0;
    flex-shrink: 1;
  }
}
</style>