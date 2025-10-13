import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

export const useConverterStore = defineStore('converter', {
  state: () => ({
    currentSpec: null,
    specId: null,
    endpoints: [],
    enrichments: {},
    compositeTools: [],
    toolModel: null,
    loading: false,
    error: null
  }),

  actions: {
    async uploadSpec(file) {
      this.loading = true
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await axios.post(`${API_BASE}/upload-spec`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })

        this.currentSpec = response.data
        this.specId = file.name
        this.endpoints = response.data.endpoints

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to upload spec'
        throw error
      } finally {
        this.loading = false
      }
    },

    async enrichEndpoint(endpoint, userContext) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(
          `${API_BASE}/enrich-endpoint?spec_id=${this.specId}`,
          {
            endpoint_path: endpoint.path,
            endpoint_method: endpoint.method,
            user_context: userContext
          }
        )

        const key = `${endpoint.path}:${endpoint.method}`
        this.enrichments[key] = response.data

        // Update the endpoint in the list
        const idx = this.endpoints.findIndex(
          ep => ep.path === endpoint.path && ep.method === endpoint.method
        )
        if (idx !== -1) {
          this.endpoints[idx].enriched_description = response.data.enriched_description
          this.endpoints[idx].business_context = response.data.business_context
          this.endpoints[idx].needs_enrichment = false
        }

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to enrich endpoint'
        throw error
      } finally {
        this.loading = false
      }
    },

    async suggestTools() {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(
          `${API_BASE}/suggest-tools?spec_id=${this.specId}`
        )
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to get suggestions'
        throw error
      } finally {
        this.loading = false
      }
    },

    async createCompositeTool(useCaseDescription, selectedEndpoints) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(
          `${API_BASE}/create-composite-tool?spec_id=${this.specId}`,
          {
            use_case_description: useCaseDescription,
            selected_endpoints: selectedEndpoints
          }
        )

        // Add to composite tools array
        this.compositeTools.push(response.data)
        
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create composite tool'
        throw error
      } finally {
        this.loading = false
      }
    },

    async loadCompositeTools() {
      this.loading = true
      this.error = null

      try {
        const response = await axios.get(
          `${API_BASE}/composite-tools?spec_id=${this.specId}`
        )
        this.compositeTools = response.data.composite_tools || []
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to load composite tools'
        throw error
      } finally {
        this.loading = false
      }
    },

    async generateTools(apiName, baseUrl) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(
          `${API_BASE}/generate-tools?spec_id=${this.specId}&api_name=${apiName}&base_url=${baseUrl}`
        )

        this.toolModel = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to generate tools'
        throw error
      } finally {
        this.loading = false
      }
    },

    async generateServer(toolModel, serverName) {
      this.loading = true
      this.error = null

      try {
        const response = await axios.post(
          `${API_BASE}/generate-server`,
          {
            tool_model: toolModel,
            server_name: serverName
          }
        )

        return response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to generate server'
        throw error
      } finally {
        this.loading = false
      }
    },

    downloadServer(serverName) {
      window.open(`${API_BASE}/download-server/${serverName}`, '_blank')
    },

    reset() {
      this.currentSpec = null
      this.specId = null
      this.endpoints = []
      this.enrichments = {}
      this.compositeTools = []
      this.toolModel = null
      this.error = null
    }
  }
})
