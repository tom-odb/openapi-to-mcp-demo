<template>
  <div class="endpoint-list">
    <h2>Enrich Endpoints</h2>
    <p class="description">
      Review endpoints and add context to improve tool descriptions
    </p>

    <div class="endpoints">
      <div v-for="endpoint in store.endpoints" :key="endpoint.path + endpoint.method" class="endpoint-card">
        <div class="endpoint-header">
          <span class="method" :class="endpoint.method">{{ endpoint.method.toUpperCase() }}</span>
          <span class="path">{{ endpoint.path }}</span>
          <span v-if="endpoint.needs_enrichment" class="badge">Needs enrichment</span>
        </div>

        <div class="endpoint-body">
          <p v-if="endpoint.summary" class="summary">{{ endpoint.summary }}</p>
          <p v-if="endpoint.description" class="description-text">{{ endpoint.description }}</p>

          <div v-if="!endpoint.enriched_description" class="enrichment-form">
            <textarea
              v-model="contextInputs[endpoint.path + endpoint.method]"
              placeholder="Add business context or use case description..."
              rows="3"
            ></textarea>
            <button @click="enrichEndpoint(endpoint)" class="btn-enrich">
              Enrich with AI
            </button>
          </div>

          <div v-else class="enriched">
            <p><strong>Enriched Description:</strong></p>
            <p>{{ endpoint.enriched_description }}</p>
            <p v-if="endpoint.business_context"><strong>Business Context:</strong></p>
            <p v-if="endpoint.business_context">{{ endpoint.business_context }}</p>
          </div>
        </div>
      </div>
    </div>

    <button @click="$emit('next')" class="btn-next">
      Continue to Tool Generation
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const contextInputs = ref({})

defineEmits(['next'])

const enrichEndpoint = async (endpoint) => {
  const key = endpoint.path + endpoint.method
  const context = contextInputs.value[key] || ''

  try {
    await store.enrichEndpoint(endpoint, context)
    contextInputs.value[key] = ''
  } catch (error) {
    console.error('Enrichment failed:', error)
  }
}
</script>

<style scoped>
.endpoint-list {
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

.endpoints {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.endpoint-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.endpoint-header {
  background: #f8f9fa;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.method {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
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
  font-weight: 500;
}

.badge {
  margin-left: auto;
  padding: 4px 12px;
  background: #e74c3c;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.endpoint-body {
  padding: 15px;
}

.summary {
  font-weight: 500;
  margin-bottom: 10px;
}

.description-text {
  color: #7f8c8d;
  margin-bottom: 15px;
}

.enrichment-form {
  margin-top: 15px;
}

.enrichment-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 10px;
}

.btn-enrich {
  padding: 8px 16px;
  background: #9b59b6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
}

.btn-enrich:hover {
  background: #8e44ad;
}

.enriched {
  background: #d5f4e6;
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
}

.enriched p {
  margin-bottom: 10px;
}

.enriched p:last-child {
  margin-bottom: 0;
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
