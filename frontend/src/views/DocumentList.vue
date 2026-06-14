<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索文件名..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <el-button type="primary" :icon="Plus" @click="showUpload = true">上传文档</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ai_category" label="AI分类" width="110">
        <template #default="{row}"><el-tag v-if="row.ai_category" size="small" type="success">{{ row.ai_category }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="related_module" label="关联模块" width="100" />
      <el-table-column prop="file_size" label="大小" width="90">
        <template #default="{row}">{{ formatSize(row.file_size) }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="160" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="viewDocument(row)">查看</el-button>
          <el-button link type="success" size="small" @click="classifyDocument(row)">AI分类</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <!-- Upload Dialog -->
    <el-dialog v-model="showUpload" title="上传文档" width="500px" destroy-on-close>
      <el-upload drag :auto-upload="false" :on-change="handleUpload" :show-file-list="true" accept="*" multiple>
        <el-icon :size="40"><UploadFilled /></el-icon>
        <p>拖拽文件到此处或点击上传</p>
        <p style="font-size:12px;color:#c0c4cc">支持 PDF、图片、Word、Excel 等格式</p>
      </el-upload>
      <div style="margin-top:16px;">
        <el-form label-width="80px">
          <el-form-item label="关联模块"><el-select v-model="uploadForm.related_module" placeholder="选择关联模块"><el-option v-for="m in modules" :key="m" :label="m" :value="m" /></el-select></el-form-item>
          <el-form-item label="标签"><el-input v-model="uploadForm.tags" placeholder="逗号分隔" /></el-form-item>
        </el-form>
      </div>
      <div v-if="uploading" style="text-align:center;padding:12px"><el-icon class="is-loading"><Loading /></el-icon> AI 分类识别中...</div>
      <template #footer>
        <el-button @click="showUpload=false">取消</el-button>
        <el-button type="primary" @click="doUpload" :loading="uploading">上传</el-button>
      </template>
    </el-dialog>

    <!-- View Document -->
    <el-dialog v-model="showView" title="文档详情" width="700px">
      <div v-if="viewDoc">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文件名">{{ viewDoc.filename }}</el-descriptions-item>
          <el-descriptions-item label="AI分类">{{ viewDoc.ai_category || '未分类' }}</el-descriptions-item>
          <el-descriptions-item label="关联模块">{{ viewDoc.related_module }}</el-descriptions-item>
          <el-descriptions-item label="文件大小">{{ formatSize(viewDoc.file_size) }}</el-descriptions-item>
          <el-descriptions-item label="上传时间" :span="2">{{ viewDoc.created_at }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="viewDoc.ocr_text" style="margin-top:16px">
          <h4>OCR 识别文本</h4>
          <div style="background:#f5f7fa;padding:12px;border-radius:6px;max-height:300px;overflow-y:auto;white-space:pre-wrap;font-size:13px">{{ viewDoc.ocr_text }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCrud } from '@/composables/useCrud'
import { createAPI, aiAPI } from '@/api'
import { ElMessage } from 'element-plus'

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('documents')
const api = createAPI('documents')
const showUpload = ref(false); const showView = ref(false); const viewDoc = ref(null)
const uploading = ref(false); const uploadFiles = ref([])
const uploadForm = reactive({ related_module: '', tags: '' })
const modules = ['customer','supplier','product','contract','order','inspection','shipment','payment']

function formatSize(bytes) { if (!bytes) return '-'; const units=['B','KB','MB','GB'];let i=0;while(bytes>=1024&&i<3){bytes/=1024;i++};return bytes.toFixed(1)+' '+units[i] }

async function handleUpload(file) { uploadFiles.value = [file] }
async function doUpload() {
  if (!uploadFiles.value.length) return
  uploading.value = true
  try {
    for (const f of uploadFiles.value) {
      const fd = new FormData(); fd.append('file', f.raw)
      // AI classify
      const classify = await aiAPI.documentClassify(fd)
      // OCR
      const ocrFd = new FormData(); ocrFd.append('file', f.raw); ocrFd.append('module','ocr_text')
      const ocrResult = await aiAPI.ocrExtract(ocrFd)

      await api.create({
        filename: f.name,
        category: classify.category,
        ai_category: classify.category,
        ai_confidence: classify.confidence,
        related_module: uploadForm.related_module,
        file_size: f.size,
        mime_type: f.raw?.type,
        ocr_text: ocrResult.text || ocrResult.raw?.choices?.[0]?.message?.content,
        tags: uploadForm.tags ? uploadForm.tags.split(',').map(t=>t.trim()) : [],
      })
    }
    ElMessage.success('上传完成')
    showUpload.value = false; uploadFiles.value = []
    fetchList()
  } catch { ElMessage.error('上传失败') }
  finally { uploading.value = false }
}

function viewDocument(row) { viewDoc.value = row; showView.value = true }
async function classifyDocument(row) {
  try {
    const r = await aiAPI.documentClassify({ file: null }) // needs file
    ElMessage.success(`AI分类: ${r.category}`)
  } catch { ElMessage.error('分类失败') }
}
onMounted(fetchList)
</script>
