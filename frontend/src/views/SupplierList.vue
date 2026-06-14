<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索供应商..." clearable style="width:260px" @clear="onSearch" @keyup.enter="onSearch" />
      <el-select v-model="query.status" placeholder="状态" clearable style="width:120px" @change="onSearch">
        <el-option label="正常" value="active" /><el-option label="已删除" value="deleted" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <div style="display:flex;gap:8px">
        <el-button type="primary" :icon="Plus" @click="openEdit()">新增供应商</el-button>
        <el-button :icon="Upload">导入Excel</el-button>
      </div>
    </div>
    <el-table :data="list" v-loading="loading" stripe @selection-change="(v)=>sel=v.map(x=>x.id)">
      <el-table-column type="selection" width="50" />
      <el-table-column prop="code" label="编号" width="120" />
      <el-table-column prop="name" label="供应商名称" min-width="160">
        <template #default="{row}"><el-link type="primary" @click="openEdit(row)">{{ row.name }}</el-link></template>
      </el-table-column>
      <el-table-column prop="country" label="国家" width="100" />
      <el-table-column prop="contact_person" label="联系人" width="100" />
      <el-table-column prop="email" label="邮箱" width="160" />
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="rating" label="评分" width="80">
        <template #default="{row}"><el-rate v-model="row.rating" disabled size="small" /></template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑供应商':'新增供应商'" width="700px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="英文名"><el-input v-model="form.name_en" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="国家"><el-input v-model="form.country" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="联系人"><el-input v-model="form.contact_person" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="地址"><el-input v-model="form.address" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="工厂地址"><el-input v-model="form.factory_address" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="主营产品"><el-input v-model="form.main_products" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
        <div class="ai-panel">
          <div class="ai-panel__title"><el-icon color="#409EFF"><MagicStick /></el-icon>AI 智能识别</div>
          <el-upload drag :auto-upload="false" :on-change="handleAIUpload" :show-file-list="false" accept="image/*,.pdf">
            <el-icon :size="40"><UploadFilled /></el-icon><p>上传供应商资料，AI 自动提取</p>
          </el-upload>
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

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('suppliers')
const api = createAPI('suppliers')
const sel = ref([])
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const form = reactive({ name:'', name_en:'', country:'', contact_person:'', email:'', phone:'', address:'', factory_address:'', main_products:'', notes:'', certifications:[], rating:3, tags:[] })

function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='certifications'||k==='tags' ? [] : (k==='rating'?3:'')); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function handleAIUpload(f) { try { const fd=new FormData(); fd.append('file',f.raw); fd.append('module','supplier'); const r=await aiAPI.ocrExtract(fd); if(r){ form.name=r['公司名称']||r.name||form.name; form.contact_person=r['联系人']||r.contact_person||form.contact_person; form.email=r['邮箱']||r.email||form.email; form.phone=r['电话']||r.phone||form.phone; form.address=r['地址']||r.address||form.address; ElMessage.success('AI识别完成') } } catch { ElMessage.error('AI识别失败') } }
onMounted(fetchList)
</script>
