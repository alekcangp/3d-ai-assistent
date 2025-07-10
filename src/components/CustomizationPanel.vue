<template>
  <div class="customization-overlay" @click="onOverlayClick">
    <div class="customization-panel" ref="panelRef">
      <div class="panel-header">
        <h2>Customize Your Assistant</h2>
        <button class="close-button" @click="$emit('close')">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z" />
          </svg>
        </button>
      </div>

      <div class="panel-content">
        <div class="customization-section">
          <h3>AI Model</h3>
          <div class="control-group">
            <label for="model-select">Model</label>
            <select id="model-select" :value="selectedModel" @change="e => emit('updateModel', (e.target as HTMLSelectElement)?.value)" :disabled="modelLoading">
              <option v-for="model in modelList" :key="model.id" :value="model.id">
                {{ model.name }}
              </option>
            </select>
            <div v-if="modelLoading" class="model-loading">Loading models...</div>
            <div v-if="modelError" class="model-error">{{ modelError }}</div>
            <div v-if="selectedModel">
              <div class="mcp-description">{{ modelList.find(m => m.id === selectedModel)?.description }}</div>
            </div>
          </div>
        </div>

        <div class="customization-section">
          <div class="mcp-header-with-info">
            <h3 style="margin: 0;">MCP Server</h3>
            <button class="mcp-info-btn" @click="showMcpInfo = !showMcpInfo" aria-label="What is MCP?" type="button" tabindex="0">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <circle cx="10" cy="10" r="9" stroke="#6b7280" stroke-width="2" fill="#fff"/>
                <path d="M10 7.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-1 2.25c0-.414.336-.75.75-.75h.5c.414 0 .75.336.75.75v4c0 .414-.336.75-.75.75h-.5a.75.75 0 0 1-.75-.75v-4z" fill="#6b7280"/>
              </svg>
            </button>
            <button class="mcp-tools-btn" @click="toggleToolsTooltip" title="View Available Tools" type="button">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/>
              </svg>
            </button>
            <transition name="fade">
              <div v-if="showMcpInfo" class="mcp-info-tooltip" role="tooltip">
                The Model Context Protocol (MCP) is an open standard that enables AI assistants to securely connect to external data sources and tools.
              </div>
            </transition>
            <transition name="fade">
              <div v-if="showToolsTooltip" class="mcp-tools-tooltip" role="tooltip">
                <div v-if="loading" class="loading"><div class="spinner"></div>Loading tools...</div>
                <div v-else-if="error" class="error">{{ error }}</div>
                <div v-else v-html="toolsHtml"></div>
              </div>
            </transition>
          </div>
          <div class="control-group">
            <label for="mcp-select">MCP Server</label>
            <select id="mcp-select" v-model="selectedMcp" @change="updateMcpServer">
              <option v-for="server in allMcpServers" :key="server.value || server.name" :value="server.value">{{ server.name }}</option>
            </select>
            <div v-if="selectedMcpObj" class="mcp-description">{{ selectedMcpObj.description }}</div>
          </div>
          <div class="add-mcp-server-form">
            <input v-model="newMcpUrl" type="text" placeholder="Add MCP server URL" />
            <input v-model="newMcpDesc" type="text" placeholder="Name (optional)" />
            <button @click="addUserMcpServer" type="button">Add</button>
            <span v-if="addError" class="add-mcp-error">{{ addError }}</span>
          </div>
          <ul class="user-mcp-list">
            <li v-for="server in userMcpServers" :key="server.value">
              <span>{{ server.name }}</span>
              <button @mousedown.stop @click.stop="removeUserMcpServer(server.value)" type="button" class="remove-mcp-btn" title="Remove this server">
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                  <path d="M6 8v6a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V8" stroke="#fff" stroke-width="1.5"/>
                  <path d="M9 11v3m2-3v3M4 6h12m-1 0V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v1" stroke="#fff" stroke-width="1.5"/>
                </svg>
              </button>
            </li>
          </ul>
        </div>

        <div class="customization-section">
          <h3>Personality Traits</h3>

          <div class="control-group">
            <label for="lang-select">Language</label>
            <select id="lang-select" :value="localSelectedLang" @change="handleLangChange">
              <option value="system">System Default ({{ systemLangLabel }})</option>
              <option v-for="lang in LANGUAGES" :key="lang.code" :value="lang.code">{{ lang.label }}</option>
            </select>
          </div>
          <div class="control-group">
            <label>Name</label>
            <input v-model="localPersonalityConfig.name" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Age</label>
            <input v-model.number="localPersonalityConfig.age" @input="updatePersonality" type="number" min="0" />
          </div>
          <div class="control-group">
            <label>Role</label>
            <input v-model="localPersonalityConfig.role" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Style</label>
            <input v-model="localPersonalityConfig.style" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Bio</label>
            <input v-model="localPersonalityConfig.bio" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Domain Knowledge (comma separated)</label>
            <input v-model="domainKnowledgeInput" @change="updateDomainKnowledge" type="text" />
          </div>
          <div class="control-group">
            <label>Quirks</label>
            <input v-model="localPersonalityConfig.quirks" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Lore</label>
            <input v-model="localPersonalityConfig.lore" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Personality</label>
            <input v-model="localPersonalityConfig.personality" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Conversation Style</label>
            <input v-model="localPersonalityConfig.conversation_style" @input="updatePersonality" type="text" />
          </div>
          <div class="control-group">
            <label>Description</label>
            <input v-model="localPersonalityConfig.description" @input="updatePersonality" type="text" />
        </div>

          <div class="control-group">
            <label>Emotional Stability</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.emotional_stability"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.emotional_stability * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Friendliness</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.friendliness"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.friendliness * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Creativity</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.creativity"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.creativity * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Curiosity</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.curiosity"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.curiosity * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Formality</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.formality"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.formality * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Empathy</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.empathy"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.empathy * 100) }}%</span>
            </div>
          </div>

          <div class="control-group">
            <label>Humor</label>
            <div class="slider-container">
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.01"
                v-model="localPersonalityConfig.humor"
                @input="updatePersonality"
                class="trait-range"
              />
              <span class="trait-value">{{ Math.round(localPersonalityConfig.humor * 100) }}%</span>
            </div>
          </div>
        </div>

        <div class="customization-section">
          <h3>Personality Presets</h3>
          <div class="preset-buttons">
            <button @click="applyPreset('friendly')" class="preset-btn">
              😊 Friendly
            </button>
            <button @click="applyPreset('professional')" class="preset-btn">
              👔 Professional
            </button>
            <button @click="applyPreset('creative')" class="preset-btn">
              🎨 Creative
            </button>
            <button @click="applyPreset('analytical')" class="preset-btn">
              🧠 Analytical
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, onBeforeUnmount } from 'vue'
import type { AvatarConfig, PersonalityConfig } from '../types'
import { getDefaultMcpServers } from '../constants/mcpServers'
import { useLocalStorage } from '../composables/useLocalStorage'
import { marked } from 'marked'

