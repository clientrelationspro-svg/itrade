<template>
  <div class="page-container">
    <div class="search-bar">
      <el-input v-model="query.keyword" placeholder="搜索船名/提单号..." clearable style="width:260px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" @click="onSearch">搜索</el-button>
      <el-button :icon="Refresh" @click="onReset">重置</el-button>
    </div>
    <div class="table-toolbar"><el-button type="primary" :icon="Plus" @click="openEdit()">新增装运</el-button></div>
    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="order_id" label="订单" width="140" />
      <el-table-column prop="vessel_name" label="船名" width="140" />
      <el-table-column prop="voyage_no" label="航次" width="100" />
      <el-table-column prop="bl_no" label="提单号" width="140" />
      <el-table-column prop="container_no" label="集装箱号" width="160" />
      <el-table-column prop="etd" label="ETD" width="110" />
      <el-table-column prop="eta" label="ETA" width="110" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{row}"><el-tag :type="shipStatusTag(row.status)" size="small">{{ row.status }}</el-tag></template>
      </el-table-column>
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

    <el-dialog v-model="showEdit" :title="editingId?'编辑装运':'新增装运'" width="700px" destroy-on-close>
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12"><el-form-item label="订单"><el-input v-model="form.order_id" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="船名"><el-input v-model="form.vessel_name" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="航次"><el-input v-model="form.voyage_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="提单号"><el-input v-model="form.bl_no" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="集装箱号"><el-input v-model="form.container_no" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="ETD"><el-date-picker v-model="form.etd" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="6"><el-form-item label="ETA"><el-date-picker v-model="form.eta" type="date" style="width:100%" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="装货港"><el-input v-model="form.port_of_loading" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="卸货港"><el-input v-model="form.port_of_discharge" /></el-form-item></el-col>
          <el-col :span="24"><el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item></el-col>
        </el-row>
        <div class="ai-panel">
          <div class="ai-panel__title"><el-icon color="#409EFF"><MagicStick /></el-icon>AI 单据识别</div>
          <el-upload drag :auto-upload="false" :on-change="handleAIUpload" :show-file-list="false" accept="image/*,.pdf">
            <el-icon :size="40"><UploadFilled /></el-icon><p>上传提单/发票，AI自动提取关键信息</p>
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

const { loading, list, total, query, fetchList, doDelete, onSearch, onReset, onPageChange, onSizeChange } = useCrud('shipments')
const api = createAPI('shipments')
const showEdit = ref(false); const editingId = ref(null); const saving = ref(false)
const form = reactive({ order_id:'',vessel_name:'',voyage_no:'',container_no:'',bl_no:'',etd:'',eta:'',port_of_loading:'',port_of_discharge:'',notes:'' })

function shipStatusTag(s) { const m={pending:'info',loaded:'',in_transit:'warning',arrived:'success',cleared:'success'}; return m[s]||'' }
function openEdit(row) { editingId.value = row?.id || null; if (row) Object.assign(form, row); else Object.keys(form).forEach(k => form[k]=''); showEdit.value = true }
async function save() { saving.value=true; try { editingId.value ? await api.update(editingId.value,form) : await api.create(form); ElMessage.success('保存成功'); showEdit.value=false; fetchList() } finally { saving.value=false } }
async function handleAIUpload(f) { try { const fd=new FormData(); fd.append('file',f.raw); fd.append('module','shipment'); const r=await aiAPI.ocrExtract(fd); if(r){ form.vessel_name=r['船名']||r.vessel_name||form.vessel_name; form.bl_no=r['提单号']||r.bl_no||form.bl_no; form.container_no=r['集装箱号']||r.container_no||form.container_no; ElMessage.success('AI识别完成') } } catch { ElMessage.error('AI识别失败') } }
onMounted(fetchList)
</script>
