<template>
  <div class="server-generator">
    <h2>Generate MCP Server</h2>
    <p class="description">
      Configure your API and select which tools to include
    </p>

    <div class="server-form">
      <!-- API Configuration -->
      <div class="config-section">
        <h3>API Configuration</h3>
        <div class="form-group">
          <label>API Name:</label>
          <input
            v-model="apiName"
            type="text"
            placeholder="e.g., my-api"
          />
          <small>Used to identify your API</small>
        </div>
        <div class="form-group">
          <label>Base URL:</label>
          <input
            v-model="baseUrl"
            type="text"
            placeholder="e.g., https://api.example.com"
          />
          <small>The base URL for your API</small>
        </div>
      </div>

      <!-- Server Configuration -->
      <div class="config-section">
        <h3>Server Configuration</h3>
        <div class="form-group">
          <label>Server Name:</label>
          <input
            v-model="serverName"
            type="text"
            placeholder="e.g., my-api-mcp"
          />
          <small>Used for the folder and package name</small>
        </div>
      </div>

      <!-- Tool Selection -->
      <div class="config-section">
        <h3>Select Tools to Include</h3>
        
        <!-- Composite Tools -->
        <div v-if="store.compositeTools && store.compositeTools.length > 0" class="tool-section">
          <h4>Composite Tools ({{ store.compositeTools.length }})</h4>
          <div class="tool-selection">
            <label v-for="tool in store.compositeTools" :key="tool.name" class="tool-checkbox">
              <input
                type="checkbox"
                :value="tool.name"
                v-model="selectedCompositeTools"
              />
              <div class="tool-info">
                <span class="tool-name">{{ tool.name }}</span>
                <span class="badge composite">Composite</span>
                <p class="tool-desc">{{ tool.description }}</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Standard Tools -->
        <div v-if="store.endpoints && store.endpoints.length > 0" class="tool-section">
          <h4>Standard Tools ({{ store.endpoints.length }})</h4>
          <div class="tool-selection">
            <label v-for="endpoint in store.endpoints" :key="`${endpoint.path}:${endpoint.method}`" class="tool-checkbox">
              <input
                type="checkbox"
                :value="`${endpoint.path}:${endpoint.method}`"
                v-model="selectedStandardTools"
              />
              <div class="tool-info">
                <span class="tool-name">{{ getToolName(endpoint) }}</span>
                <span class="endpoint-badge">{{ endpoint.method.toUpperCase() }} {{ endpoint.path }}</span>
                <p class="tool-desc">{{ endpoint.enriched_description || endpoint.description || 'No description' }}</p>
              </div>
            </label>
          </div>
        </div>

        <div class="selection-actions">
          <button @click="selectAllTools" class="btn-secondary">Select All</button>
          <button @click="deselectAllTools" class="btn-secondary">Deselect All</button>
        </div>
      </div>

      <button
        @click="generateServer"
        class="btn-generate"
        :disabled="!canGenerate || generating"
      >
        {{ generating ? 'Generating...' : 'Generate Server Package' }}
      </button>
    </div>

    <div v-if="serverGenerated" class="success-message">
      <div class="success-icon">✅</div>
      <h3>Server Generated Successfully!</h3>
      <p>Your MCP server is ready to download</p>

      <button @click="downloadServer" class="btn-download">
        📦 Download Server Package
      </button>

      <div class="instructions">
        <h4>Next Steps:</h4>
        <ol>
          <li>Extract the downloaded ZIP file</li>
          <li>Navigate to the server directory</li>
          <li>Install dependencies: <code>pip install -e .</code></li>
          <li>Copy <code>.env.example</code> to <code>.env</code> and configure your API key</li>
          <li>Set <code>ANTHROPIC_API_KEY</code> if using composite tools</li>
          <li>Add the server to your Claude Desktop config</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const apiName = ref('')
const baseUrl = ref('')
const serverName = ref('')
const generating = ref(false)
const serverGenerated = ref(false)
const downloadUrl = ref('')

// Tool selection
const selectedCompositeTools = ref([])
const selectedStandardTools = ref([])

// Initialize with all tools selected
const initializeSelections = () => {
  if (store.compositeTools && store.compositeTools.length > 0) {
    selectedCompositeTools.value = store.compositeTools.map(t => t.name)
  }
  if (store.endpoints && store.endpoints.length > 0) {
    selectedStandardTools.value = store.endpoints.map(e => `${e.path}:${e.method}`)
  }
}

// Initialize on mount
onMounted(() => {
  initializeSelections()
})

// Watch for changes in store data
watch([() => store.compositeTools, () => store.endpoints], () => {
  if (selectedCompositeTools.value.length === 0 && selectedStandardTools.value.length === 0) {
    initializeSelections()
  }
})