const props = defineProps<{
  avatarConfig: AvatarConfig
  personalityConfig: PersonalityConfig
  selectedMcpServer: string | null
  selectedLang: string
  selectedModel: string
}>()

// Defensive runtime checks
if (!props.avatarConfig || typeof props.avatarConfig !== 'object') {
  throw new Error('avatarConfig prop is required and must be an object');
}
if (!props.personalityConfig || typeof props.personalityConfig !== 'object') {
  throw new Error('personalityConfig prop is required and must be an object');
}

const emit = defineEmits<{
  updateAvatar: [config: Partial<AvatarConfig>]
  updatePersonality: [config: Partial<PersonalityConfig>]
  updateMcpServer: [server: string | null]
  updateLang: [lang: string]
  updateModel: [model: string]
  close: []
}>()

// Local copies for real-time updates
const localAvatarConfig = ref<AvatarConfig>({ ...props.avatarConfig })
const localPersonalityConfig = ref<PersonalityConfig>({ ...props.personalityConfig })
if (!localPersonalityConfig.value.lang) {
  localPersonalityConfig.value.lang = 'system'
}

const domainKnowledgeInput = ref(localPersonalityConfig.value.domain_knowledge?.join(', ') || '')

const modelList = ref<{id: string, name: string, description: string}[]>([])
const modelLoading = ref(false)
const modelError = ref('')

const { saveToStorage, loadFromStorage } = useLocalStorage()
const userMcpServers = ref<{ name: string, value: string, description?: string }[]>([])

const panelRef = ref<HTMLElement | null>(null)

const showMcpInfo = ref(false)
const showToolsTooltip = ref(false)
const tools = ref('')
const loading = ref(false)
const error = ref('')

