<template>
  <div class="page-container">
    <h2 style="margin-bottom:20px">业务看板</h2>
    <!-- Stats Cards -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon :size="32" :color="stat.color"><component :is="stat.icon" /></el-icon>
            <div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="16" style="margin-bottom:20px">
      <el-col :span="16">
        <el-card>
          <template #header>订单趋势</template>
          <v-chart :option="orderTrendOption" style="height:300px" autoresize />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>AI 预警</template>
          <div v-if="alerts.length" class="alerts">
            <div v-for="(a, i) in alerts" :key="i" class="alert-item" :class="a.level">
              <el-icon><WarningFilled /></el-icon>
              <span>{{ a.message }}</span>
            </div>
          </div>
          <el-empty v-else description="暂无预警" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>近期订单</template>
          <el-table :data="recentOrders" style="width:100%" size="small">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="customer" label="客户" />
            <el-table-column prop="amount" label="金额" />
            <el-table-column prop="status" label="状态">
              <template #default="{row}">
                <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>客户分布</template>
          <v-chart :option="customerDistOption" style="height:280px" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const stats = ref([
  { label: '总订单', value: '156', icon: 'Tickets', color: '#409EFF' },
  { label: '待发货', value: '12', icon: 'Ship', color: '#E6A23C' },
  { label: '逾期收款', value: '3', icon: 'Money', color: '#F56C6C' },
  { label: '本月营收', value: '$285K', icon: 'TrendCharts', color: '#67C23A' },
])

const alerts = ref([
  { level: 'high', message: '订单 ORD-001 交货期临近，请确认生产进度' },
  { level: 'medium', message: '客户 ABC Corp 信用评级下调至中等' },
  { level: 'info', message: '合同 CTR-005 即将到期，请关注续签' },
])

const recentOrders = ref([
  { order_no: 'ORD-2026001', customer: 'ABC Corp', amount: '$45,000', status: '生产中' },
  { order_no: 'ORD-2026002', customer: 'XYZ Ltd', amount: '$32,000', status: '已完成' },
  { order_no: 'ORD-2026003', customer: 'Global Trade', amount: '$78,000', status: '待发货' },
])

const orderTrendOption = reactive({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
  yAxis: { type: 'value' },
  series: [
    { name: '订单数', type: 'bar', data: [20, 25, 22, 30, 28, 31], itemStyle: { color: '#409EFF' }, barGap: '30%' },
    { name: '营收(万$)', type: 'line', data: [15, 18, 16, 22, 20, 28], itemStyle: { color: '#67C23A' } },
    { name: '收款(万$)', type: 'line', data: [12, 15, 14, 18, 17, 25], itemStyle: { color: '#E6A23C' } },
  ],
})

const customerDistOption = reactive({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: ['45%', '75%'],
    data: [
      { value: 45, name: '美国' },
      { value: 30, name: '欧盟' },
      { value: 15, name: '东南亚' },
      { value: 10, name: '其他' },
    ],
  }],
})

function statusTag(status) {
  const map = { '生产中': 'warning', '已完成': 'success', '待发货': '', '已取消': 'danger' }
  return map[status] || 'info'
}
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}
.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}
.alerts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
}
.alert-item.high { background: #fef0f0; color: #F56C6C; }
.alert-item.medium { background: #fdf6ec; color: #E6A23C; }
.alert-item.info { background: #ecf5ff; color: #409EFF; }
</style>
