<template>
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <svg class="ai-logo" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="4" y="4" width="24" height="24" rx="8" fill="#0f172a" stroke="#00FFF0" stroke-width="2"/>
          <circle cx="16" cy="16" r="6.5" stroke="#00FFF0" stroke-width="2" fill="none"/>
          <circle cx="16" cy="16" r="2.5" fill="#00FFF0"/>
          <path d="M10 16c0-3.3 2.7-6 6-6s6 2.7 6 6-2.7 6-6 6" stroke="#00FFF0" stroke-width="1.5" stroke-linecap="round" stroke-dasharray="2 2"/>
          <path d="M16 9v2M16 21v2M9 16h2M21 16h2" stroke="#00FFF0" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        <h1 class="scifi-title">{{ personalityConfig && personalityConfig.name ? personalityConfig.name : 'AI Assistant' }}</h1>
      </div>
      <div class="scanner-bar"></div>
      
      <div class="header-controls">
        <button 
          class="control-btn"
          @click="$emit('toggleCustomization')"
          title="Customize Assistant"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1 0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
          </svg>
        </button>
        
        <button 
          class="control-btn theme-toggle"
          @click="$emit('toggleTheme')"
          :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
        >
          <svg v-if="isDarkMode" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 18C8.69 18 6 15.31 6 12S8.69 6 12 6 18 8.69 18 12 15.31 18 12 18M20 8.69V4H15.31L12 .69 8.69 4H4V8.69L.69 12 4 15.31V20H8.69L12 23.31 15.31 20H20V15.31L23.31 12 20 8.69Z"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M17.75 4.09L15.22 6.03L16.13 9.09L13.5 7.28L10.87 9.09L11.78 6.03L9.25 4.09L12.44 4L13.5 1L14.56 4L17.75 4.09M21.25 11L19.61 12.25L20.2 14.23L18.5 13.06L16.8 14.23L17.39 12.25L15.75 11L17.81 10.95L18.5 9L19.19 10.95L21.25 11M18.97 15.95C19.8 15.87 20.69 17.05 20.16 17.8C19.84 18.25 19.5 18.67 19.08 19.07C15.17 23 8.84 23 4.94 19.07C1.03 15.17 1.03 8.83 4.94 4.93C5.34 4.53 5.76 4.17 6.21 3.85C6.96 3.32 8.14 4.21 8.06 5.04C7.79 7.9 8.75 10.87 10.95 13.06C13.14 15.26 16.1 16.22 18.97 15.95Z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Tools Modal -->
    <div v-if="showToolsModal" class="modal-overlay" @click="showToolsModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Available Tools</h3>
          <button class="close-btn" @click="showToolsModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Loading tools...</p>
          </div>
          <div v-else-if="error" class="error">
            <p>{{ error }}</p>
          </div>
          <div v-else class="tools-list">
            <div v-html="toolsHtml"></div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed, ref, watch, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'
marked.setOptions({ breaks: true, gfm: true })

const props = defineProps({
  isDarkMode: Boolean,
  selectedLang: {
    type: String,
    default: 'ru-RU'
  },
  isOnline: Boolean,
  selectedMcpServer: {
    type: [String, null],
    default: null
  },
  personalityConfig: {
    type: Object,
    default: () => ({})
  }
})
const emit = defineEmits(['toggleTheme', 'toggleCustomization', 'updateLang', 'toggleOnline'])

// Tools modal state
const showToolsModal = ref(false)
const tools = ref('')
const loading = ref(false)
const error = ref('')

// Fetch tools when modal opens
watch(showToolsModal, async (newVal) => {
  if (newVal && props.selectedMcpServer) {
    await fetchTools()
  }
})

async function fetchTools() {
  if (!props.selectedMcpServer) return
  
  loading.value = true
  error.value = ''
  tools.value = ''
  
  try {
    const API_URL = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000").replace(/\/$/, '')
    console.log('API_URL:', API_URL)
    console.log('Selected MCP Server:', props.selectedMcpServer)
    
    const url = `${API_URL}/mcp-tools?mcp_url=${encodeURIComponent(props.selectedMcpServer)}`
    console.log('Requesting URL:', url)
    
    const response = await fetch(url)
    console.log('Response status:', response.status)
    
    const data = await response.json()
    console.log('Response data:', data)
    
    if (data.tools && !data.tools.startsWith('Error:')) {
      tools.value = data.tools
    } else {
      error.value = data.tools || 'Failed to load tools'
    }
  } catch (err) {
    console.error('Fetch error:', err)
    error.value = 'Failed to connect to server'
  } finally {
    loading.value = false
  }
}

const toolsHtml = computed(() => tools.value ? marked.parse(tools.value) : '')

let keepAliveInterval: number | undefined