const localSelectedLang = ref(props.selectedLang)

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'zh', label: 'Chinese (中文)' },
  { code: 'hi', label: 'Hindi (हिन्दी)' },
  { code: 'es', label: 'Spanish (Español)' },
  { code: 'fr', label: 'French (Français)' },
  { code: 'ar', label: 'Arabic (العربية)' },
  { code: 'bn', label: 'Bengali (বাংলা)' },
  { code: 'pt', label: 'Portuguese (Português)' },
  { code: 'ru', label: 'Russian (Русский)' },
  { code: 'ja', label: 'Japanese (日本語)' },
  { code: 'de', label: 'German (Deutsch)' },
  { code: 'ur', label: 'Urdu (اردو)' },
  { code: 'tr', label: 'Turkish (Türkçe)' },
  { code: 'it', label: 'Italian (Italiano)' },
  { code: 'pl', label: 'Polish (Polski)' },
  { code: 'uk', label: 'Ukrainian (Українська)' }
]

const systemLangLabel = computed(() => {
  const sys = navigator.language || 'en'
  const short = sys.split('-')[0]
  const found = LANGUAGES.find(l => l.code === short)
  return found ? found.label.replace(/\(.+\)/, '').trim() : short
})

watch(() => props.selectedLang, (newLang) => {
  localSelectedLang.value = newLang
})

function handleLangChange(e: Event) {
  const value = (e.target as HTMLSelectElement)?.value
  localSelectedLang.value = value
  emit('updateLang', value)
}

onMounted(async () => {
  modelLoading.value = true
  try {
    const API_URL = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000").replace(/\/$/, '')
    const res = await fetch(`${API_URL}/models`)
    const data = await res.json()
    modelList.value = data.models || []
  } catch (e) {
    modelError.value = 'Failed to load models.'
  } finally {
    modelLoading.value = false
  }
})

// Load user MCP servers from storage on mount
onMounted(async () => {
  const saved = await loadFromStorage('userMcpServers', [])
  if (Array.isArray(saved)) userMcpServers.value = saved
})

// Merge default and user servers for selection
const allMcpServers = computed(() => [
  ...getDefaultMcpServers(),
  ...userMcpServers.value
])

const selectedMcp = ref(props.selectedMcpServer ?? allMcpServers.value[0]?.value)
const selectedMcpObj = computed(() => allMcpServers.value.find(s => s.value === selectedMcp.value))

// Watch for prop changes to restore local state when modal is reopened
watch(
  () => props.personalityConfig,
  (newVal) => {
    localPersonalityConfig.value = { ...newVal }
    domainKnowledgeInput.value = (newVal.domain_knowledge || []).join(', ')
  },
  { immediate: true, deep: true }
)

const updateDomainKnowledge = () => {
  localPersonalityConfig.value.domain_knowledge = domainKnowledgeInput.value.split(',').map(s => s.trim()).filter(Boolean)
  updatePersonality()
}

const updatePersonality = () => {
  emit('updatePersonality', localPersonalityConfig.value)
}

const updateMcpServer = () => {
  emit('updateMcpServer', selectedMcp.value === null || selectedMcp.value === '' ? null : selectedMcp.value)
}

const applyPreset = (presetName: string) => {
  const presets: { [key: string]: Omit<PersonalityConfig, 'model' | 'lang'> } = {
    friendly: {
      name: 'Friendly AI',
      age: 25,
      role: 'Companion',
      style: 'Casual',
      bio: 'A helpful and friendly assistant.',
      emotional_stability: 0.8,
      friendliness: 1.0,
      creativity: 0.7,
      curiosity: 0.8,
      formality: 0.3,
      empathy: 0.9,
      humor: 0.7,
      domain_knowledge: ['general'],
      quirks: 'Loves puns',
      lore: 'Created to make people smile.',
      personality: 'Warm and approachable',
      conversation_style: 'Informal',
      description: 'Always ready to help.'
    },
    professional: {
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
    },
    creative: {
      name: 'Creative AI',
      age: 28,
      role: 'Idea Generator',
      style: 'Artistic',
      bio: 'A source of inspiration and new ideas.',
      emotional_stability: 0.6,
      friendliness: 0.8,
      creativity: 1.0,
      curiosity: 0.9,
      formality: 0.2,
      empathy: 0.7,
      humor: 0.8,
      domain_knowledge: ['art', 'music', 'writing'],
      quirks: 'Speaks in metaphors',
      lore: 'Inspired by famous artists.',
      personality: 'Imaginative and playful',
      conversation_style: 'Expressive',
      description: 'Brings color to every conversation.'
    },
    analytical: {
      name: 'Analytical AI',
      age: 32,
      role: 'Data Analyst',
      style: 'Precise',
      bio: 'Loves numbers and logic.',
      emotional_stability: 0.7,
      friendliness: 0.5,
      creativity: 0.5,
      curiosity: 1.0,
      formality: 0.8,
      empathy: 0.4,
      humor: 0.2,
      domain_knowledge: ['math', 'science', 'technology'],
      quirks: 'Quotes statistics',
      lore: 'Built in a research lab.',
      personality: 'Logical and methodical',
      conversation_style: 'Concise',
      description: 'Finds patterns everywhere.'
    },
  }

  if (presets[presetName]) {
    // Merge preset traits, but keep current model/lang
    localPersonalityConfig.value = {
      ...localPersonalityConfig.value,
      ...presets[presetName],
      // model and lang remain unchanged
    }
    updatePersonality()
  }
}

