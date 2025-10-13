<template>
  <div class="spec-uploader">
    <h2>Upload OpenAPI Specification</h2>
    <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        accept=".yaml,.yml,.json"
        style="display: none"
      />
      <div class="upload-content">
        <p class="upload-icon">📄</p>
        <p>Drag and drop your OpenAPI spec here</p>
        <p class="or">or</p>
        <button @click="$refs.fileInput.click()" class="btn-primary">
          Choose File
        </button>
      </div>
    </div>

    <div v-if="store.loading" class="loading">
      Parsing specification...
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useConverterStore } from '../stores/converter'

const store = useConverterStore()
const fileInput = ref(null)

const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadFile(file)
  }
}

const handleDrop = async (event) => {
  const file = event.dataTransfer.files[0]
  if (file) {
    await uploadFile(file)
  }
}

const uploadFile = async (file) => {
  try {
    await store.uploadSpec(file)
  } catch (error) {
    console.error('Upload failed:', error)
  }
}
</script>

<style scoped>
.spec-uploader {
  background: white;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

h2 {
  margin-bottom: 30px;
  color: #2c3e50;
}

.upload-area {
  border: 3px dashed #bdc3c7;
  border-radius: 8px;
  padding: 60px 40px;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #3498db;
  background: #ecf0f1;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.or {
  margin: 20px 0;
  color: #7f8c8d;
}

.btn-primary {
  padding: 12px 30px;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
}

.btn-primary:hover {
  background: #2980b9;
}

.loading {
  margin-top: 20px;
  padding: 15px;
  background: #3498db;
  color: white;
  border-radius: 4px;
}
</style>