onMounted(async () => {
  // Periodically fetch /models every 10 minutes to keep backend awake
  const API_URL = (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000').replace(/\/$/, '')
  keepAliveInterval = window.setInterval(async () => {
    try {
      await fetch(`${API_URL}/models`)
    } catch (e) {
      // Ignore errors
    }
  }, 10 * 60 * 1000)
})

onUnmounted(() => {
  if (keepAliveInterval) clearInterval(keepAliveInterval)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');

.header {
  background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
  box-shadow: 0 2px 24px 0 #00fff055;
  border-bottom: 1.5px solid #00fff0cc;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s ease;
  overflow: hidden;
}

.dark .header {
  background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
  border-bottom: 1.5px solid #00fff0cc;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 2rem 0.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ai-logo {
  filter: drop-shadow(0 0 8px #00fff0cc);
  animation: logoPulse 2.5s infinite alternate;
}
@keyframes logoPulse {
  0% { filter: drop-shadow(0 0 8px #00fff0cc); }
  100% { filter: drop-shadow(0 0 16px #00fff0); }
}

.scifi-title {
  font-family: 'Orbitron', 'Segoe UI', Arial, sans-serif;
  font-size: 1.7rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #00fff0;
  text-shadow: 0 0 8px #00fff0cc, 0 0 2px #fff;
  margin: 0;
  text-transform: uppercase;
  transition: color 0.2s;
}

.dark .scifi-title {
  color: #00fff0;
}

.scanner-bar {
  position: absolute;
  left: 0;
  right: 0;
  top: 100%;
  height: 3px;
  background: linear-gradient(90deg, #00fff0 0%, #00b3ff 100%);
  box-shadow: 0 0 12px #00fff0cc;
  opacity: 0.7;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.control-btn {
  background: rgba(0,255,240,0.08);
  border: 1.5px solid #00fff0cc;
  color: #00fff0;
  padding: 0.5rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(.4,2,.6,1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 8px #00fff033, 0 1px 2px #00fff011;
  backdrop-filter: blur(2px);
}

.control-btn:hover {
  background: rgba(0,255,240,0.18);
  box-shadow: 0 0 16px #00fff0cc, 0 2px 8px #00fff022;
  transform: translateY(-2px) scale(1.05);
}

.dark .control-btn {
  background: rgba(0,255,240,0.12);
  border: 1.5px solid #00fff0cc;
}

.dark .control-btn:hover {
  background: rgba(0,255,240,0.22);
}

.lang-label {
  margin-right: 6px;
  font-size: 1rem;
  color: #374151;
  font-weight: 500;
}

.lang-select {
  padding: 7px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  background: #f9fafb;
  color: #1f2937;
  font-size: 1rem;
  margin-right: 16px;
  outline: none;
  transition: border 0.2s;
}
.lang-select:focus {
  border: 1.5px solid #3b82f6;
}
.dark .lang-label {
  color: #f9fafb;
}
.dark .lang-select {
  background: #23272f;
  color: #f9fafb;
  border: 1px solid #334155;
}

.mcp-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-right: 1rem;
}
.mcp-label {
  font-size: 0.95rem;
  color: #374151;
  font-weight: 500;
}
.mcp-value {
  font-size: 0.95rem;
  color: #3b82f6;
  font-weight: 600;
}
.mcp-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
  background: #d1d5db;
  border: 1.5px solid #cbd5e1;
  vertical-align: middle;
  transition: background 0.2s, border 0.2s;
}
.mcp-indicator--on {
  background: #22c55e;
  border-color: #16a34a;
}
.mcp-indicator--off {
  background: #d1d5db;
  border-color: #cbd5e1;
}
.dark .mcp-indicator--on {
  background: #22c55e;
  border-color: #16a34a;
}
.dark .mcp-indicator--off {
  background: #374151;
  border-color: #4b5563;
}

@media (max-width: 768px) {
  .header-content {
    padding: 1rem;
  }
  
  .logo h1 {
    font-size: 1.25rem;
  }
}

/* Tools Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 2px solid #00fff0;
  border-radius: 16px;
  box-shadow: 0 0 32px rgba(0, 255, 240, 0.3);
  max-width: 90vw;
  max-height: 80vh;
  width: 600px;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem 1rem 2rem;
  border-bottom: 1px solid #334155;
  background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
}

.modal-header h3 {
  color: #00fff0;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  text-shadow: 0 0 8px #00fff0cc;
}

.close-btn {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid #ef4444;
  color: #ef4444;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.2);
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
}

.modal-body {
  padding: 1.5rem 2rem 2rem 2rem;
  max-height: 60vh;
  overflow-y: auto;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #00fff0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0, 255, 240, 0.2);
  border-top: 3px solid #00fff0;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #ef4444;
  text-align: center;
  padding: 2rem;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.tools-list {
  color: #e2e8f0;
  font-size: 0.9rem;
  line-height: 1.5;
}
:deep(.tools-list strong), :deep(.tools-list b) {
  color: #00fff0 !important;
}
.tools-list code, .tools-list pre {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.tools-list pre {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  color: #e2e8f0;
  margin: 0;
}

/* Dark mode adjustments */
.dark .modal-content {
  background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
}

.dark .modal-header {
  background: linear-gradient(90deg, #0f172a 0%, #020617 100%);
  border-bottom: 1px solid #1e293b;
}

.dark .tools-list pre {
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid #1e293b;
}
</style>