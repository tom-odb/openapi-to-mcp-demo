<template>
  <div class="tool-preview">
    <h2>Generate MCP Tools</h2>
    <p class="description">
      Configure your MCP server and preview the tools
    </p>

    <div class="config-form">
      <div class="form-group">
        <label>API Name:</label>
        <input v-model="apiName" type="text" placeholder="e.g., my-api" />
      </div>
      <div class="form-group">
        <label>Base URL:</label>
        <input v-model="baseUrl" type="text" placeholder="e.g., https://api.example.com" />
      </div>
      <button @click="generateTools" class="btn-generate" :disabled="!apiName || !baseUrl">
        Generate Tool Definitions
      </button>
    </div>

    <div v-if="store.toolModel" class="tools-preview">
      <!-- Composite Tools Section -->
      <div v-if="store.toolModel.composite_tools && store.toolModel.composite_tools.length > 0" class="composite-section">
        <h3>Composite Tools ({{ store.toolModel.composite_tools.length }})</h3>
        <div class="tools-list">
          <div v-for="tool in store.toolModel.composite_tools" :key="tool.name" class="tool-card composite">
            <div class="tool-header">
              <h4>{{ tool.name }}</h4>
              <span class="badge composite">Composite</span>
            </div>
            <p class="tool-description">{{ tool.description }}</p>
            <p class="use-case"><strong>Use Case:</strong> {{ tool.use_case_description }}</p>
            <details>
              <summary>Input Schema</summary>
              <pre>{{ JSON.stringify(tool.input_schema, null, 2) }}</pre>
            </details>
            <details>
              <summary>Endpoints Used ({{ tool.endpoint_mappings.length }})</summary>
              <ul class="endpoint-list">
                <li v-for="(mapping, idx) in tool.endpoint_mappings" :key="idx">
                  <strong>{{ mapping.method.toUpperCase() }}</strong> {{ mapping.path }}
                  <p v-if="mapping.purpose" class="purpose">{{ mapping.purpose }}</p>
                </li>
              </ul>
            </details>
            <details>
              <summary>Orchestration Logic</summary>
              <p class="orchestration">{{ tool.orchestration_logic }}</p>
            </details>
          </div>
        </div>
      </div>

      <!-- Regular Tools Section -->
      <h3>Standard Tools ({{ store.toolModel.tools.length }})</h3>
      <div class="tools-list">
        <div v-for="tool in store.toolModel.tools" :key="tool.name" class="tool-card">
          <h4>{{ tool.name }}</h4>
          <p class="tool-description">{{ tool.description }}</p>
          <details>
            <summary>Input Schema</summary>
            <pre>{{ JSON.stringify(tool.input_schema, null, 2) }}</pre>
          </details>
          <p class="endpoint-mapping">
            <strong>Maps to:</strong> {{ tool.endpoint_mapping.method.toUpperCase() }} {{ tool.endpoint_mapping.path }}
          </p>
        </div>
      </div>

      <button @click="$emit('next')" class="btn-next">
        Continue to Server Generation
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const apiName = ref('')
const baseUrl = ref('')

defineEmits(['next'])

const generateTools = async () => {
  try {
    await store.generateTools(apiName.value, baseUrl.value)
  } catch (error) {
    console.error('Tool generation failed:', error)
  }
}
</script>

<style scoped>
.tool-preview {
  padding: 20px;
}

h2 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  margin-bottom: 30px;
}

.config-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-generate {
  padding: 10px 20px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}

.btn-generate:hover:not(:disabled) {
  background: #2980b9;
}

.tools-preview {
  margin-top: 30px;
}

.composite-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #f3e5f5;
  border-radius: 6px;
}

h3 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.tool-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 20px;
  background: white;
}

.tool-card.composite {
  border: 2px solid #9b59b6;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.tool-card h4 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-family: monospace;
}

.badge.composite {
  padding: 4px 12px;
  background: #9b59b6;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.tool-description {
  color: #555;
  margin-bottom: 15px;
  line-height: 1.6;
}

.use-case {
  margin-bottom: 15px;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 14px;
}

.endpoint-list {
  margin-top: 10px;
  padding-left: 20px;
}

.endpoint-list li {
  margin-bottom: 8px;
}

.purpose {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.orchestration {
  margin-top: 10px;
  white-space: pre-line;
  line-height: 1.6;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
}

details {
  margin-bottom: 15px;
}

summary {
  cursor: pointer;
  color: #3498db;
  font-weight: 500;
  padding: 5px 0;
}

pre {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 12px;
  margin-top: 10px;
}

.endpoint-mapping {
  color: #7f8c8d;
  font-size: 14px;
  font-family: monospace;
}

.btn-next {
  padding: 12px 30px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
}

.btn-next:hover {
  background: #27ae60;
}
</style>
