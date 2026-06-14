<template>
  <div class="page-container">
    <!-- Search Bar -->
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索客户名称/邮箱/电话..." clearable
        style="width:260px" @clear="onSearch" @keyup.enter="onSearch" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width:120px" @change="onSearch">
        <el-option label="正常" value="active" />
        <el-option label="已删除" value="deleted" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>

    <!-- Toolbar -->
    <div class="table-toolbar">
      <div style="display:flex;gap:8px">
        <el-button type="primary" :icon="Plus" @click="openEdit()">新增客户</el-button>
        <el-button :icon="Upload" @click="showImport = true">导入Excel</el-button>
        <el-button :icon="Download">导出</el-button>
        <el-button v-if="selectedIds.length" type="danger" :icon="Delete" @click="batchDelete">批量删除</el-button>
      </div>
      <el-button v-if="query.status==='deleted'" type="info" @click="query.status='';onSearch()">
        返回列表
      </el-button>
    </div>

    <!-- Table -->
    <el-table :data="list" v-loading="loading" stripe @selection-change="(val) => selectedIds = val.map(v=>v.id)"
      style="width:100%">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="code" label="客户编号" width="140" />
      <el-table-column prop="name" label="客户名称" min-width="160">
        <template #default="{row}">
          <el-link type="primary" @click="openEdit(row)">{{ row.name }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="country" label="国家" width="100" />
      <el-table-column prop="contact_person" label="联系人" width="100" />
      <el-table-column prop="email" label="邮箱" width="160" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="credit_rating" label="信用评级" width="100">
        <template #default="{row}">
          <el-tag :type="creditTag(row.credit_rating)" size="small">{{ row.credit_rating || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button v-if="query.status!=='deleted'" link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="query.status==='deleted'" link type="success" size="small" @click="doRestore(row.id)">还原</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)">
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize"
        :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next"
        @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <!-- Edit Dialog -->
    <el-dialog v-model="showEdit" :title="editingId ? '编辑客户' : '新增客户'" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="客户名称" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="英文名称" prop="name_en">
              <el-input v-model="form.name_en" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="国家" prop="country">
              <el-input v-model="form.country" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人" prop="contact_person">
              <el-input v-model="form.contact_person" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="form.email" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话" prop="phone">
              <el-input v-model="form.phone" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="地址" prop="address">
              <el-input v-model="form.address" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="税号" prop="tax_id">
              <el-input v-model="form.tax_id" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="备注" prop="notes">
              <el-input v-model="form.notes" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- AI Smart Fill -->
        <div class="ai-panel">
          <div class="ai-panel__title">
            <el-icon color="#409EFF"><MagicStick /></el-icon>
            AI 智能识别填充
          </div>
          <el-upload drag :auto-upload="false" :on-change="handleAIUpload" :show-file-list="false"
            accept="image/*,.pdf">
            <el-icon :size="40"><UploadFilled /></el-icon>
            <p>上传客户名片/营业执照/合同文件，AI 自动提取并填充</p>
            <p style="font-size:12px;color:#c0c4cc">Qwen2.5-VL-72B 视觉模型</p>
          </el-upload>
          <div v-if="aiLoading" style="text-align:center;padding:12px">
            <el-icon class="is-loading"><Loading /></el-icon> AI 识别中...
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        <el-button v-if="!editingId" type="success" :loading="saving" @click="saveAndNew">保存并新增</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCrud } from '@/composables/useCrud'
import { aiAPI, createAPI } from '@/api'
import { ElMessage } from 'element-plus'

const { loading, list, total, query, fetchList, doDelete, doRestore, onSearch, onReset, onPageChange, onSizeChange } = useCrud('customers')
const api = createAPI('customers')

const showEdit = ref(false)
const editingId = ref(null)
const saving = ref(false)
const selectedIds = ref([])
const aiLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  name: '', name_en: '', country: '', contact_person: '',
  email: '', phone: '', address: '', tax_id: '', notes: '', tags: [],
})

const rules = {
  name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

function openEdit(row) {
  editingId.value = row?.id || null
  if (row) {
    Object.assign(form, row)
  } else {
    Object.keys(form).forEach(k => form[k] = '')
    form.tags = []
  }
  showEdit.value = true
}

async function save() {
  saving.value = true
  try {
    if (editingId.value) {
      await api.update(editingId.value, form)
    } else {
      await api.create(form)
    }
    ElMessage.success('保存成功')
    showEdit.value = false
    fetchList()
  } finally {
    saving.value = false
  }
}

async function saveAndNew() {
  saving.value = true
  try {
    await api.create(form)
    ElMessage.success('保存成功')
    Object.keys(form).forEach(k => form[k] = '')
    form.tags = []
  } finally {
    saving.value = false
  }
}

async function handleAIUpload(file) {
  aiLoading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.raw)
    fd.append('module', 'customer')
    const result = await aiAPI.ocrExtract(fd)
    // Try to parse result and fill form
    if (result) {
      const r = result
      if (r['公司名称']) form.name = r['公司名称'] || r.name || ''
      if (r['联系人']) form.contact_person = r['联系人'] || r.contact_person || ''
      if (r['邮箱']) form.email = r['邮箱'] || r.email || ''
      if (r['电话']) form.phone = r['电话'] || r.phone || ''
      if (r['地址']) form.address = r['地址'] || r.address || ''
      if (r['税号']) form.tax_id = r['税号'] || r.tax_id || ''
      if (r['国家']) form.country = r['国家'] || r.country || ''
      ElMessage.success('AI 识别完成，请核对并确认')
    }
  } catch (e) {
    ElMessage.error('AI 识别失败')
  } finally {
    aiLoading.value = false
  }
}

async function batchDelete() {
  if (!selectedIds.value.length) return
  await api.batchDelete(selectedIds.value)
  ElMessage.success('批量删除成功')
  selectedIds.value = []
  fetchList()
}

function creditTag(rating) {
  const map = { low: 'success', medium: 'warning', high: 'danger', critical: 'danger' }
  return map[rating] || 'info'
}

onMounted(fetchList)
</script>