const canGenerate = computed(() => {
  return apiName.value && 
         baseUrl.value && 
         serverName.value && 
         (selectedCompositeTools.value.length > 0 || selectedStandardTools.value.length > 0)
})

const getToolName = (endpoint) => {
  // Generate a tool name from the endpoint
  const pathParts = endpoint.path.split('/').filter(p => p && !p.startsWith('{'))
  const method = endpoint.method.toLowerCase()
  
  if (pathParts.length === 0) return method
  
  // Simple heuristic: listProducts, getProduct, createProduct, etc.
  if (method === 'get' && endpoint.path.includes('{')) {
    return `get${capitalize(pathParts[pathParts.length - 1])}`
  } else if (method === 'get') {
    return `list${capitalize(pathParts[pathParts.length - 1])}`
  } else if (method === 'post') {
    return `create${capitalize(pathParts[pathParts.length - 1])}`
  } else if (method === 'put') {
    return `update${capitalize(pathParts[pathParts.length - 1])}`
  } else if (method === 'delete') {
    return `delete${capitalize(pathParts[pathParts.length - 1])}`
  }
  
  return `${method}${capitalize(pathParts.join('_'))}`
}

const capitalize = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

const selectAllTools = () => {
  if (store.compositeTools) {
    selectedCompositeTools.value = store.compositeTools.map(t => t.name)
  }
  if (store.endpoints) {
    selectedStandardTools.value = store.endpoints.map(e => `${e.path}:${e.method}`)
  }
}

const deselectAllTools = () => {
  selectedCompositeTools.value = []
  selectedStandardTools.value = []
}

const generateServer = async () => {
  generating.value = true
  try {
    // First, generate tools with selected endpoints
    await store.generateTools(apiName.value, baseUrl.value)
    
    // Filter the tool model to only include selected tools
    const filteredToolModel = {
      ...store.toolModel,
      tools: store.toolModel.tools.filter(tool => {
        const endpoint = store.endpoints.find(e => 
          e.path === tool.endpoint_mapping.path && 
          e.method === tool.endpoint_mapping.method
        )
        if (endpoint) {
          return selectedStandardTools.value.includes(`${endpoint.path}:${endpoint.method}`)
        }
        return false
      }),
      composite_tools: (store.toolModel.composite_tools || []).filter(tool => 
        selectedCompositeTools.value.includes(tool.name)
      )
    }
    
    // Generate server with filtered tools
    const result = await store.generateServer(filteredToolModel, serverName.value)
    downloadUrl.value = result.download_url
    serverGenerated.value = true
  } catch (error) {
    console.error('Server generation failed:', error)
  } finally {
    generating.value = false
  }
}

const downloadServer = () => {
  store.downloadServer(serverName.value)
}
</script>

<style scoped>
.server-generator {
  padding: 20px;
}

h2 {
  margin-bottom: 10px;
  color: #2c3e50;
}

h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #2c3e50;
  font-size: 18px;
}

h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #34495e;
  font-size: 16px;
}

.description {
  color: #7f8c8d;
  margin-bottom: 30px;
}

.server-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 30px;
}

.config-section {
  background: white;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
}

.tool-section {
  margin-bottom: 20px;
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

.form-group small {
  display: block;
  margin-top: 5px;
  color: #7f8c8d;
  font-size: 12px;
}

.tool-selection {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 10px;
  background: #fafafa;
}

.tool-checkbox {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-checkbox:hover {
  border-color: #3498db;
  background: #f0f8ff;
}

.tool-checkbox input[type="checkbox"] {
  margin-top: 3px;
  margin-right: 12px;
  cursor: pointer;
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-weight: 600;
  color: #2c3e50;
  margin-right: 8px;
}

.tool-desc {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 13px;
  line-height: 1.4;
}

.badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.composite {
  background: #9b59b6;
  color: white;
}

.endpoint-badge {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  background: #ecf0f1;
  color: #34495e;
  margin-left: 8px;
}

.selection-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-secondary {
  padding: 8px 16px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-generate {
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
  width: 100%;
  cursor: pointer;
}

.btn-generate:hover:not(:disabled) {
  background: #2980b9;
}

.btn-generate:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.success-message {
  background: #d5f4e6;
  border: 2px solid #2ecc71;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.success-message h3 {
  color: #27ae60;
  margin-bottom: 10px;
}

.success-message p {
  color: #555;
  margin-bottom: 25px;
}

.btn-download {
  padding: 15px 30px;
  background: #2ecc71;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 30px;
}

.btn-download:hover {
  background: #27ae60;
}

.instructions {
  background: white;
  padding: 20px;
  border-radius: 6px;
  text-align: left;
  margin-top: 20px;
}

.instructions h4 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.instructions ol {
  margin-left: 20px;
  line-height: 2;
}

.instructions li {
  color: #555;
}

.instructions code {
  background: #f8f9fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 13px;
}
</style>
