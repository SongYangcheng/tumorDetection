import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import WelcomeView from '../views/WelcomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import DataManagerView from '../views/DataManagerView.vue'
import WorkbenchView from '../views/WorkbenchView.vue'
import PreOpPlanningView from '../views/PreOpPlanningView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import ForgotPasswordView from '../views/ForgotPasswordView.vue'
import YoloDetectionView from '../views/YoloDetectionView.vue'
import VideoDetectionView from '../views/VideoDetectionView.vue'
import AnalysisReportView from '../views/AnalysisReportView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView,
      meta: { title: 'NeuroVision - 脑肿瘤检测系统' },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true, title: '系统总览' },
    },
    {
      path: '/data',
      name: 'data',
      component: DataManagerView,
      meta: { requiresAuth: true, title: '病例管理' },
    },
    {
      path: '/workbench',
      name: 'workbench',
      component: WorkbenchView,
      meta: { requiresAuth: true, title: '检测工作台' },
    },
    {
      path: '/yolo-detection/:imageId',
      name: 'yoloDetection',
      component: YoloDetectionView,
      meta: { requiresAuth: true, title: '检测结果' },
    },
    {
      path: '/video-detection',
      name: 'videoDetection',
      component: VideoDetectionView,
      meta: { requiresAuth: true, title: '视频检测' },
    },
    {
      path: '/analysis-report',
      name: 'analysisReport',
      component: AnalysisReportView,
      meta: { requiresAuth: true, title: '分析报告' },
    },
    {
      path: '/preop/:imageId?',
      name: 'preop',
      component: PreOpPlanningView,
      meta: { requiresAuth: true, title: '术前规划' },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: '登录' },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { title: '注册账户' },
    },
    {
      path: '/forgot-password',
      name: 'forgotPassword',
      component: ForgotPasswordView,
      meta: { title: '重置密码' },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true, title: '个人资料' },
    },
    // 影像组学指向视频检测页面
    {
      path: '/radiomics',
      redirect: '/video-detection',
      meta: { requiresAuth: true },
    },
    // 分析报告不再作为独立菜单项，通过工作台跳转
    {
      path: '/analysis',
      redirect: '/data',
      meta: { requiresAuth: true },
    },
  ],
})

// 路由守卫：检查认证状态
router.beforeEach((to, from, next) => {
  // 使用 Pinia store 获取认证状态
  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isAuthenticated = userStore.isAuthenticated

  // 调试日志（仅在开发环境）
  if (import.meta.env.DEV) {
    console.log(`[路由导航] ${from.path} → ${to.path}`, {
      requiresAuth,
      isAuthenticated,
    })
  }

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - NeuroVision`
  }

  // 如果路由需要认证但用户未登录
  if (requiresAuth && !isAuthenticated) {
    if (import.meta.env.DEV) {
      console.log(`[重定向] 受保护页面需要认证，重定向到登录`)
    }
    next({
      path: '/login',
      query: { redirect: to.fullPath }, // 保存目标路径，登录后可跳转回来
    })
  }
  // 如果用户已登录但想访问登录/注册页面
  else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    // 特殊处理：确保不会陷入无限循环
    if (from.path === '/login' || from.path === '/register') {
      // 已经在登录页，允许导航以避免循环
      next()
    } else {
      // 用户已登录但访问登录页，重定向到仪表盘
      if (import.meta.env.DEV) {
        console.log(`[重定向] 已认证用户访问登录页，重定向到仪表盘`)
      }
      next('/dashboard')
    }
  }
  // 其他情况正常导航
  else {
    if (import.meta.env.DEV) {
      console.log(`[允许] 允许导航`)
    }
    next()
  }
})

// 路由完成后的处理
router.afterEach((to) => {
  if (import.meta.env.DEV) {
    console.log(`[完成] 路由导航完成: ${to.path}`)
  }
})

export default router
