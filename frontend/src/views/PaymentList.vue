<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar"><el-button type="primary" :icon="Plus" @click="openEdit()">新增收款记录</el-button></div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="order_id" label="订单" width="140" />
      <el-table-column prop="receivable" label="应收" width="120" />
      <el-table-column prop="received" label="已收" width="120" />
      <el-table-column prop="outstanding" label="未收" width="120" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{row}"><el-tag :type="payStatusTag(row.status)" size="small">{{ row.status }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="due_date" label="应付日期" width="110" />
      <el-table-column prop="payment_method" label="付款方式" width="120" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="success" size="small" @click="assessCredit(row)">信用评估</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑':'新增'" width="600px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="订单"><el-input v-model="form.order_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="付款方式"><el-input v-model="form.payment_method" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="应收"><el-input v-model="form.receivable" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="已收"><el-input v-model="form.received" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="未收"><el-input v-model="form.outstanding" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="应付日期"><el-date-picker v-model="form.due_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="到账日期"><el-date-picker v-model="form.received_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="银行信息"><el-input v-model="form.bank_info" type="textarea" :rows="2" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status"><el-option v-for="s in pStatus" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCredit" title="AI 信用评估" width="600px">
      <div v-if="creditResult" class="risk-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="信用评分">{{ creditResult.credit_score }}</el-descriptions-item>
          <el-descriptions-item label="信用评级">
            <el-tag :type="riskTag(creditResult.credit_rating)">{{ creditResult.credit_rating }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px"><h4>建议付款条款</h4><p>{{ creditResult.recommended_terms }}</p></div>
        <div style="margin-top:16px"><h4>收款预测</h4><p>{{ creditResult.payment_prediction }}</p></div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCrud } from '@/composables/useCrud'
import { createAPI, aiAPI } from '@/api'
import { ElMessage } from 'element-plus'

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('payments')
const api = createAPI('payments')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const showCredit = ref(false); const creditResult = ref(null)
const pStatus = ['unpaid','partial','paid','overdue']
const form = reactive({ order_id:'',receivable:'',received:'',outstanding:'',due_date:'',received_date:'',payment_method:'',bank_info:'',status:'unpaid',notes:[] })

function payStatusTag(s) { const m={unpaid:'info',partial:'warning',paid:'success',overdue:'danger'}; return m[s]||'' }
function riskTag(r) { const m={low:'success',medium:'warning',high:'danger',critical:'danger'}; return m[r]||'' }
function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='notes'?[]:(k==='status'?'unpaid':'')); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function assessCredit(row) { try { creditResult.value = await aiAPI.creditAssess({ customer_id: row.id }); showCredit.value = true } catch { ElMessage.error('评估失败') } }
onMounted(fetchList)
</script>
