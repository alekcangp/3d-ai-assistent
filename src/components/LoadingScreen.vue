<template>
  <div class="loading-screen">
    <div class="loading-content">
      <div class="logo-animation">
        <div class="ai-brain">
          <div class="brain-core"></div>
          <div class="neural-network">
            <div class="node" v-for="i in 8" :key="i" :style="{ '--delay': i * 0.2 + 's' }"></div>
          </div>
        </div>
      </div>
      
      <h2>Initializing AI Assistant</h2>
      <p>Loading IOIntel neural networks...</p>
      
      <div class="progress-container">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="progress-text">{{ progress }}%</span>
      </div>
      
      <div class="loading-steps">
      <div class="step" :class="{ active: progress >= 10 }">
          <span class="checkmark">✓</span>
          Waking up... (50 seconds or more)
        </div>
        <div class="step" :class="{ active: progress >= 20 }">
          <span class="checkmark">✓</span>
          Loading WebGPU Runtime
        </div>
        <div class="step" :class="{ active: progress >= 50 }">
          <span class="checkmark">✓</span>
          Initializing Neural Networks
        </div>
        <div class="step" :class="{ active: progress >= 80 }">
          <span class="checkmark">✓</span>
          Configuring AI Personality
        </div>
        <div class="step" :class="{ active: progress >= 100 }">
          <span class="checkmark">✓</span>
          Ready to Assist
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  progress: number
}>()
</script>

<style scoped>
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-content {
  text-align: center;
  color: white;
  max-width: 400px;
  padding: 2rem;
}

.logo-animation {
  margin-bottom: 2rem;
}

.ai-brain {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto;
}

.brain-core {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  border-radius: 50%;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: coreGlow 2s ease-in-out infinite alternate;
}

.neural-network {
  position: absolute;
  width: 100%;
  height: 100%;
}

.node {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #60a5fa;
  border-radius: 50%;
  animation: nodeFlash 2s infinite ease-in-out;
  animation-delay: var(--delay);
}

.node:nth-child(1) { top: 10%; left: 50%; transform: translateX(-50%); }
.node:nth-child(2) { top: 25%; right: 15%; }
.node:nth-child(3) { top: 50%; right: 5%; transform: translateY(-50%); }
.node:nth-child(4) { bottom: 25%; right: 15%; }
.node:nth-child(5) { bottom: 10%; left: 50%; transform: translateX(-50%); }
.node:nth-child(6) { bottom: 25%; left: 15%; }
.node:nth-child(7) { top: 50%; left: 5%; transform: translateY(-50%); }
.node:nth-child(8) { top: 25%; left: 15%; }

.loading-content h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.loading-content p {
  font-size: 1rem;
  opacity: 0.8;
  margin: 0 0 2rem 0;
}

.progress-container {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #60a5fa, #3b82f6);
  transition: width 0.3s ease;
  border-radius: 4px;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.loading-steps {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  text-align: left;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.step.active {
  opacity: 1;
}

.checkmark {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  transition: all 0.3s ease;
}

.step.active .checkmark {
  background: #10b981;
  color: white;
}

@keyframes coreGlow {
  0% { box-shadow: 0 0 20px rgba(96, 165, 250, 0.5); }
  100% { box-shadow: 0 0 40px rgba(96, 165, 250, 0.8); }
}

@keyframes nodeFlash {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}
</style>