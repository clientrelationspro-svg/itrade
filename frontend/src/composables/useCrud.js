import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createAPI } from '@/api'

export function useCrud(prefix) {
  const api = createAPI(prefix)
  const loading = ref(false)
  const list = ref([])
  const total = ref(0)
  const query = reactive({
    page: 1,
    pageSize: 20,
    keyword: '',
    status: '',
    dateFrom: '',
    dateTo: '',
    sortBy: 'created_at',
    sortOrder: 'desc',
  })

  async function fetchList() {
    loading.value = true
    try {
      const res = await api.list(query)
      list.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function doDelete(id, permanent = false) {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await api.delete(id, permanent)
    ElMessage.success('删除成功')
    await fetchList()
  }

  async function doRestore(id) {
    await api.restore(id)
    ElMessage.success('已还原')
    await fetchList()
  }

  async function doBatchDelete(ids) {
    await ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 条记录吗？`, '提示', { type: 'warning' })
    await api.batchDelete(ids)
    ElMessage.success('批量删除成功')
    await fetchList()
  }

  function onSearch() {
    query.page = 1
    fetchList()
  }

  function onReset() {
    query.keyword = ''
    query.status = ''
    query.dateFrom = ''
    query.dateTo = ''
    query.page = 1
    fetchList()
  }

  function onPageChange(page) {
    query.page = page
    fetchList()
  }

  function onSizeChange(size) {
    query.pageSize = size
    query.page = 1
    fetchList()
  }

  return {
    api, loading, list, total, query,
    fetchList, doDelete, doRestore, doBatchDelete,
    onSearch, onReset, onPageChange, onSizeChange,
  }
}
