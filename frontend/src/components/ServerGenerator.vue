<template>
  <div class="server-generator">
    <h2>Generate MCP Server</h2>
    <p class="description">
      Create a complete, ready-to-use MCP server
    </p>

    <div class="server-form">
      <div class="form-group">
        <label>Server Name:</label>
        <input
          v-model="serverName"
          type="text"
          placeholder="e.g., my-api-mcp"
        />
        <small>Used for the folder and package name</small>
      </div>

      <button
        @click="generateServer"
        class="btn-generate"
        :disabled="!serverName || generating"
      >
        {{ generating ? 'Generating...' : 'Generate Server' }}
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
          <li>Add the server to your Claude Desktop config</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const serverName = ref('')
const generating = ref(false)
const serverGenerated = ref(false)
const downloadUrl = ref('')

const generateServer = async () => {
  generating.value = true
  try {
    const result = await store.generateServer(store.toolModel, serverName.value)
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
