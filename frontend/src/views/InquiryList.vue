<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索询价..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar">
      <el-button type="primary" :icon="Plus" @click="openEdit()">新增询价</el-button>
    </div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="customer_id" label="客户" width="150" />
      <el-table-column prop="product_id" label="产品" width="150" />
      <el-table-column prop="quantity" label="数量" width="100" />
      <el-table-column prop="unit" label="单位" width="70" />
      <el-table-column prop="target_price" label="目标价" width="120" />
      <el-table-column prop="currency" label="币种" width="70" />
      <el-table-column prop="valid_until" label="有效期" width="110" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
          <el-button link type="success" size="small" @click="compareQuotes(row)">报价对比</el-button>
          <el-popconfirm title="确定删除？" @confirm="doDelete(row.id)"><template #reference><el-button link type="danger" size="small">删除</el-button></template></el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
    <div style="display:flex;justify-content:flex-end;margin-top:16px">
      <el-pagination v-model:current-page="query.page" v-model:page-size="query.pageSize" :total="total" :page-sizes="[20,50,100]" layout="total,sizes,prev,pager,next" @current-change="onPageChange" @size-change="onSizeChange" />
    </div>

    <el-dialog v-model="showEdit" :title="editingId?'编辑询价':'新增询价'" width="600px" destroy-on-close>
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="客户"><el-input v-model="form.customer_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="产品"><el-input v-model="form.product_id" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="数量"><el-input v-model="form.quantity" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item></el-col>
          <el-col :span="8"><el-form-item label="目标价"><el-input v-model="form.target_price" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="币种"><el-input v-model="form.currency" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="有效期"><el-date-picker v-model="form.valid_until" type="date" style="width:100%" /></el-form-item></el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showEdit=false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showCompare" title="AI 报价对比分析" width="700px">
      <div v-if="compareResult" style="white-space:pre-wrap;font-size:13px;line-height:1.8;color:#303133">{{ JSON.stringify(compareResult, null, 2) }}</div>
      <el-empty v-else description="分析中..." />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useCrud } from '@/composables/useCrud'
import { createAPI, aiAPI } from '@/api'
import { ElMessage } from 'element-plus'

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('inquiries')
const api = createAPI('inquiries')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const showCompare = ref(false); const compareResult = ref(null)
const form = reactive({ customer_id:'', product_id:'', quantity:'', unit:'', target_price:'', currency:'USD', supplier_quotes:[], valid_until:'' })

function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='supplier_quotes'?[]:(k==='currency'?'USD':'')); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function compareQuotes(row) {
  try {
    compareResult.value = await aiAPI.compareQuotes({ quotes: row.supplier_quotes || [] })
    showCompare.value = true
  } catch { ElMessage.error('分析失败') }
}
onMounted(fetchList)
</script>
