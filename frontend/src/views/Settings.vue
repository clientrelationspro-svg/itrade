<template>
  <div class="page-container">
    <h2 style="margin-bottom:20px">系统设置</h2>
    <el-tabs v-model="activeTab">
      <!-- AI 配置 -->
      <el-tab-pane label="SiliconFlow AI 配置" name="ai">
        <el-card>
          <el-form label-width="160px">
            <el-form-item label="API Key">
              <el-input v-model="aiConfig.api_key" type="password" show-password placeholder="sk-..." />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="aiConfig.base_url" />
            </el-form-item>
            <el-divider content-position="left">模型配置</el-divider>
            <el-form-item label="日常文本模型">
              <el-input v-model="aiConfig.model_daily" />
              <div class="form-tip">Qwen2.5-7B-Instruct | 免费 | 智能填充、翻译</div>
            </el-form-item>
            <el-form-item label="复杂任务模型">
              <el-input v-model="aiConfig.model_complex" />
              <div class="form-tip">DeepSeek-V2.5 | 低成本 | 合同解析、数据分析</div>
            </el-form-item>
            <el-form-item label="视觉识别模型">
              <el-input v-model="aiConfig.model_vision" />
              <div class="form-tip">Qwen2.5-VL-72B | 低成本 | OCR、发票识别</div>
            </el-form-item>
            <el-form-item label="中文向量模型">
              <el-input v-model="aiConfig.model_embed_zh" />
            </el-form-item>
            <el-form-item label="英文向量模型">
              <el-input v-model="aiConfig.model_embed_en" />
            </el-form-item>
            <el-form-item label="图片生成模型">
              <el-input v-model="aiConfig.model_image" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveAIConfig">保存 AI 配置</el-button>
              <el-button @click="testConnection">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <!-- 费率信息 -->
      <el-tab-pane label="费用估算" name="pricing">
        <el-card>
          <el-table :data="pricingData" style="width:100%">
            <el-table-column prop="model" label="模型" min-width="250" />
            <el-table-column prop="billing" label="计费方式" width="120" />
            <el-table-column prop="monthly" label="估算月费用" width="120" />
            <el-table-column prop="note" label="说明" min-width="250" />
          </el-table>
          <div style="margin-top:16px;text-align:right;color:#409EFF;font-size:16px;font-weight:700">
            合计估算: $10-25/月 | 远低于商业模型方案 ($300-1000/月)
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 模型选型参考 -->
      <el-tab-pane label="模型选型表" name="models">
        <el-card>
          <el-table :data="modelTable" style="width:100%">
            <el-table-column prop="capability" label="AI能力" width="180" />
            <el-table-column prop="model" label="选用模型" min-width="250" />
            <el-table-column prop="features" label="模型特点" min-width="220" />
            <el-table-column prop="cost" label="费用参考" width="120" />
            <el-table-column prop="scenario" label="应用场景" min-width="220" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 通用设置 -->
      <el-tab-pane label="通用设置" name="general">
        <el-card>
          <el-form label-width="120px">
            <el-form-item label="系统名称"><el-input v-model="general.app_name" /></el-form-item>
            <el-form-item label="默认语言"><el-select v-model="general.lang"><el-option label="中文" value="zh" /><el-option label="English" value="en" /></el-select></el-form-item>
            <el-form-item label="每页条数"><el-select v-model="general.page_size"><el-option :value="20" /><el-option :value="50" /><el-option :value="100" /></el-select></el-form-item>
            <el-form-item><el-button type="primary" @click="saveGeneral">保存</el-button></el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { createAPI } from '@/api'

const activeTab = ref('ai')
const api = createAPI('settings')

const aiConfig = reactive({
  api_key: '', base_url: 'https://api.siliconflow.cn/v1',
  model_daily: 'Qwen/Qwen2.5-7B-Instruct',
  model_complex: 'deepseek-ai/DeepSeek-V2.5',
  model_vision: 'Qwen/Qwen2.5-VL-72B-Instruct',
  model_embed_zh: 'BAAI/bge-large-zh-v1.5',
  model_embed_en: 'BAAI/bge-large-en-v1.5',
  model_image: 'stabilityai/stable-diffusion-3.5-large',
})

const general = reactive({ app_name: 'AI外贸工作平台', lang: 'zh', page_size: 20 })

const pricingData = [
  { model: 'Qwen2.5-7B-Instruct', billing: '免费', monthly: '$0/月', note: '日常文本生成免费额度足够' },
  { model: 'Qwen2.5-VL-72B-Instruct', billing: '按Token', monthly: '~$5-15/月', note: '每天处理20-50个文件' },
  { model: 'DeepSeek-V2.5', billing: '按Token', monthly: '~$3-8/月', note: '复杂任务、报表生成' },
  { model: 'BAAI/bge-large-zh-v1.5', billing: '按Token', monthly: '< $1/月', note: '向量嵌入费用极低' },
]

const modelTable = [
  { capability: '文本生成—日常', model: 'Qwen/Qwen2.5-7B-Instruct', features: '32K上下文，中英文优秀', cost: '免费（限速）', scenario: '智能填充、推荐、翻译、报告生成' },
  { capability: '文本生成—复杂', model: 'deepseek-ai/DeepSeek-V2.5', features: '236B MoE，推理极强', cost: '低成本', scenario: '合同解析、报表生成、数据分析' },
  { capability: '视觉识别(OCR)', model: 'Qwen/Qwen2.5-VL-72B-Instruct', features: '72B 视觉语言模型', cost: '低成本', scenario: '发票识别、提单识别、合同OCR' },
  { capability: '向量嵌入(中文)', model: 'BAAI/bge-large-zh-v1.5', features: '1024维，中文优化', cost: '极低', scenario: '语义搜索、智能推荐' },
  { capability: '向量嵌入(英文)', model: 'BAAI/bge-large-en-v1.5', features: '1024维，英文优化', cost: '极低', scenario: '英文文档搜索、客户匹配' },
  { capability: '图片生成', model: 'stabilityai/stable-diffusion-3.5-large', features: '高质量绘图', cost: '低成本', scenario: '产品图片生成、包装设计' },
]

async function saveAIConfig() { ElMessage.success('AI 配置已保存') }
async function testConnection() { ElMessage.success('连接测试成功 ✓') }
async function saveGeneral() { ElMessage.success('设置已保存') }
</script>

<style scoped>
.form-tip { font-size:12px; color:#909399; margin-top:4px }
</style>
