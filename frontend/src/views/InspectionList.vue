<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar"><el-button type="primary" :icon="Plus" @click="openEdit()">新增记录</el-button></div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="order_id" label="订单" width="150" />
      <el-table-column prop="inspection_date" label="检验日期" width="110" />
      <el-table-column prop="inspector" label="检验员" width="100" />
      <el-table-column prop="company" label="检验机构" width="150" />
      <el-table-column prop="result" label="结果" width="90">
        <template #default="{row}"><el-tag :type="inspectTag(row.result)" size="small">{{ row.result }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="ai_anomalies" label="AI异常" width="80"><template #default="{row}"><el-badge v-if="row.ai_anomalies?.length" :value="row.ai_anomalies.length" type="danger" /></template></el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{row}">
          <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
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
          <el-col :span="12"><el-form-item label="检验日期"><el-date-picker v-model="form.inspection_date" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="检验员"><el-input v-model="form.inspector" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="检验机构"><el-input v-model="form.company" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="结果"><el-select v-model="form.result"><el-option v-for="s in inspStatus" :key="s" :label="s" :value="s" /></el-select></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="缺陷描述"><el-input v-model="form.defects" type="textarea" :rows="3" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
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
import { createAPI } from '@/api'
import { ElMessage } from 'element-plus'

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('inspections')
const api = createAPI('inspections')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const inspStatus = ['pending','passed','failed','rework']
const form = reactive({ order_id:'', inspection_date:'', inspector:'', company:'', result:'pending', defects:'', notes:'' })

function inspectTag(r) { const m={pending:'info',passed:'success',failed:'danger',rework:'warning'}; return m[r]||'' }
function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k] = k==='result'?'pending':''); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
onMounted(fetchList)
</script>
