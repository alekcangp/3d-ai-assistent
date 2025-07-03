<template>
  <div id="app" :class="{ 'dark': isDarkMode }">
    <Header 
      :isDarkMode="isDarkMode" 
      :selectedLang="selectedLang"
      :selectedMcpServer="selectedMcpServer"
      @updateLang="(lang) => selectedLang = lang"
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
          <ChatInterface
            :messages="messages"
            :isProcessing="isProcessing"
            @sendMessage="handleMessage"
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
import { ref, onMounted, watch } from 'vue'
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

const avatarConfig = ref<AvatarConfig>({ ...defaultAvatarConfig })

let personalityConfig = ref<PersonalityConfig>({
  name: "Elandria the Arcane Scholar",
  age: 164,
  role: "an ancient elven mage",
  style: "formal and slightly archaic",
  bio: "Once studied at the Grand Academy of Runic Arts",
  emotional_stability: 0.85,
  friendliness: 0.45,
  creativity: 0.68,
  curiosity: 0.95,
  formality: 0.1,
  empathy: 0.57,
  humor: 0.99,
  domain_knowledge: ["arcane magic", "elven history", "ancient runes"],
  quirks: "often references centuries-old events casually",
  lore: "Elves in this world can live up to 300 years",
  personality: "calm, wise, but sometimes condescending",
  conversation_style: "uses 'thee' and 'thou' occasionally",
  description: "Tall, silver-haired, wearing intricate robes with arcane symbols",
  lang: 'en'
})

const messages = ref<Message[]>([])

// Composables
const { saveToStorage, loadFromStorage } = useLocalStorage()
const { initializeAI } = useAI()
const { startListening, stopListening, speak, stopSpeaking } = useSpeech()

// Add at the top of the script setup
const API_URL = import.meta.env.VITE_API_URL || 'https://threed-ai-assistent.onrender.com'

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
  // Prepare last 5 messages as history (excluding system messages)
  const history = messages.value
    .filter(m => m.role && typeof m.content === 'string')
    .map(m => ({ role: m.role, content: m.content }))
    .slice(-5)
  // Always use the selected language from personalityConfig.lang
  let langToSend = personalityConfig.value.lang
  if (!langToSend || langToSend === 'system') langToSend = navigator.language
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      traits: { ...personalityConfig.value, lang: langToSend },
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
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: aiResponse,
      role: 'assistant',
      timestamp: new Date()
    }
    messages.value.push(aiMessage)
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
  } catch (error) {
    console.error('Error processing message:', error)
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: 'Sorry, I encountered an error processing your request.',
      role: 'assistant',
      timestamp: new Date()
    }
    messages.value.push(errorMessage)
  } finally {
    isProcessing.value = false
    saveToStorage('messages', messages.value)
  }
}

const startVoiceInput = () => {
  isListening.value = true
  if (avatarCanvas.value) {
    avatarCanvas.value.playAnimation('listening')
  }
  startListening(
    (transcript: string) => {
    if (transcript) {
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
  // Load saved settings
  const savedTheme = await loadFromStorage('theme', 'light')
  isDarkMode.value = savedTheme === 'dark'
  
  const savedAvatarConfig = await loadFromStorage('avatarConfig', defaultAvatarConfig)
  avatarConfig.value = { ...defaultAvatarConfig, ...(savedAvatarConfig || {}) }
  
  const savedPersonalityConfig = await loadFromStorage('personalityConfig', personalityConfig.value)
  // Remove any lingering 'lang' and 'model' property
  if (savedPersonalityConfig && 'lang' in savedPersonalityConfig) {
    delete savedPersonalityConfig.lang
  }
  if (savedPersonalityConfig && 'model' in savedPersonalityConfig) {
    delete savedPersonalityConfig.model
  }
  personalityConfig.value = { ...personalityConfig.value, ...(savedPersonalityConfig || {}) }
  
  const savedMessages = await loadFromStorage('messages', [])
  messages.value = savedMessages || []

  // Load saved MCP server
  let savedMcpServer = await loadFromStorage('mcpServer', null)
  if (savedMcpServer === undefined || savedMcpServer === '') savedMcpServer = null
  selectedMcpServer.value = savedMcpServer

  // Load selectedLang
  const lang = await loadFromStorage('selectedLang')
  if (lang) {
    selectedLang.value = lang
    personalityConfig.value.lang = lang
  } else {
    selectedLang.value = 'system'
    personalityConfig.value.lang = 'system'
  }

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
    console.error('Failed to initialize AI:', error)
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
    // Force CustomizationPanel to use the current selected MCP server
    // (relies on v-if recreating the component)
    // No-op here, but ensures the prop is up to date
    // If you want to be extra sure, you could emit an event or use a key binding
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
  let lang = personalityConfig.value.lang
  if (!lang || lang === 'system') lang = navigator.language
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
</script>

<style scoped>
.main-content {
  min-height: calc(100vh - 80px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: all 0.3s ease;
}

.dark .main-content {
  background: linear-gradient(135deg, #2D3748 0%, #1A202C 100%);
}

.app-container {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  min-height: calc(100vh - 80px);
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
  }
}
</style>