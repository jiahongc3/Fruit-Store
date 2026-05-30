<script setup lang="ts">
import { ref, onMounted, watch, provide } from 'vue'
import router from './router'
import type { Fruit } from './types'
import { API_BASE } from './config'

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

// 核心監聽：同步購物車
watch([cartItems, currentUser], async () => {
  if (currentUser.value && currentUser.value.account) {
    try {
      await fetch(`${API_BASE}/cart/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: currentUser.value.account,
          cartItems: cartItems.value
        })
      })
    } catch (error) {
      console.error('同步購物車至後端資料庫失敗:', error)
    }
  }
}, { deep: true })

onMounted(async () => {
  await fetchFruitsFromBackend()
  try {
    const response = await fetch(`${API_BASE}/auth/auto-login`)
    const result = await response.json()
    if (result.success && result.user) {
      currentUser.value = result.user
      cartItems.value = result.user.cart_items || []
    } else {
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
  cartItems.value = user.cart_items || []
  router.push('/')
}

// 登出系統
const handleLogout = async () => {
  if (currentUser.value) {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: currentUser.value.account })
      })
    } catch (e) {
      console.error('發送登出請求失敗:', e)
    }
  }
  currentUser.value = null
  cartItems.value = []
  router.push('/')
}

// 加入購物車
const handleAddToCart = (fruit: any, quantity: number) => {
  const existingItem = cartItems.value.find(item => item.fruit_id === fruit.fruit_id)
  if (existingItem) {
    existingItem.quantity += quantity
  } else {
    cartItems.value.push({ ...fruit, quantity })
  }
  window.alert(`成功將 ${quantity} 斤「${fruit.name}」加入購物車！`)
}

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

const onCheckoutSuccess = () => {
  cartItems.value = []
  fetchFruitsFromBackend()
  router.push('/')
}

// 透過 Provide 傳遞全域狀態給路由組件
provide('globalState', {
  fruits,
  currentUser,
  cartItems,
  handleLoginSuccess,
  handleLogout,
  handleAddToCart,
  onUpdateQuantity,
  onCheckoutSuccess
})
</script>

<template>
  <div class="app-main-wrapper">
    <router-view></router-view>
  </div>
</template>

<style>
.app-main-wrapper {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}
</style>