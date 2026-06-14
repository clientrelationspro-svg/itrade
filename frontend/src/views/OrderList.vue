<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索订单号..." clearable style="width:240px" @clear="onSearch" @keyup.enter="onSearch" />
      <el-select v-model="query.status" placeholder="订单状态" clearable style="width:140px" @change="onSearch">
        <el-option v-for="s in statuses" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <el-button type="primary" :icon="Plus" @click="openEdit()">新增订单</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column type="selection" width="50" />
      <el-table-column prop="order_no" label="订单号" width="150" />
      <el-table-column prop="customer_id" label="客户" width="120" />
      <el-table-column prop="total_amount" label="金额" width="120" />
      <el-table-column prop="currency" label="币种" width="70" />
      <el-table-column prop="status" label="状态" width="110">
        <template #default="{row}"><el-tag :type="orderStatusTag(row.status)" size="small">{{ row.status }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="delivery_deadline" label="交货期" width="110" />
      <el-table-column prop="ai_risk_alert" label="风险" width="80">
        <template #default="{row}"><el-tag v-if="row.ai_risk_alert&&row.ai_risk_alert!=='low'" :type="riskTag(row.ai_risk_alert)" size="small">{{ row.ai_risk_alert }}</el-tag></template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="warning" size="small" @click="assessRisk(row)">风险评估</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑订单':'新增订单'" width="750px" destroy-on-close>
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="订单号"><el-input v-model="form.order_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="客户"><el-input v-model="form.customer_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="合同"><el-input v-model="form.contract_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="总金额"><el-input v-model="form.total_amount" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="币种"><el-input v-model="form.currency" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="状态"><el-select v-model="form.status"><el-option v-for="s in statuses" :key="s.value" :label="s.label" :value="s.value" /></el-select></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="生产截止"><el-date-picker v-model="form.production_deadline" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="发货截止"><el-date-picker v-model="form.shipping_deadline" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="交货截止"><el-date-picker v-model="form.delivery_deadline" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- Risk Assessment Dialog -->
    <el-dialog v-model="showRisk" title="AI 风险评估" width="600px">
      <div v-if="riskResult" class="risk-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="风险等级">
            <el-tag :type="riskTag(riskResult.risk_level)">{{ riskResult.risk_level }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="综合评分">{{ riskResult.overall_score }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top:16px">
          <h4>风险因素</h4>
          <ul><li v-for="(f,i) in riskResult.risk_factors" :key="i">{{ f }}</li></ul>
        </div>
        <div style="margin-top:16px">
          <h4>建议措施</h4>
          <ul><li v-for="(s,i) in riskResult.suggestions" :key="i">{{ s }}</li></ul>
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

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('orders')
const api = createAPI('orders')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const showRisk = ref(false); const riskResult = ref(null)
const form = reactive({ order_no:'', customer_id:'', contract_id:'', total_amount:'', currency:'USD', status:'draft', production_deadline:'', shipping_deadline:'', delivery_deadline:'', notes:'' })

const statuses = [
  { label: '草稿', value: 'draft' },{ label: '已确认', value: 'confirmed' },{ label: '生产中', value: 'in_production' },
  { label: '验货中', value: 'inspecting' },{ label: '运输中', value: 'shipping' },{ label: '已完成', value: 'completed' },{ label: '已取消', value: 'cancelled' },
]
function orderStatusTag(s) { const m={draft:'info',confirmed:'',in_production:'warning',inspecting:'warning',shipping:'',completed:'success',cancelled:'danger'}; return m[s]||'' }
function riskTag(r) { const m={low:'success',medium:'warning',high:'danger',critical:'danger'}; return m[r]||'' }

function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k]=k==='currency'?'USD':(k==='status'?'draft':'')); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function assessRisk(row) {
  try {
    riskResult.value = await aiAPI.orderRisk({ order_id: row.id })
    showRisk.value = true
    fetchList()
  } catch { ElMessage.error('评估失败') }
}
onMounted(fetchList)
</script>

<style scoped>
.risk-result h4 { margin-bottom:8px; color:#303133; font-size:14px }
.risk-result ul { padding-left:20px; color:#606266; font-size:13px; line-height:1.8 }
</style>
