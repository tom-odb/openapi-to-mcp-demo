<template>
  <div class="composite-tool-creator">
    <h2>Create Composite Tools</h2>
    <p class="description">
      Combine multiple endpoints into a single tool for complex use cases
    </p>

    <!-- Created Composite Tools -->
    <div v-if="store.compositeTools.length > 0" class="created-tools">
      <h3>Created Composite Tools ({{ store.compositeTools.length }})</h3>
      <div class="composite-tools-list">
        <div v-for="(tool, index) in store.compositeTools" :key="index" class="composite-tool-card">
          <div class="tool-header">
            <h4>{{ tool.name }}</h4>
            <span class="badge composite">Composite</span>
          </div>
          <p class="tool-description">{{ tool.description }}</p>
          <p class="use-case"><strong>Use Case:</strong> {{ tool.use_case_description }}</p>
          <details>
            <summary>Endpoints Used ({{ tool.endpoint_mappings.length }})</summary>
            <ul class="endpoint-list">
              <li v-for="(mapping, idx) in tool.endpoint_mappings" :key="idx">
                <span class="method" :class="mapping.method">{{ mapping.method.toUpperCase() }}</span>
                <span class="path">{{ mapping.path }}</span>
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

    <!-- Create New Composite Tool -->
    <div class="creator-form">
      <h3>Create New Composite Tool</h3>
      
      <!-- Use Case Description -->
      <div class="form-section">
        <label>Describe Your Use Case:</label>
        <textarea
          v-model="useCaseDescription"
          placeholder="E.g., Retrieve orders with full customer information including their contact details and order history..."
          rows="4"
        ></textarea>
        <p class="hint">Describe what you want to achieve. The AI will determine how to combine the selected endpoints.</p>
      </div>

      <!-- Endpoint Selection -->
      <div class="form-section">
        <label>Select Endpoints to Combine ({{ selectedEndpoints.length }} selected):</label>
        <div class="endpoints-grid">
          <div 
            v-for="endpoint in store.endpoints" 
            :key="endpoint.path + endpoint.method"
            class="endpoint-checkbox"
            :class="{ selected: isSelected(endpoint) }"
          >
            <input
              type="checkbox"
              :id="endpoint.path + endpoint.method"
              :value="endpoint"
              @change="toggleEndpoint(endpoint)"
              :checked="isSelected(endpoint)"
            />
            <label :for="endpoint.path + endpoint.method">
              <span class="method" :class="endpoint.method">{{ endpoint.method.toUpperCase() }}</span>
              <span class="path">{{ endpoint.path }}</span>
              <p v-if="endpoint.summary" class="summary">{{ endpoint.summary }}</p>
            </label>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button 
          @click="createCompositeTool" 
          class="btn-create"
          :disabled="!canCreate || store.loading"
        >
          {{ store.loading ? 'Creating...' : 'Create Composite Tool' }}
        </button>
      </div>
    </div>

    <!-- Navigation -->
    <div class="navigation">
      <button @click="$emit('back')" class="btn-back">
        ← Back to Enrichment
      </button>
      <button @click="$emit('next')" class="btn-next">
        Continue to Tool Generation →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const useCaseDescription = ref('')
const selectedEndpoints = ref([])

defineEmits(['next', 'back'])

const isSelected = (endpoint) => {
  return selectedEndpoints.value.some(
    ep => ep.path === endpoint.path && ep.method === endpoint.method
  )
}

const toggleEndpoint = (endpoint) => {
  const index = selectedEndpoints.value.findIndex(
    ep => ep.path === endpoint.path && ep.method === endpoint.method
  )
  
  if (index >= 0) {
    selectedEndpoints.value.splice(index, 1)
  } else {
    selectedEndpoints.value.push({
      path: endpoint.path,
      method: endpoint.method
    })
  }
}

const canCreate = computed(() => {
  return useCaseDescription.value.trim().length > 10 && selectedEndpoints.value.length >= 2
})

const createCompositeTool = async () => {
  if (!canCreate.value) return

  try {
    await store.createCompositeTool(
      useCaseDescription.value,
      selectedEndpoints.value
    )
    
    // Reset form
    useCaseDescription.value = ''
    selectedEndpoints.value = []
  } catch (error) {
    console.error('Failed to create composite tool:', error)
    alert('Failed to create composite tool. Please try again.')
  }
}
</script>

<style scoped>
.composite-tool-creator {
  padding: 20px;
}

h2 {
  margin-bottom: 10px;
  color: #2c3e50;
}

h3 {
  margin: 20px 0 15px;
  color: #2c3e50;
}

.description {
  color: #7f8c8d;
  margin-bottom: 30px;
}

/* Created Tools */
.created-tools {
  margin-bottom: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

.composite-tools-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.composite-tool-card {
  background: white;
  border: 2px solid #9b59b6;
  border-radius: 6px;
  padding: 15px;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.tool-header h4 {
  margin: 0;
  color: #2c3e50;
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
  margin-bottom: 10px;
  color: #555;
}

.use-case {
  margin-bottom: 15px;
  padding: 10px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 14px;
}

details {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 4px;
}

details summary {
  cursor: pointer;
  font-weight: 600;
  color: #2c3e50;
  user-select: none;
}

details summary:hover {
  color: #9b59b6;
}

.endpoint-list {
  margin-top: 10px;
  padding-left: 20px;
}

.endpoint-list li {
  margin-bottom: 8px;
}

.orchestration {
  margin-top: 10px;
  white-space: pre-line;
  line-height: 1.6;
}

/* Creator Form */
.creator-form {
  border: 2px solid #ddd;
  border-radius: 6px;
  padding: 20px;
  margin-bottom: 30px;
}

.form-section {
  margin-bottom: 25px;
}

.form-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #2c3e50;
}

.form-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: vertical;
}

.hint {
  margin-top: 8px;
  font-size: 13px;
  color: #7f8c8d;
  font-style: italic;
}

/* Endpoints Grid */
.endpoints-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.endpoint-checkbox {
  border: 2px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  transition: all 0.2s;
}

.endpoint-checkbox:hover {
  border-color: #9b59b6;
  background: #f8f9fa;
}

.endpoint-checkbox.selected {
  border-color: #9b59b6;
  background: #f3e5f5;
}

.endpoint-checkbox input[type="checkbox"] {
  margin-right: 8px;
}

.endpoint-checkbox label {
  cursor: pointer;
  display: block;
}

.method {
  padding: 2px 8px;
  border-radius: 3px;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  margin-right: 8px;
}

.method.get {
  background: #61affe;
  color: white;
}

.method.post {
  background: #49cc90;
  color: white;
}

.method.put {
  background: #fca130;
  color: white;
}

.method.delete {
  background: #f93e3e;
  color: white;
}

.path {
  font-family: monospace;
  font-size: 13px;
  font-weight: 500;
}

.summary {
  margin-top: 5px;
  font-size: 12px;
  color: #7f8c8d;
}

.purpose {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
  font-style: italic;
}

/* Actions */
.actions {
  display: flex;
  justify-content: center;
}

.btn-create {
  padding: 12px 30px;
  background: #9b59b6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-create:hover:not(:disabled) {
  background: #8e44ad;
}

.btn-create:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Navigation */
.navigation {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 30px;
}

.btn-back {
  padding: 12px 30px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

.btn-back:hover {
  background: #7f8c8d;
}

.btn-next {
  padding: 12px 30px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}

.btn-next:hover {
  background: #27ae60;
}
</style>
