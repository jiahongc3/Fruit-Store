<script setup lang="ts">
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE } from '../config'

const props = defineProps<{
  initialMode?: 'login' | 'register'
}>()

const router = useRouter()
const globalState = inject<any>('globalState')
if (!globalState) {
  throw new Error('globalState not found')
}
const { handleLoginSuccess } = globalState

const isLoginMode = ref<boolean>(props.initialMode !== 'register')

const toggleMode = () => {
  isLoginMode.value = !isLoginMode.value
  router.push(isLoginMode.value ? '/login' : '/register')
}
const username = ref<string>('')
const password = ref<string>('')
const confirmPassword = ref<string>('')
const nickname = ref<string>('')

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

const handleLogin = async () => {
  if (!username.value || !password.value) return window.alert('請填寫帳號與密碼！')
  if (!emailRegex.test(username.value)) return window.alert('帳號格式不正確，請輸入正確的電子郵件！')
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    const result = await response.json()
    if (response.ok && result.success) {
      handleLoginSuccess(result.user)
    } else {
      window.alert(result.message || '帳號或密碼錯誤！')
    }
  } catch (error) {
    window.alert('後端連線失敗，請檢查 Flask 服務是否開啟')
  }
}

const handleRegister = async () => {
  if (!username.value || !password.value || !confirmPassword.value || !nickname.value) {
    return window.alert('所有欄位皆為必填！')
  }
  
  if (!emailRegex.test(username.value)) return window.alert('帳號必須是有效的電子郵件地址！')
  
  const nicknameRegex = /^[\u4e00-\u9fa5]{2,4}$/
  if (!nicknameRegex.test(nickname.value)) {
    return window.alert('會員名稱格式不正確！請輸入 2 至 4 個字的中文字，不能包含英文或數字。')
  }
  
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{8,}$/
  if (!passwordRegex.test(password.value)) return window.alert('密碼必須至少 8 個字，且必須包含英文與數字！')
  
  if (password.value !== confirmPassword.value) return window.alert('兩次輸入的密碼不一致！')

  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        username: username.value, 
        password: password.value,
        nickname: nickname.value
      })
    })
    const result = await response.json()
    if (response.ok && result.success) {
      window.alert('註冊成功！已切換回登入模式。')
      password.value = ''
      confirmPassword.value = ''
      nickname.value = ''
      isLoginMode.value = true
    } else {
      window.alert(result.message || '註冊失敗！')
    }
  } catch (error) {
    window.alert('與後端通訊時發生錯誤')
  }
}

const goBack = () => router.push('/')
</script>

<template>
  <div class="login-screen-container">
    <div class="fullscreen-bg"></div>
    
    <div class="center-content-box">
      <div class="brand-header">
        <h1 class="brand-title">線上水果行 <span class="brand-sub">(Online Fruit Shop)</span></h1>
      </div>

      <button class="login-back-btn" @click="goBack">
        <span class="arrow">←</span> 上一頁
      </button>

      <div class="modern-card">
        <h2 class="card-mode-title">{{ isLoginMode ? '歡迎回來 / MEMBER LOGIN' : '加入會員 / REGISTER' }}</h2>
        <div class="form-wrapper">
          <input v-if="!isLoginMode" v-model="nickname" type="text" placeholder="會員名稱 (例如: 陳小晴)" class="modern-input" />
          
          <input v-model="username" type="text" placeholder="電子郵件 / 帳號" class="modern-input" />
          <input v-model="password" type="password" placeholder="密碼" class="modern-input" />
          <input v-if="!isLoginMode" v-model="confirmPassword" type="password" placeholder="再次確認密碼" class="modern-input" />
          
          <div class="button-group">
            <button v-if="isLoginMode" @click="handleLogin" class="action-btn btn-green">登入系統</button>
            <button v-else @click="handleRegister" class="action-btn btn-emerald">建立新帳號</button>
            <button @click="toggleMode" class="action-btn btn-text">
              {{ isLoginMode ? '還沒有帳號？立即註冊' : '已有帳號？返回登入' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-back-btn {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.05);
  padding: 8px 20px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  color: #57534e;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
  margin-right: 600px;
}
.login-back-btn:hover {
  background: #ffffff;
  transform: translateX(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}
.login-back-btn .arrow {
  font-weight: 800;
}

.login-screen-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; z-index: 999; }
.fullscreen-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('../assets/fruit.png'); background-size: cover; background-position: center; background-repeat: no-repeat; z-index: 1; }
.center-content-box { position: relative; z-index: 10; display: flex; flex-direction: column; align-items: center; width: 100%; padding: 20px; transform: translateY(-20px); }
.brand-header { margin-bottom: -10px; text-align: center; }
.brand-title { font-size: 34px; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: 1.5px; text-shadow: 0 2px 10px rgba(255, 255, 255, 0.9); }
.brand-sub { font-size: 20px; font-weight: 400; color: #334155; }
.modern-card { width: 100%; max-width: 440px; background: rgba(255, 255, 255, 0.96); border-radius: 24px; padding: 45px 40px; box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.08); border: 1px solid rgba(226, 232, 240, 0.8); }
.card-mode-title { text-align: center; font-size: 16px; font-weight: 700; color: #94a3b8; letter-spacing: 1px; margin: 0 0 35px 0; }
.form-wrapper { display: flex; flex-direction: column; gap: 18px; }
.modern-input { width: 100%; padding: 14px 20px; border: 1px solid #cbd5e1; border-radius: 12px; font-size: 15px; color: #1e293b; background-color: #ffffff; outline: none; box-sizing: border-box; transition: all 0.25s ease; }
.modern-input:focus { border-color: #0b9b6a; box-shadow: 0 0 0 3px rgba(11, 155, 106, 0.1); }
.button-group { display: flex; flex-direction: column; gap: 12px; margin-top: 10px; }
.action-btn { width: 100%; padding: 14px; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; border: none; box-sizing: border-box; text-align: center; transition: all 0.2s ease; }
.btn-green { background-color: #0b9b6a; color: #ffffff; }
.btn-green:hover { background-color: #098259; box-shadow: 0 4px 12px rgba(9, 130, 89, 0.15); }
.btn-emerald { background-color: #10b981; color: #ffffff; }
.btn-text { background: transparent; color: #64748b; font-weight: 500; font-size: 14px; }
.btn-text:hover { color: #0b9b6a; text-decoration: underline; }
</style>