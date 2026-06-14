<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索合同号/标题..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <el-button type="primary" :icon="Plus" @click="openEdit()">新增合同</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="contract_no" label="合同号" width="150" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="amount" label="金额" width="120" />
      <el-table-column prop="currency" label="币种" width="70" />
      <el-table-column prop="sign_date" label="签订日期" width="110" />
      <el-table-column prop="expiry_date" label="截止日期" width="110" />
      <el-table-column prop="risk_level" label="风险" width="80">
        <template #default="{row}"><el-tag v-if="row.risk_level" :type="riskTag(row.risk_level)" size="small">{{ row.risk_level }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="success" size="small" @click="parseContract(row)">AI解析</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑合同':'新增合同'" width="750px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="合同号" required><el-input v-model="form.contract_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="标题" required><el-input v-model="form.title" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="客户"><el-input v-model="form.customer_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="供应商"><el-input v-model="form.supplier_id" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="金额"><el-input v-model="form.amount" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="币种"><el-input v-model="form.currency" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="签订日期"><el-date-picker v-model="form.sign_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="到期日"><el-date-picker v-model="form.expiry_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="交货日期"><el-date-picker v-model="form.delivery_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="关键条款"><el-input v-model="form.key_terms" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="付款条款"><el-input v-model="form.payment_terms" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
        <div class="ai-panel">
          <div class="ai-panel__title"><el-icon color="#409EFF"><MagicStick /></el-icon>AI 合同解析</div>
          <el-upload drag :auto-upload="false" :on-change="handleContractUpload" :show-file-list="false" accept="image/*,.pdf">
            <el-icon :size="40"><UploadFilled /></el-icon><p>上传合同文件，AI 智能解析关键条款</p>
            <p style="font-size:12px;color:#c0c4cc">DeepSeek-V2.5 复杂推理模型</p>
          </el-upload>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showParse" title="AI 合同解析结果" width="700px">
      <div v-if="parseResult" style="font-size:13px">
        <el-descriptions v-if="parseResult.parties" :column="2" border>
          <el-descriptions-item v-for="(v,k) in parseResult.parties" :key="k" :label="k">{{ v }}</el-descriptions-item>
        </el-descriptions>
        <div v-if="parseResult.risk_flags" style="margin-top:16px">
          <h4>风险提示</h4>
          <el-tag v-for="(f,i) in parseResult.risk_flags" :key="i" type="danger" style="margin:4px">{{ f }}</el-tag>
        </div>
        <div v-if="parseResult.key_clauses" style="margin-top:16px">
          <h4>关键条款</h4>
          <ul><li v-for="(c,i) in parseResult.key_clauses" :key="i">{{ c }}</li></ul>
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

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('contracts')
const api = createAPI('contracts')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const showParse = ref(false); const parseResult = ref(null)
const form = reactive({ contract_no:'',title:'',customer_id:'',supplier_id:'',amount:'',currency:'USD',sign_date:'',expiry_date:'',delivery_date:'',key_terms:'',payment_terms:'',attachments:[],notes:'' })

function riskTag(r) { const m={low:'success',medium:'warning',high:'danger',critical:'danger'}; return m[r]||'' }
function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='attachments'?[]:(k==='currency'?'USD':'')); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function parseContract(row) { try { parseResult.value = await aiAPI.contractParse(row.key_terms || ''); showParse.value = true } catch { ElMessage.error('解析失败') } }
async function handleContractUpload(f) { try { const fd=new FormData(); fd.append('file',f.raw); const r=await aiAPI.contractParseFile(fd); if(r){ form.title=r.title||form.title; form.amount=r.amount||form.amount; form.key_terms=r.raw_text||''; ElMessage.success('AI解析完成') } } catch { ElMessage.error('AI解析失败') } }
onMounted(fetchList)
</script>
