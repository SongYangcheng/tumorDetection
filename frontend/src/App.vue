<template>
  <div id="app" class="layout-shell" :class="{ 'no-sidebar': !showSidebar }">
    <aside v-if="showSidebar" class="sidebar card">
      <div class="brand">
        <div class="brand-badge">AI</div>
        <div class="brand-text">
          <div class="title">NeuroVision</div>
          <div class="subtitle">Tumor Planning</div>
        </div>
      </div>
      <nav class="side-menu">
        <router-link v-if="isLoggedIn" to="/dashboard" class="side-link">总览</router-link>
        <router-link v-if="isLoggedIn" to="/data" class="side-link">数据管理</router-link>
        <router-link v-if="isLoggedIn" to="/workbench" class="side-link">处理与分割</router-link>
        <router-link v-if="isLoggedIn" to="/analysis-report" class="side-link">分析报告</router-link>
        <router-link v-if="isLoggedIn" to="/preop" class="side-link">术前规划</router-link>
        <router-link v-if="isLoggedIn" to="/radiomics" class="side-link">影像组学</router-link>
        <router-link v-if="isLoggedIn" to="/profile" class="side-link">个人资料</router-link>
      </nav>
      <div v-if="isLoggedIn" class="sidebar-footer">
        <button class="btn ghost" @click="handleLogout">退出</button>
      </div>
    </aside>

    <main class="main">
      <header v-if="showSidebar" class="topbar">
        <div class="crumb">{{ route.meta?.title || '智能术前决策平台' }}</div>
        <div class="top-actions">
          <ThemeToggle />
          <router-link class="chip" to="/dashboard">实时总览</router-link>
          <router-link class="chip" to="/data">数据</router-link>
          <div class="status-dot">
            <span class="pulse" />
            <span>在线</span>
          </div>
        </div>
      </header>
      <section class="page-body">
        <router-view />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 使用 Pinia store 的认证状态
const isLoggedIn = computed(() => userStore.isAuthenticated)

// Determine if sidebar should be shown
const showSidebar = computed(() => {
  // Hide sidebar on welcome, login, register pages
  const hideOnRoutes = ['welcome', 'login', 'register', 'forgotPassword']
  return !hideOnRoutes.includes(route.name as string) && isLoggedIn.value
})

// 处理退出登录
const handleLogout = (e: Event) => {
  e.preventDefault()
  userStore.logout()
  router.push('/')
}

// 应用初始化时检查认证状态
onMounted(() => {
  userStore.checkAuthStatus()
})

// 监听路由变化更新认证状态
router.afterEach(() => {
  userStore.checkAuthStatus()
})
</script>

<style>
#app {
  color: var(--text);
}

.layout-shell {
  background: transparent;
}

.sidebar {
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: sticky;
  top: 0;
  min-height: 100vh;
  border-right: 1px solid var(--border);
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 6px 10px;
}

.brand-badge {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2563eb, #38bdf8);
  display: grid;
  place-items: center;
  font-weight: 800;
  letter-spacing: 0.02em;
  color: #ffffff;
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.35);
}

.brand-text .title {
  font-size: 16px;
  font-weight: 800;
}

.brand-text .subtitle {
  color: var(--text-muted);
  font-size: 13px;
}

.brand-text .title {
  color: var(--text);
  transition: var(--transition-theme);
}

.side-menu {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.side-link {
  padding: 10px 12px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-muted);
  border: 1px solid transparent;
  transition: all 0.2s ease;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.side-link:hover {
  color: var(--text);
  border-color: var(--border-hover);
  background: var(--btn-bg);
}

.side-link.router-link-exact-active {
  color: var(--text);
  border-color: var(--primary);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(56, 189, 248, 0.18));
}

.sidebar-footer {
  margin-top: auto;
}

.btn.ghost {
  width: 100%;
  background: var(--btn-bg);
  transition: var(--transition-theme);
}

.btn.ghost:hover {
  background: var(--btn-bg-hover);
}

.main {
  padding: 28px;
  min-height: 100vh;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding: 14px 18px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--panel);
  box-shadow: var(--shadow);
  transition: var(--transition-theme);
}

.crumb {
  font-weight: 700;
  letter-spacing: 0.01em;
  color: var(--text);
  transition: var(--transition-theme);
}

.top-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chip {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  color: var(--text-muted);
  text-decoration: none;
  transition: all 0.2s ease;
}

.chip:hover {
  color: var(--text);
  border-color: var(--border-hover);
  background: var(--btn-bg-hover);
}

.status-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
}

.status-dot .pulse {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.14);
}

.page-body {
  width: 100%;
}

@media (max-width: 900px) {
  .sidebar {
    position: fixed;
    inset: 0 0 auto 0;
    transform: translateY(-100%);
  }

  .layout-shell.no-sidebar {
    display: block;
  }

  .topbar {
    position: sticky;
    top: 0;
    z-index: 2;
  }
}
</style>
