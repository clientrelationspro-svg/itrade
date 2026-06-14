import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '看板', icon: 'DataAnalysis' },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/CustomerList.vue'),
        meta: { title: '客户管理', icon: 'User' },
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/SupplierList.vue'),
        meta: { title: '供应商管理', icon: 'OfficeBuilding' },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/ProductList.vue'),
        meta: { title: '产品管理', icon: 'Goods' },
      },
      {
        path: 'inquiries',
        name: 'Inquiries',
        component: () => import('@/views/InquiryList.vue'),
        meta: { title: '询价管理', icon: 'ChatLineSquare' },
      },
      {
        path: 'contracts',
        name: 'Contracts',
        component: () => import('@/views/ContractList.vue'),
        meta: { title: '合同管理', icon: 'Document' },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/OrderList.vue'),
        meta: { title: '订单管理', icon: 'Tickets' },
      },
      {
        path: 'inspections',
        name: 'Inspections',
        component: () => import('@/views/InspectionList.vue'),
        meta: { title: '验货管理', icon: 'Checked' },
      },
      {
        path: 'shipments',
        name: 'Shipments',
        component: () => import('@/views/ShipmentList.vue'),
        meta: { title: '装运管理', icon: 'Ship' },
      },
      {
        path: 'payments',
        name: 'Payments',
        component: () => import('@/views/PaymentList.vue'),
        meta: { title: '收付款管理', icon: 'Money' },
      },
      {
        path: 'documents',
        name: 'Documents',
        component: () => import('@/views/DocumentList.vue'),
        meta: { title: '文档管理', icon: 'Folder' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
