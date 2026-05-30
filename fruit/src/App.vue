<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { Fruit } from './types'
import FruitStore from './components/FruitStore.vue'
import CartAndCheckout from './components/CartAndCheckout.vue'
import LoginView from './components/LoginView.vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000/api'

const currentView = ref<string>('store')
const fruits = ref<Fruit[]>([])
const currentUser = ref<any>(null)
const cartItems = ref<any[]>([])

const fetchFruitsFromBackend = async () => {
  try {
    const response = await fetch(`${API_BASE}/fruits`)
    const result = await response.json()
    if (result.success) {
      fruits.value = result.data
    }
  } catch (error) {
    console.error('無法連線至 Flask 後端:', error)
  }
}

// 🚀 核心監聽：只有在會員已登入時，購物車的任何加減變動才會自動發送給後端 SQLite 保存
watch([cartItems, currentUser], async () => {
  if (currentUser.value && currentUser.value.account) {
    try {
      await fetch(`${API_BASE}/cart/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: currentUser.value.account, // 對應後端接收的 account
          cartItems: cartItems.value
        })
      })
    } catch (error) {
      console.error('同步購物車至後端資料庫失敗:', error)
    }
  }
}, { deep: true })

// 🚀 初始化載入：開啟網頁時，從後端 SQLite 查詢是否有記住登入的會員
onMounted(async () => {
  await fetchFruitsFromBackend()

  try {
    const response = await fetch(`${API_BASE}/auth/auto-login`)
    const result = await response.json()
    
    if (result.success && result.user) {
      currentUser.value = result.user
      // 🌟 自動從後端資料庫中回復該會員上次過夜的水果紀錄
      cartItems.value = result.user.cart_items || []
      console.log(`✨ 後端自動登入成功：${result.user.username}`)
    } else {
      // 🌟 未登入訪客模式：重開網頁時購物車直接清空
      currentUser.value = null
      cartItems.value = []
    }
  } catch (error) {
    console.error('向後端檢查自動登入失敗:', error)
    cartItems.value = []
  }
})

// 登入成功
const handleLoginSuccess = (user: any) => {
  currentUser.value = user
  // 🌟 登入成功瞬間，立刻載入後端此會員專屬的購物車水果陣列
  cartItems.value = user.cart_items || []
  currentView.value = 'store'
}

// 登出系統
const handleLogout = async () => {
  if (currentUser.value) {
    try {
      // 通知後端將 SQLite 資料庫中的 is_remembered 改為 0
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: currentUser.value.account })
      })
    } catch (e) {
      console.error('發送登出請求失敗:', e)
    }
  }
  
  // 🌟 登出後一律將前端數據重置、購物車即時清空
  currentUser.value = null
  cartItems.value = []
  currentView.value = 'store'
}

// 加入購物車
const handleAddToCart = (fruit: any, quantity: number) => {
  const existingItem = cartItems.value.find(item => item.fruit_id === fruit.fruit_id)
  if (existingItem) {
    existingItem.quantity += quantity
  } else {
    cartItems.value.push({
      ...fruit,
      quantity: quantity
    })
  }
  window.alert(`成功將 ${quantity} 斤「${fruit.name}」加入購物車！`)
}

// 加減數量與完全移出購物車
const onUpdateQuantity = (fruitId: string, newQty: number) => {
  const index = cartItems.value.findIndex(i => i.fruit_id === fruitId)
  if (index !== -1) {
    if (newQty <= 0) {
      cartItems.value.splice(index, 1)
    } else {
      cartItems.value[index].quantity = newQty
    }
  }
}
</script>

<template>
  <div class="app-main-wrapper">
    
    <LoginView 
      v-if="currentView === 'login'"
      @login-success="handleLoginSuccess"
      @go-back="currentView = 'store'"
    />

    <template v-else>
      
      <FruitStore 
        v-if="currentView === 'store'" 
        :fruits="fruits" 
        :currentUser="currentUser"
        :cartItems="cartItems"
        @go-to-login="currentView = 'login'"
        @go-to-cart="currentView = 'cart'"
        @logout="handleLogout"
        @add-to-cart="handleAddToCart"
      />

      <CartAndCheckout 
        v-if="currentView === 'cart' || currentView === 'checkout'"
        :viewMode="currentView === 'cart' ? 'cart' : 'checkout'"
        :cartItems="cartItems"
        :currentUser="currentUser"
        @go-back="currentView = 'store'"
        @go-to-checkout="currentView = 'checkout'"
        @update-quantity="onUpdateQuantity" 
        @checkout-success="cartItems = []; currentView = 'store'; fetchFruitsFromBackend()"
      />
      
    </template>
  </div>
</template>

<style>
.app-main-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>