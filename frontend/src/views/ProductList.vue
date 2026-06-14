<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索产品名称/HS编码..." clearable style="width:260px" @clear="onSearch" @keyup.enter="onSearch" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width:120px" @change="onSearch">
        <el-option label="正常" value="active" /><el-option label="已删除" value="deleted" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <el-button type="primary" :icon="Plus" @click="openEdit()">新增产品</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column type="selection" width="50" />
      <el-table-column prop="code" label="编号" width="120" />
      <el-table-column prop="name" label="产品名称" min-width="160">
        <template #default="{row}"><el-link type="primary" @click="openEdit(row)">{{ row.name }}</el-link></template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="100" />
      <el-table-column prop="specification" label="规格" width="150" show-overflow-tooltip />
      <el-table-column prop="unit" label="单位" width="70" />
      <el-table-column prop="hs_code" label="HS编码" width="120" />
      <el-table-column prop="hs_code_recommended" label="AI推荐HS" width="120">
        <template #default="{row}"><el-tag v-if="row.hs_code_recommended" size="small" type="success">{{ row.hs_code_recommended }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="price_range" label="价格区间" width="120" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="success" size="small" @click="recommendHS(row)">AI推荐HS</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑产品':'新增产品'" width="700px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="产品名称" prop="name" required><el-input v-model="form.name" placeholder="必填" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="英文名称" prop="name_en"><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="分类" prop="category"><el-input v-model="form.category" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="单位" prop="unit"><el-input v-model="form.unit" placeholder="如: 个、kg、件" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="HS编码" prop="hs_code"><el-input v-model="form.hs_code" placeholder="可选" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="MOQ" prop="moq"><el-input v-model="form.moq" placeholder="最小起订量" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="价格区间" prop="price_range"><el-input v-model="form.price_range" placeholder="如: $10-15/kg" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="规格描述" prop="specification"><el-input v-model="form.specification" type="textarea" :rows="3" placeholder="详细规格描述" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注" prop="notes"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
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
            <p>上传产品图片/规格书/目录，AI 自动提取并填充</p>
            <p style="font-size:12px;color:#c0c4cc">Qwen3-VL 视觉模型</p>
          </el-upload>
          <div v-if="aiLoading" style="text-align:center;padding:12px">
            <el-icon class="is-loading"><Loading /></el-icon> AI 识别中...
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCrud } from '@/composables/useCrud'
import { createAPI, aiAPI } from '@/api'
import { ElMessage } from 'element-plus'
import { MagicStick, UploadFilled, Loading } from '@element-plus/icons-vue'

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('products')
const api = createAPI('products')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false); const aiLoading = ref(false)
const formRef = ref(null)
const form = reactive({ name:'', name_en:'', category:'', specification:'', unit:'', hs_code:'', hs_code_recommended:'', supplier_id:'', moq:'', price_range:'', notes:'', images:[] })

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '产品名称长度应在 2-100 个字符', trigger: 'blur' }
  ],
  unit: [
    { max: 20, message: '单位长度不能超过 20 个字符', trigger: 'blur' }
  ],
  hs_code: [
    { pattern: /^\d{0,10}$/, message: 'HS编码应为数字（最多10位）', trigger: 'blur' }
  ],
  moq: [
    { pattern: /^\d*\.?\d*$/, message: 'MOQ应为数字', trigger: 'blur' }
  ],
}

function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='images'?[]:''); showEdit.value = true }
async function save() {
  saving.value = true
  
  // 先进行表单验证
  try {
    await formRef.value.validate()
  } catch (validationError) {
    saving.value = false
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  try {
    console.log('Saving product:', form)
    
    // 准备提交的数据，转换字段类型
    const submitData = { ...form }
    
    // 转换 moq 为数字（如果是字符串）
    if (submitData.moq && typeof submitData.moq === 'string') {
      submitData.moq = parseFloat(submitData.moq) || null
    }
    
    // 确保 images 是数组
    if (!submitData.images) {
      submitData.images = []
    }
    
    console.log('Submit data:', submitData)
    
    if (editingId.value) {
      const result = await api.update(editingId.value, submitData)
      console.log('Update result:', result)
    } else {
      const result = await api.create(submitData)
      console.log('Create result:', result)
    }
    ElMessage.success('保存成功')
    showEdit.value = false
    fetchList()
  } catch (error) {
    console.error('Save failed:', error)
    const errorMsg = error.response?.data?.detail || error.message || '未知错误'
    ElMessage.error('保存失败: ' + errorMsg)
  } finally {
    saving.value = false
  }
}
async function recommendHS(row) {
  try {
    const r = await aiAPI.hsRecommend({ product_name: row.name, description: row.specification || '' })
    if (r.hs_code) {
      row.hs_code_recommended = r.hs_code
      await api.update(row.id, { hs_code_recommended: r.hs_code })
      ElMessage.success(`AI推荐HS编码: ${r.hs_code} - ${r.chapter || ''}`)
    }
  } catch { ElMessage.error('推荐失败') }
}
async function handleAIUpload(file) {
  aiLoading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file.raw)
    fd.append('module', 'product')
    const result = await aiAPI.ocrExtract(fd)
    if (result) {
      const r = result
      if (r['产品名称']) form.name = r['产品名称'] || ''
      if (r['规格']) form.specification = r['规格'] || ''
      if (r['型号']) form.specification = form.specification + ' ' + (r['型号'] || '')
      if (r['HS编码']) form.hs_code = r['HS编码'] || ''
      if (r['单位']) form.unit = r['单位'] || ''
      if (r['单价范围']) form.price_range = r['单价范围'] || ''
      ElMessage.success('AI 识别完成，请核对并确认')
    }
  } catch (e) {
    ElMessage.error('AI 识别失败')
  } finally {
    aiLoading.value = false
  }
}
onMounted(fetchList)
</script>
