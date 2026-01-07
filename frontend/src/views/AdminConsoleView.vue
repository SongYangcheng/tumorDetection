<template>
  <div class="admin container">
    <h2>系统管理后台</h2>
    <div class="grid">
      <div class="panel card">
        <h3>用户与角色管理</h3>
        <div class="form">
          <input v-model="user.username" placeholder="用户名" />
          <select v-model="user.role">
            <option value="doctor">医生</option>
            <option value="researcher">研究员</option>
            <option value="admin">管理员</option>
          </select>
          <button class="btn btn-primary" @click="createUser">创建</button>
        </div>
        <ul class="list">
          <li v-for="u in users" :key="u.id">{{ u.username }} - {{ u.role }}</li>
        </ul>
        <div v-if="message" class="message">{{ message }}</div>
        <div v-if="error" class="error">{{ error }}</div>
      </div>
      <div class="panel card">
        <h3>模型运维</h3>
        <div>当前版本: {{ model.version }}</div>
        <button class="btn" @click="updateModel">更新模型</button>
        <div>性能: {{ model.performance }}</div>
      </div>
      <div class="panel card">
        <h3>系统监控</h3>
        <div>服务器: {{ monitor.serverStatus }}</div>
        <div>存储: {{ monitor.storageUsage }}%</div>
        <div>API请求: {{ monitor.apiCalls }}</div>
        <div class="ops">
          <button class="btn" @click="backup">数据备份</button>
          <button class="btn" @click="refreshMonitor">刷新监控</button>
        </div>
        <div v-if="message2" class="message">{{ message2 }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import type { UserSummary } from '@/services/api'

const user = ref<{ username: string; role: 'doctor' | 'researcher' | 'admin' }>({
  username: '',
  role: 'doctor',
})
const users = ref<UserSummary[]>([])
const model = ref({ version: 'v0', performance: '未知' })
const monitor = ref({ serverStatus: '未知', storageUsage: 0, apiCalls: 0 })
const message = ref('')
const message2 = ref('')
const error = ref('')

const createUser = async () => {
  try {
    await api.createUser(user.value)
    users.value = await api.listUsers()
    message.value = '用户已创建'
    error.value = ''
  } catch (e: any) {
    error.value = e?.message || '创建失败'
  }
}
const updateModel = async () => {
  try {
    model.value = await api.updateModel()
    message.value = '模型已更新'
  } catch (e: any) {
    error.value = e?.message || '更新失败'
  }
}
const backup = async () => {
  try {
    await api.backupData()
    message2.value = '已开始备份'
  } catch (e: any) {
    error.value = e?.message || '备份失败'
  }
}
const refreshMonitor = async () => {
  monitor.value = await api.getSystemMonitor()
}

onMounted(async () => {
  users.value = await api.listUsers()
  monitor.value = await api.getSystemMonitor()
  model.value = await api.getModelInfo()
})
</script>

<style scoped>
.admin {
  max-width: 1100px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
.panel {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  background: var(--card);
}
.form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list li {
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  color: var(--muted);
}
.ops {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.message {
  margin-top: 8px;
  color: #22c55e;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid #86efac;
  padding: 8px 12px;
  border-radius: 8px;
}
.error {
  margin-top: 8px;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid #fecaca;
  padding: 8px 12px;
  border-radius: 8px;
}
</style>
