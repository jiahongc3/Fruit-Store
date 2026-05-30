<script setup lang="ts">
import { computed, ref, watchEffect, inject } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE } from '../config'

const props = defineProps<{
  viewMode: string
}>()

const router = useRouter()
const globalState = inject<any>('globalState')
if (!globalState) {
  throw new Error('globalState not found')
}

const {
  currentUser,
  cartItems,
  onUpdateQuantity,
  onCheckoutSuccess
} = globalState

const recipientName = ref('')
const phone = ref('')
const address = ref('')
const paymentMethod = ref('cod')

watchEffect(() => {
  if (currentUser.value && typeof currentUser.value === 'object') {
    recipientName.value = currentUser.value.username || '新會員'
    phone.value = currentUser.value.phone || ''
    address.value = currentUser.value.address || ''
  } else {
    recipientName.value = ''
    phone.value = ''
    address.value = ''
  }
})

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum: number, item: any) => sum + (item.price * item.quantity), 0)
})

const totalQuantity = computed(() => {
  return cartItems.value.reduce((sum: number, item: any) => sum + item.quantity, 0)
})

const handleQtyChange = (fruitId: string, currentQty: number, delta: number) => {
  const newQty = currentQty + delta
  if (newQty <= 0) {
    const confirmDelete = window.confirm('確認要將此水果從購物籃中完全移除嗎？')
    if (confirmDelete) {
      onUpdateQuantity(fruitId, 0)
    }
  } else {
    onUpdateQuantity(fruitId, newQty)
  }
}

