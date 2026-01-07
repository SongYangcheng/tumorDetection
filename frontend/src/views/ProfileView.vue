<template>
  <div class="profile container">
    <div class="page-header">
      <div>
        <p class="eyebrow">Account</p>
        <h2>个人资料</h2>
        <p class="muted">查看账户信息并管理安全设置</p>
      </div>
    </div>

    <div v-if="loading" class="state">加载中...</div>
    <div v-else-if="error" class="state error">{{ error }}</div>
    <div v-else-if="userProfile" class="profile-grid">
      <div class="card panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">用户信息</p>
            <h3>基本信息</h3>
          </div>
          <span class="pill">{{ userProfile.is_admin ? '管理员' : '普通用户' }}</span>
        </div>
        <div class="info-list">
          <div class="info-row">
            <span class="label">用户名</span>
            <span class="value">{{ userProfile.username }}</span>
          </div>
          <div class="info-row">
            <span class="label">邮箱</span>
            <span class="value">{{ userProfile.email || '—' }}</span>
          </div>
          <div class="info-row">
            <span class="label">注册时间</span>
            <span class="value">{{ formatDate(userProfile.created_at) }}</span>
          </div>
          <div class="info-row">
            <span class="label">角色</span>
            <span class="value">{{ userProfile.is_admin ? '管理员' : '普通用户' }}</span>
          </div>
        </div>
      </div>

      <div class="card panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">Security</p>
            <h3>修改密码</h3>
          </div>
        </div>
        <form class="form" @submit.prevent="handleChangePassword">
          <label class="field">
            <span>原密码</span>
            <input id="oldPassword" v-model="passwordForm.oldPassword" type="password" required placeholder="输入原密码" />
          </label>
          <label class="field">
            <span>新密码</span>
            <input id="newPassword" v-model="passwordForm.newPassword" type="password" required placeholder="至少 6 位" />
          </label>
          <label class="field">
            <span>确认新密码</span>
            <input id="confirmNewPassword" v-model="confirmNewPassword" type="password" required
              placeholder="再次输入新密码" />
          </label>
          <button type="submit" :disabled="changingPassword" class="btn btn-primary submit">
            {{ changingPassword ? '修改中...' : '修改密码' }}
          </button>
        </form>
        <p v-if="passwordError" class="status error">{{ passwordError }}</p>
        <p v-if="passwordSuccess" class="status success">{{ passwordSuccess }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 从store获取用户信息
const userProfile = computed(() => userStore.user)
const loading = ref(false)
const error = ref('')
const changingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
})

const confirmNewPassword = ref('')

const fetchProfile = async () => {
  try {
    loading.value = true
    error.value = ''

    await userStore.fetchProfile()
  } catch (err: any) {
    error.value = err.message || '获取用户信息失败'
  } finally {
    loading.value = false
  }
}

const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''

  // 验证密码确认
  if (passwordForm.value.newPassword !== confirmNewPassword.value) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }

  // 验证密码长度
  if (passwordForm.value.newPassword.length < 6) {
    passwordError.value = '新密码长度不能少于6位'
    return
  }

  changingPassword.value = true

  try {
    await userStore.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    )

    passwordSuccess.value = '密码修改成功！'

    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
    }
    confirmNewPassword.value = ''
  } catch (err: any) {
    passwordError.value = err.message || '修改密码失败'
  } finally {
    changingPassword.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  // 如果store中已有用户信息，直接使用
  if (userStore.user) {
    loading.value = false
  } else {
    // 否则从服务器获取
    fetchProfile()
  }
})
</script>

<style scoped>
.profile {
  padding-top: 10px;
  padding-bottom: 32px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 18px;
}

.eyebrow {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin: 0;
}

.page-header h2 {
  margin: 6px 0 6px;
  color: #fff;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
}

.panel {
  padding: 18px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.panel h3 {
  margin: 4px 0;
  color: #fff;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
  font-weight: 700;
  font-size: 12px;
}

.info-list {
  display: grid;
  gap: 10px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
}

.label {
  color: var(--text-muted);
  font-size: 13px;
}

.value {
  color: #fff;
  font-weight: 700;
}

.form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
  color: var(--text);
  font-size: 14px;
}

.field input {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text);
}

.field input:focus {
  outline: none;
  border-color: rgba(56, 189, 248, 0.6);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

.submit {
  width: 100%;
  height: 44px;
  font-weight: 700;
}

.submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.state {
  text-align: center;
  color: var(--text-muted);
}

.status {
  margin-top: 8px;
  font-size: 13px;
  text-align: center;
}

.status.success {
  color: #34d399;
}

.status.error,
.state.error {
  color: #fca5a5;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 6px;
  }
}
</style>
