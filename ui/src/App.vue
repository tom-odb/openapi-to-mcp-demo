<template>
  <div id="app" class="container">
    <header>
      <h1>OpenAPI to MCP Converter</h1>
      <p>Convert OpenAPI specifications into working MCP servers</p>
    </header>

    <main>
      <SpecUploader v-if="!store.currentSpec" />

      <div v-else class="workflow">
        <div class="progress-bar">
          <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
            1. Upload Spec
          </div>
          <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
            2. Enrich Endpoints
          </div>
          <div class="step" :class="{ active: currentStep >= 3, completed: currentStep > 3 }">
            3. Composite Tools
          </div>
          <div class="step" :class="{ active: currentStep >= 4 }">
            4. Generate Server
          </div>
        </div>

        <EndpointList v-if="currentStep === 2" @next="currentStep = 3" />
        <CompositeToolCreator v-if="currentStep === 3" @next="currentStep = 4" @back="currentStep = 2" />
        <ServerGenerator v-if="currentStep === 4" />

        <button @click="reset" class="reset-btn">Start Over</button>
      </div>

      <div v-if="store.error" class="error">
        {{ store.error }}
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useConverterStore } from './stores/converter'
import SpecUploader from './components/SpecUploader.vue'
import EndpointList from './components/EndpointList.vue'
import CompositeToolCreator from './components/CompositeToolCreator.vue'
import ServerGenerator from './components/ServerGenerator.vue'

const store = useConverterStore()
const currentStep = ref(1)

watch(() => store.currentSpec, (newVal) => {
  if (newVal) {
    currentStep.value = 2
  }
})

const reset = () => {
  store.reset()
  currentStep.value = 1
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
  color: #333;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #2c3e50;
}

header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

main {
  min-height: 400px;
}

.workflow {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  padding: 0 20px;
}

.step {
  flex: 1;
  text-align: center;
  padding: 15px;
  background: #ecf0f1;
  margin: 0 5px;
  border-radius: 4px;
  font-weight: 500;
  transition: all 0.3s;
}

.step.active {
  background: #3498db;
  color: white;
}

.step.completed {
  background: #2ecc71;
  color: white;
}

.error {
  background: #e74c3c;
  color: white;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: center;
}

.reset-btn {
  margin-top: 30px;
  padding: 10px 20px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.reset-btn:hover {
  background: #7f8c8d;
}

button {
  cursor: pointer;
  transition: all 0.2s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