const handleFinalSubmit = async () => {
  if (!recipientName.value || !phone.value || !address.value) {
    return window.alert('請完整填寫收件資訊！')
  }

  const nameRegex = /^[\u4e00-\u9fa5]{2,4}$/
  if (!nameRegex.test(recipientName.value)) {
    return window.alert('收件人姓名格式不正確！請輸入 2 至 4 個字的中文字，不能包含英文或數字。')
  }

  const phoneRegex = /^09\d{8}$/
  if (!phoneRegex.test(phone.value)) {
    return window.alert('聯絡電話格式不正確！')
  }

  try {
    const payload = {
      username: currentUser.value?.account || 'guest',
      cartItems: cartItems.value.map((item: any) => ({
        fruit_id: item.fruit_id,
        quantity: item.quantity
      })),
      recipientName: recipientName.value,
      phone: phone.value,
      address: address.value,
      paymentMethod: paymentMethod.value
    }

    const response = await fetch(`${API_BASE}/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const result = await response.json()
    if (response.ok && result.success) {
      window.alert(`下單成功！訂單編號：${result.orderId}\n應付總額為 NT$ ${result.totalPrice}\n付款方式：貨到付款`)
      onCheckoutSuccess()
    } else {
      window.alert(result.message || '訂單建立失敗')
    }
  } catch (error) {
    window.alert('發送訂單時失敗，請確認後端狀態')
  }
}

const handleGoToCheckout = () => {
  if (!currentUser.value) {
    window.alert('請先登入或註冊會員，才能進行結帳喔！')
    router.push('/login')
    return
  }
  
  if (cartItems.value.length === 0) {
    window.alert('您的購物籃是空的，請先挑選喜愛的水果再前去結帳！')
    return
  }
  
  router.push('/checkout')
}

const goBack = () => router.push('/')
</script>

<template>
  <div class="process-screen">
    <div class="fullscreen-bg"></div>
    
    <div class="process-container">
      <button class="back-nav-btn" @click="goBack">
        <span class="arrow">←</span> 上一頁
      </button>

      <div v-if="viewMode === 'cart'" class="content-card">
        <h2 class="section-title">我的購物籃 <span class="count">({{ totalQuantity }})</span></h2>
        
        <div class="cart-list">
          <div v-for="item in cartItems" :key="item.fruit_id" class="cart-item">
            <img :src="item.image_url" class="item-img" />
            <div class="item-info">
              <h4>{{ item.name }}</h4>
              <div v-if="item.name.includes('大西瓜')" class="watermelon-note">一斤約為兩片(每片約3到5公分帶皮)</div>
              <p class="unit-price">NT$ {{ item.price }} / {{ item.unit }}</p>
            </div>
            
            <div class="qty-control-block">
              <button class="cart-qty-btn" @click="handleQtyChange(item.fruit_id, item.quantity, -1)">➖</button>
              <span class="cart-qty-num">{{ item.quantity }}</span>
              <button class="cart-qty-btn" @click="handleQtyChange(item.fruit_id, item.quantity, 1)">➕</button>
            </div>

            <div class="item-total">NT$ {{ item.price * item.quantity }}</div>
          </div>
        </div>

        <div class="cart-footer">
          <div class="total-bar">總計金額: <span class="price">NT$ {{ totalPrice }}</span></div>
          <button class="next-step-btn" @click="handleGoToCheckout">
            前往結帳 →
          </button>
        </div>
      </div>

      <div v-if="viewMode === 'checkout'" class="content-card">
        <h2 class="section-title">結帳資料確認</h2>
        <div class="checkout-form">
          <div class="form-group">
            <label>收件人姓名</label>
            <input v-model="recipientName" type="text" placeholder="陳小晴" class="form-input" />
          </div>
          <div class="form-group">
            <label>聯絡電話</label>
            <input v-model="phone" type="text" placeholder="09xx-xxx-xxx" class="form-input" />
          </div>
          <div class="form-group">
            <label>送貨地址</label>
            <input v-model="address" type="text" placeholder="請輸入詳細地址" class="form-input" />
          </div>

          <div class="checkout-footer-row">
            <div class="form-group payment-group">
              <label>付款方式</label>
              <div class="payment-selector">
                <button 
                  type="button"
                  class="payment-btn" 
                  :class="{ 'is-active': paymentMethod === 'cod' }"
                  @click="paymentMethod = 'cod'"
                >
                  <span class="icon">💵</span> 貨到付款
                </button>
              </div>
            </div>
            
            <div class="order-summary inline-summary">
              <p>應付總額: <strong>NT$ {{ totalPrice }}</strong></p>
            </div>
          </div>
          
          <button class="final-submit-btn" @click="handleFinalSubmit">確認並送出訂單</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.qty-control-block { margin-left: auto; display: flex; align-items: center; background: #f5f5f4; border-radius: 8px; padding: 4px 8px; gap: 8px; }
.cart-qty-btn { background: transparent; border: none; cursor: pointer; font-size: 10px; display: flex; align-items: center; justify-content: center; padding: 4px; }
.cart-qty-num { font-size: 14px; font-weight: 700; color: #1c1917; min-width: 24px; text-align: center; }
.process-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; z-index: 1000; }
.fullscreen-bg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-image: url('../assets/fruit.png'); background-size: cover; z-index: 1; }
.process-container { position: relative; z-index: 10; width: 100%; max-width: 600px; padding: 20px; }
.back-nav-btn { background: rgba(255, 255, 255, 0.9); border: none; padding: 8px 16px; border-radius: 50px; font-weight: 600; color: #57534e; cursor: pointer; margin-bottom: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s; }
.back-nav-btn:hover { background: #fff; transform: translateX(-4px); }
.content-card { background: white; border-radius: 24px; padding: 35px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
.section-title { font-size: 22px; margin-bottom: 25px; color: #1c1917; }
.cart-item { display: flex; align-items: center; gap: 15px; padding: 15px 0; border-bottom: 1px solid #f5f5f4; }
.item-img { width: 50px; height: 50px; border-radius: 8px; object-fit: cover; }
.item-info h4 { margin: 0; font-size: 16px; }
.watermelon-note { font-size: 11px; color: #a8a29e; margin-top: -4px; margin-bottom: 4px; }
.unit-price { font-size: 12px; color: #a8a29e; margin: 0; }
.item-total { font-weight: 700; color: #ff8a3d; min-width: 80px; text-align: right; }
.cart-footer { margin-top: 30px; text-align: right; }
.total-bar { font-size: 18px; font-weight: 700; margin-bottom: 20px; }
.total-bar .price { color: #ff8a3d; font-size: 24px; }
.next-step-btn, .final-submit-btn { background: #ff8a3d; color: white; border: none; padding: 14px 30px; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; width: 100%; }
.checkout-form { display: flex; flex-direction: column; gap: 15px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 5px; color: #57534e; }
.form-input { width: 100%; padding: 12px; border: 1px solid #e7e5e4; border-radius: 8px; outline: none; }
.checkout-footer-row { display: flex; align-items: flex-end; justify-content: space-between; gap: 20px; margin: 5px 0; }
.payment-group { flex: 1; margin-bottom: 0; }
.payment-selector { display: flex; margin-top: 5px; }
.payment-btn { width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px; padding: 7px 0px; background: #ffffff; border: 2px solid #e7e5e4; border-radius: 12px; font-size: 14px; font-weight: 700; color: #57534e; cursor: pointer; transition: all 0.2s ease; }
.payment-btn.is-active { background: #fff7ed; border-color: #ff8a3d; color: #ff8a3d; box-shadow: 0 4px 12px rgba(255, 138, 61, 0.08); }
.payment-btn .icon { font-size: 16px; }
.inline-summary { margin: 0; text-align: right; flex: 1; padding-bottom: 10px; }
</style>