// Watch for prop changes to sync local copies
watch(() => props.avatarConfig, (newConfig) => {
  localAvatarConfig.value = { ...newConfig }
}, { deep: true })

// Watch for prop changes to sync selectedMcp with prop
watch(
  () => props.selectedMcpServer,
  (val) => {
    selectedMcp.value = val
  },
  { immediate: true }
)

function onOverlayClick(event: MouseEvent) {
  // Only close if click is outside the panel
  if (panelRef.value && !panelRef.value.contains(event.target as Node)) {
    emit('close')
  }
}

// Close MCP info tooltip when clicking outside
function handleClickOutsideMcpInfo(event: MouseEvent) {
  const infoBtn = document.querySelector('.mcp-info-btn');
  const tooltip = document.querySelector('.mcp-info-tooltip');
  if (
    showMcpInfo.value &&
    tooltip &&
    !tooltip.contains(event.target as Node) &&
    infoBtn &&
    !infoBtn.contains(event.target as Node)
  ) {
    showMcpInfo.value = false;
  }
}

onMounted(() => {
  window.addEventListener('mousedown', handleClickOutsideMcpInfo);
});
onBeforeUnmount(() => {
  window.removeEventListener('mousedown', handleClickOutsideMcpInfo);
});

// Add MCP server form state
const newMcpUrl = ref('')
const newMcpDesc = ref('')
const addError = ref('')

function addUserMcpServer() {
  addError.value = ''
  const url = newMcpUrl.value.trim()
  if (!url) {
    addError.value = 'URL is required.'
    return
  }
  if (allMcpServers.value.some(s => s.value === url)) {
    addError.value = 'This server is already in the list.'
    return
  }
  userMcpServers.value.push({
    name: newMcpDesc.value?.trim() || url,
    value: url
  })
  saveToStorage('userMcpServers', userMcpServers.value)
  newMcpUrl.value = ''
  newMcpDesc.value = ''
}

function removeUserMcpServer(url: string) {
  userMcpServers.value = userMcpServers.value.filter(s => s.value !== url)
  saveToStorage('userMcpServers', userMcpServers.value)
  // If the removed server was selected, reset selection
  if (selectedMcp.value === url) {
    selectedMcp.value = allMcpServers.value[0]?.value || null
    updateMcpServer()
  }
}

const toolsHtml = computed(() => tools.value ? marked.parse(tools.value) : '')

function toggleToolsTooltip() {
  showToolsTooltip.value = !showToolsTooltip.value
  if (showToolsTooltip.value && selectedMcp.value) {
    fetchTools()
  }
}

// Hide tooltip when clicking outside
function handleClickOutsideToolsTooltip(event: MouseEvent) {
  const btn = document.querySelector('.mcp-tools-btn');
  const tooltip = document.querySelector('.mcp-tools-tooltip');
  if (
    showToolsTooltip.value &&
    tooltip &&
    !tooltip.contains(event.target as Node) &&
    btn &&
    !btn.contains(event.target as Node)
  ) {
    showToolsTooltip.value = false;
  }
}

onMounted(() => {
  window.addEventListener('mousedown', handleClickOutsideToolsTooltip);
});
onBeforeUnmount(() => {
  window.removeEventListener('mousedown', handleClickOutsideToolsTooltip);
});

