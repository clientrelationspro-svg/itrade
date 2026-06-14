<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <el-icon :size="24"><Platform /></el-icon>
        <span v-show="!isCollapse" class="logo-text">AI外贸平台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#1d1e2c"
        text-color="#a6a9b6"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>看板</span>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <span>客户管理</span>
        </el-menu-item>
        <el-menu-item index="/suppliers">
          <el-icon><OfficeBuilding /></el-icon>
          <span>供应商管理</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>产品管理</span>
        </el-menu-item>
        <el-menu-item index="/inquiries">
          <el-icon><ChatLineSquare /></el-icon>
          <span>询价管理</span>
        </el-menu-item>
        <el-menu-item index="/contracts">
          <el-icon><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><Tickets /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/inspections">
          <el-icon><Checked /></el-icon>
          <span>验货管理</span>
        </el-menu-item>
        <el-menu-item index="/shipments">
          <el-icon><Ship /></el-icon>
          <span>装运管理</span>
        </el-menu-item>
        <el-menu-item index="/payments">
          <el-icon><Money /></el-icon>
          <span>收付款管理</span>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><Folder /></el-icon>
          <span>文档管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main -->
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-button :icon="isCollapse ? Expand : Fold" text @click="isCollapse = !isCollapse" />
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-input
            v-model="searchQuery"
            :placeholder="searchPlaceholder"
            prefix-icon="Search"
            class="nl-search"
            @keyup.enter="doNLSearch"
          >
            <template #append>
              <el-button :icon="MagicStick" @click="doNLSearch" />
            </template>
          </el-input>
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span>{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/settings')">系统设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { aiAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const searchQuery = ref('')
const username = ref(localStorage.getItem('username') || 'Admin')

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '')
const searchPlaceholder = computed(() => "AI 自然语言搜索：如'找上次从川谷买的辣椒干'")

async function doNLSearch() {
  if (!searchQuery.value.trim()) return
  try {
    const result = await aiAPI.naturalSearch({ query: searchQuery.value })
    ElMessage.success(`AI 理解: ${result.parsed?.intent || '搜索完成'}`)
    // Navigate based on intent
    const intent = result.parsed?.intent
    if (intent?.includes('customer')) router.push('/customers')
    else if (intent?.includes('product')) router.push('/products')
    else if (intent?.includes('order')) router.push('/orders')
    // Store search params for the target page
    sessionStorage.setItem('nlSearchParams', JSON.stringify(result.parsed))
  } catch (e) {
    ElMessage.error('AI 搜索失败')
  }
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.layout-aside {
  background: #1d1e2c;
  overflow: hidden;
  transition: width 0.3s;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #409EFF;
  font-size: 16px;
  font-weight: 700;
  border-bottom: 1px solid #2d2e3c;
}
.logo-text {
  white-space: nowrap;
}
.layout-header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
  height: 60px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title {
  font-size: 16px;
  font-weight: 600;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.nl-search {
  width: 360px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.layout-main {
  background: #f0f2f5;
  overflow-y: auto;
}
</style>
