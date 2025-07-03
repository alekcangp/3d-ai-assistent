<template>
  <div class="customization-overlay">
    <div class="customization-panel">
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
              <small>{{ modelList.find(m => m.id === selectedModel)?.description }}</small>
            </div>
          </div>
        </div>

        <div class="customization-section">
          <h3>MCP Server</h3>
          <div class="control-group">
            <label for="mcp-select">MCP Server</label>
            <select id="mcp-select" v-model="selectedMcp" @change="updateMcpServer">
              <option v-for="server in mcpServers" :key="server.name" :value="server.value">{{ server.name }}</option>
            </select>
            <div class="mcp-description">{{ selectedMcpObj?.description }}</div>
          </div>
        </div>

        <div class="customization-section">
          <h3>Personality Traits</h3>

          <div class="control-group">
            <label for="lang-select">Language</label>
            <select id="lang-select" :value="selectedLang" @change="e => emit('updateLang', (e.target as HTMLSelectElement)?.value)">
              <option value="system">System Default</option>
              <option value="en">English</option>
              <option value="zh">Chinese (中文)</option>
              <option value="hi">Hindi (हिन्दी)</option>
              <option value="es">Spanish (Español)</option>
              <option value="fr">French (Français)</option>
              <option value="ar">Arabic (العربية)</option>
              <option value="bn">Bengali (বাংলা)</option>
              <option value="pt">Portuguese (Português)</option>
              <option value="ru">Russian (Русский)</option>
              <option value="ja">Japanese (日本語)</option>
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
import { ref, watch, onMounted, computed } from 'vue'
import type { AvatarConfig, PersonalityConfig } from '../types'

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

const mcpServers = [
  {
    name: 'Only LLM knowledge',
    value: null,
    description: 'Use only the LLM\'s internal knowledge. No real-time data.'
  },
  {
    name: 'CoinGecko',
    value: 'https://mcp.api.coingecko.com/sse',
    description: 'CoinGecko is a cryptocurrency data platform.'
  },
  {
    name: 'Fetch',
    value: 'https://remote.mcpservers.org/fetch/mcp',
    description: 'An MCP server that provides web content fetching capabilities. This server enables LLMs to retrieve and process content from web pages, converting HTML to markdown for easier consumption.'
  },
  {
    name: 'Sequential Thinking',
    value: 'https://remote.mcpservers.org/sequentialthinking/mcp',
    description: 'An MCP server implementation that provides a tool for dynamic and reflective problem-solving through a structured thinking process.'
  }
]
const selectedMcp = ref(props.selectedMcpServer ?? mcpServers[0].value)
const selectedMcpObj = computed(() => mcpServers.find(s => s.value === selectedMcp.value))

onMounted(async () => {
  modelLoading.value = true
  try {
    const res = await fetch('http://localhost:8000/models')
    const data = await res.json()
    modelList.value = data.models || []
  } catch (e) {
    modelError.value = 'Failed to load models.'
  } finally {
    modelLoading.value = false
  }
})

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
</style>