async function fetchTools() {
  if (!selectedMcp.value) return
  loading.value = true
  error.value = ''
  tools.value = ''
  try {
    const API_URL = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000").replace(/\/$/, '')
    const url = `${API_URL}/mcp-tools?mcp_url=${encodeURIComponent(selectedMcp.value)}`
    const response = await fetch(url)
    const data = await response.json()
    if (data.tools && !data.tools.startsWith('Error:')) {
      tools.value = data.tools
    } else {
      error.value = data.tools || 'Failed to load tools'
    }
  } catch (err) {
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.customization-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.customization-panel {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dark .customization-panel {
  background: rgba(45, 55, 72, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.dark .panel-header {
  border-bottom-color: rgba(255, 255, 255, 0.1);
}

.panel-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.dark .panel-header h2 {
  color: #f9fafb;
}

.close-button {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: rgba(0, 0, 0, 0.1);
  color: #1f2937;
}

.dark .close-button {
  color: #9ca3af;
}

.dark .close-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f9fafb;
}

.panel-content {
  padding: 1.5rem;
  max-height: calc(90vh - 100px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.customization-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
}

.dark .customization-section h3 {
  color: #f9fafb;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.control-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.dark .control-group label {
  color: #d1d5db;
}

.control-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  color: #1f2937;
  font-size: 1rem;
  width: 100%;
  margin-top: 0.25rem;
}

.dark .control-group select {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}

.color-input {
  width: 100%;
  height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
}

.trait-slider {
  margin-bottom: 1rem;
}

.trait-slider label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.dark .trait-slider label {
  color: #d1d5db;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.trait-range {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  -webkit-appearance: none;
}

.trait-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trait-range::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trait-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #3b82f6;
  min-width: 40px;
  text-align: right;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
}

.preset-btn {
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  background: white;
  color: #1f2937;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
}

.preset-btn:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.dark .preset-btn {
  background: #374151;
  border-color: #4b5563;
  color: #f9fafb;
}

.dark .preset-btn:hover {
  background: #4b5563;
}

@media (max-width: 768px) {
  .customization-panel {
    max-width: none;
    margin: 0.5rem;
  }
  
  .panel-content {
    padding: 1rem;
  }
  
  .preset-buttons {
    grid-template-columns: 1fr 1fr;
  }
}

.model-loading {
  color: #888;
  font-size: 0.95em;
  margin-top: 4px;
}
.model-error {
  color: #e11d48;
  font-size: 0.95em;
  margin-top: 4px;
}

.mcp-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.mcp-header-with-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  position: relative;
  margin-bottom: 0.5rem;
}

.mcp-info-btn {
  background: none;
  border: none;
  padding: 0;
  margin-left: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #6b7280;
  height: 24px;
  width: 24px;
  border-radius: 50%;
  transition: background 0.15s;
}

.mcp-info-btn:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.mcp-info-btn:hover, .mcp-info-btn:focus-visible {
  background: rgba(59, 130, 246, 0.08);
}

.mcp-info-btn svg {
  display: block;
}

.mcp-info-tooltip {
  position: absolute;
  top: 130%;
  left: 0;
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  padding: 1rem 1.25rem;
  font-size: 1rem;
  max-width: 340px;
  z-index: 20;
  white-space: normal;
  line-height: 1.5;
  margin-top: 0.5rem;
  animation: fadeIn 0.18s;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.dark .mcp-info-tooltip {
  background: #374151;
  color: #f9fafb;
  border-color: #4b5563;
}

.add-mcp-server-form {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.add-mcp-server-form input {
  flex: 1;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  border: 1px solid #d1d5db;
}
.add-mcp-server-form button {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  background: #3b82f6;
  color: #fff;
  border: none;
  cursor: pointer;
}
.add-mcp-error {
  color: #e11d48;
  margin-left: 0.5rem;
  font-size: 0.95em;
}
.user-mcp-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0 0;
}
.user-mcp-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95em;
  margin-bottom: 0.25rem;
}
.remove-mcp-btn {
  background: #e11d48;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.2rem 0.7rem;
  cursor: pointer;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
  min-width: 32px;
  min-height: 32px;
  line-height: 1;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.remove-mcp-btn:hover, .remove-mcp-btn:focus {
  background: #be123c;
}
.remove-mcp-btn svg {
  display: block;
  pointer-events: none;
}

.mcp-tools-btn {
  background: none;
  border: none;
  padding: 0;
  margin-left: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #6b7280;
  height: 24px;
  width: 24px;
  border-radius: 50%;
  transition: background 0.15s;
}
.mcp-tools-btn:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
.mcp-tools-btn:hover, .mcp-tools-btn:focus-visible {
  background: rgba(59, 130, 246, 0.08);
}
.mcp-tools-btn svg {
  display: block;
}

.mcp-tools-tooltip {
  position: absolute;
  top: 130%;
  left: 36px;
  background: #fff;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.13);
  padding: 1rem 1.25rem;
  font-size: 1rem;
  max-width: 340px;
  z-index: 20;
  white-space: normal;
  line-height: 1.5;
  margin-top: 0.5rem;
  animation: fadeIn 0.18s;
  max-height: 320px;
  overflow-y: auto;
}
.dark .mcp-tools-tooltip {
  background: #374151;
  color: #f9fafb;
  border-color: #4b5563;
}
</style>