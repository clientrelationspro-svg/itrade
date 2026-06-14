<template>
  <div>
    <!-- 调试横幅：显示当前 API 地址和构建版本 -->
    <div v-if="showDebug" class="debug-banner">
      🔧 构建: {{ buildTime }} | API: {{ apiUrl }} | 
      <a :href="apiUrl + '/docs'" target="_blank" style="color:white;text-decoration:underline">API文档</a>
      | <a :href="testUrl" target="_blank" style="color:white;text-decoration:underline">连接测试</a>
      | <a :href="apiUrl" target="_blank" style="color:white;text-decoration:underline">后端根路径</a>
      <button @click="testConnection" style="margin-left:10px;cursor:pointer">测试连接</button>
      <span v-if="testResult" style="margin-left:8px">{{ testResult }}</span>
    </div>
    <router-view />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const showDebug = ref(true)
const buildTime = '__BUILD_TIME__'
const apiUrl = 'https://ai-trade-platform-api.onrender.com/api'
const testUrl = window.location.origin + '/test-api.html'
const testResult = ref('')

async function testConnection() {
  testResult.value = '测试中...'
  try {
    const resp = await fetch(apiUrl + '/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'test', password: 'test' })
    })
    if (resp.ok || resp.status === 401) {
      testResult.value = '✅ 连接成功 (' + resp.status + ')'
    } else {
      testResult.value = '❌ 状态码: ' + resp.status
    }
  } catch (e) {
    testResult.value = '❌ 连接失败: ' + e.message
  }
}

onMounted(() => {
  console.log('[App] 版本: ' + buildTime, '| API:', apiUrl)
})
</script>

<style>
.debug-banner {
  background: #1a1a2e;
  color: #00ff88;
  padding: 6px 16px;
  font-size: 12px;
  font-family: monospace;
  text-align: center;
  border-bottom: 1px solid #333;
  position: sticky;
  top: 0;
  z-index: 9999;
}
.debug-banner button {
  background: #00ff88;
  color: #1a1a2e;
  border: none;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}
</style>
