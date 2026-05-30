<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { useRouter } from 'vue-router'
import type { Fruit } from '../types'

const router = useRouter()
const globalState = inject<any>('globalState')
if (!globalState) {
  throw new Error('globalState not found')
}

const {
  fruits,
  currentUser,
  cartItems,
  handleLogout,
  handleAddToCart: addToCartGlobal
} = globalState

const activeCategory = ref<string>('當季主打')
const searchQuery = ref<string>('')
const categories = ['當季主打', '在地小農', '進口水果']

const quantities = ref<Record<string, number>>({})
const getQuantity = (id: string) => quantities.value[id] || 1

const changeQuantity = (id: string, delta: number) => {
  const current = getQuantity(id)
  const next = current + delta
  if (next >= 1) {
    quantities.value[id] = next
  }
}

const filteredFruits = computed(() => {
  return fruits.value.filter((f: Fruit) => {
    const matchCat = f.category === activeCategory.value
    const matchSearch = f.name.includes(searchQuery.value) || f.origin.includes(searchQuery.value)
    return matchCat && matchSearch
  })
})

const handleAddToCartLocal = (fruit: Fruit) => {
  const qty = getQuantity(fruit.fruit_id)
  addToCartGlobal(fruit, qty)
  quantities.value[fruit.fruit_id] = 1
}

const totalCartQuantity = computed(() => {
  if (!cartItems.value) return 0
  return cartItems.value.reduce((sum: number, item: any) => sum + item.quantity, 0)
})

const goToCart = () => router.push('/cart')
const goToLogin = () => router.push('/login')
</script>

<template>
  <div class="luxury-store-wrapper">
    <header class="glass-header">
      <div class="header-brand">
        <span class="brand-emoji">🍊</span>
        <div class="brand-text-group">
          <span class="brand-main">水果行</span>
          <span class="brand-sub">DAILY FRUIT SHOP</span>
        </div>
      </div>
      
      <div class="header-right-actions-group">
        <div class="search-input-container">
          <span class="search-lens">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜尋果物名稱..." 
            class="elegant-search-input" 
          />
        </div>

        <button class="pill-cart-badge" @click="goToCart">
          <div class="cart-icon-wrapper">
            <span class="cart-icon">🛒</span>
            <span v-if="totalCartQuantity > 0" class="cart-count-badge">{{ totalCartQuantity }}</span>
          </div>
          <span class="cart-label">購物車</span>
        </button>

        <div class="member-action-block">
          <button v-if="!currentUser" class="pill-login-btn" @click="goToLogin">
            <span class="user-icon">👤</span> 登入/註冊
          </button>
          
          <div v-else class="user-logged-box">
            <button class="logout-text-btn" @click="handleLogout">登出</button>
            <span class="user-welcome">你好，{{ currentUser.username || '新會員' }}🌷</span>
          </div>
        </div>
      </div>
    </header>

    <div class="store-layout-body">
      <aside class="floating-sidebar">
        <div class="sidebar-caption">精品分類</div>
        <div class="sidebar-nav-list">
          <button 
            v-for="cat in categories" 
            :key="cat"
            @click="activeCategory = cat"
            :class="['nav-item-btn', activeCategory === cat ? 'is-active' : '']"
          >
            <span class="active-indicator-dot"></span>
            <span class="btn-text-content">{{ cat }}</span>
          </button>
        </div>
      </aside>

      <main class="gallery-display-zone">
        <div class="gallery-title-row">
          <h2 class="category-main-title">{{ activeCategory }}</h2>
          <span class="category-meta-count">Selected {{ filteredFruits.length }} items</span>
        </div>

        <div class="aesthetic-products-grid">
          <div 
            v-for="fruit in filteredFruits" 
            :key="fruit.fruit_id" 
            class="premium-fruit-card"
          >
            <div class="card-hero-image-box">
              <img :src="fruit.image_url" :alt="fruit.name" class="hero-fruit-img" />
              <div class="glass-location-tag">
                <span class="pin-icon">📍</span>{{ fruit.origin }}
              </div>
            </div>

            <div class="card-detail-pane">
              <h3 class="fruit-display-name">{{ fruit.name }}</h3>
              <div v-if="fruit.name.includes('大西瓜')" class="watermelon-note">一斤約為兩片(每片約3到5公分帶皮)</div>
              <div class="price-typography-row">
                <span class="currency-symbol">NT$</span>
                <span class="price-number">{{ fruit.price }}</span>
                <span class="price-separator">/</span>
                <span class="unit-text">{{ fruit.unit }}</span>
              </div>
            </div>

            <div class="card-qty-selector">
              <button class="qty-btn" @click="changeQuantity(fruit.fruit_id, -1)">➖</button>
              <span class="qty-number">{{ getQuantity(fruit.fruit_id) }}</span>
              <button class="qty-btn" @click="changeQuantity(fruit.fruit_id, 1)">➕</button>
            </div>

            <button @click="handleAddToCartLocal(fruit)" class="minimal-add-cart-btn">
              <span>加入購物車</span>
            </button>
          </div>
        </div>

        <div v-if="filteredFruits.length === 0" class="premium-empty-state">
          <div class="empty-illustration">🍃</div>
          <h3>期待下一季的相遇</h3>
          <p>當前分類下沒有找到符合條件的果物商品</p>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.pill-cart-badge {
  background: #1c1917; 
  border: none; 
  padding: 10px 22px; 
  border-radius: 40px; 
  color: #ffffff; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  cursor: pointer; 
  font-weight: 600; 
  font-size: 13px; 
  transition: background 0.2s ease; 
}
.pill-cart-badge:hover { background: #3f3f46; }

.cart-icon-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cart-icon {
  font-size: 16px;
}

.cart-count-badge {
  position: absolute;
  top: -8px;
  right: -10px;
  background-color: #ffffff;
  color: hsl(0, 0%, 0%);
  font-size: 10px;
  font-weight: 800;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.member-action-block { display: flex; align-items: center; }
.pill-login-btn { background: transparent; border: 1.5px solid #1c1917; padding: 10px 20px; border-radius: 40px; color: #1c1917; display: flex; align-items: center; gap: 6px; cursor: pointer; font-weight: 600; font-size: 13px; transition: all 0.2s ease; }
.pill-login-btn:hover { background: #1c1917; color: #ffffff; }
.user-logged-box {display: flex; gap: 20px;}
.logout-text-btn { 
  background: hsla(0, 2%, 38%, 0.369); 
  border: none; 
  padding: 13px 30px; 
  border-radius: 40px; 
  color: hwb(0 0% 100% / 0.712); 
  display: flex; 
  align-items: center; 
  cursor: pointer; 
  font-weight: 600; 
  font-size: 13px; 
  transition: background 0.2s ease;
}
.logout-text-btn:hover { text-decoration: underline; }
.user-welcome { display: flex; align-items: center; font-size: 13px; font-weight: 700; color: #1c1917; white-space: nowrap; }
.card-qty-selector { display: flex; align-items: center; justify-content: space-between; background: #f5f5f4; border-radius: 12px; padding: 6px 12px; margin-bottom: 12px; }
.qty-btn { background: transparent; border: none; cursor: pointer; font-size: 12px; padding: 6px; display: flex; align-items: center; justify-content: center; transition: transform 0.1s; }
.qty-btn:active { transform: scale(0.85); }
.qty-number { font-size: 15px; font-weight: 700; color: #1c1917; min-width: 30px; text-align: center; }
.luxury-store-wrapper { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; flex-direction: column; background-color: #f6f8f7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; overflow: hidden; box-sizing: border-box; }
.glass-header { background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); padding: 16px 40px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(0, 0, 0, 0.04); box-shadow: 0 4px 30px rgba(0, 0, 0, 0.01); position: relative; z-index: 100; }
.header-brand { display: flex; align-items: center; gap: 12px; }
.brand-emoji { font-size: 28px; }
.brand-text-group { display: flex; flex-direction: column; }
.brand-main { font-size: 19px; font-weight: 800; color: #1c1917; letter-spacing: 1px; line-height: 1.2; }
.brand-sub { font-size: 9px; font-weight: 700; color: #a8a29e; letter-spacing: 1.5px; }
.header-right-actions-group { display: flex; align-items: center; gap: 20px; flex-grow: 1; justify-content: flex-end; max-width: 700px; }
.search-input-container { position: relative; flex: 1; max-width: 260px; }
.search-lens { position: absolute; left: 20px; top: 50%; transform: translateY(-50%); font-size: 16px; color: #a8a29e; }
.elegant-search-input { width: 100%; padding: 11px 20px 11px 45px; border: 1px solid rgba(0,0,0,0.08); border-radius: 30px; font-size: 14px; font-weight: 500; outline: none; background-color: #f5f5f4; color: #1c1917; transition: all 0.3s; box-sizing: border-box; }
.elegant-search-input:focus { background-color: #ffffff; border-color: #ff8a3d; }
.store-layout-body { display: flex; width: 100%; flex-grow: 1; overflow: hidden; }
.floating-sidebar { width: 250px; display: flex; flex-direction: column; padding: 32px 16px 32px 32px; box-sizing: border-box; flex-shrink: 0; }
.sidebar-caption { font-size: 11px; font-weight: 700; color: #a8a29e; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 18px; padding-left: 12px; }
.sidebar-nav-list { background-color: #ffffff; border-radius: 20px; padding: 10px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.02); }
.nav-item-btn { width: 100%; padding: 14px 16px; background: transparent; border: none; text-align: left; font-size: 14.5px; font-weight: 600; color: #57534e; cursor: pointer; border-radius: 14px; display: flex; align-items: center; gap: 12px; margin-bottom: 4px; transition: all 0.25s ease; }
.nav-item-btn.is-active { background-color: #fff7ed; color: #ff8a3d; }
.nav-item-btn.is-active .active-indicator-dot { background-color: #ff8a3d; transform: scale(1.4); }
.gallery-display-zone { flex-grow: 1; padding: 32px 40px 32px 16px; box-sizing: border-box; overflow-y: auto; }
.gallery-title-row { display: flex; align-items: baseline; gap: 14px; margin-bottom: 28px; }
.category-main-title { font-size: 24px; font-weight: 800; color: #1c1917; margin: 0; letter-spacing: -0.5px; }
.aesthetic-products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 32px; }
.premium-fruit-card { background-color: #ffffff; border-radius: 24px; padding: 14px; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid rgba(0,0,0,0.01); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.015); transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1); box-sizing: border-box; }
.premium-fruit-card:hover { transform: translateY(-8px); box-shadow: 0 24px 36px -4px rgba(255, 138, 61, 0.07); }
.card-hero-image-box { position: relative; width: 100%; height: 210px; border-radius: 18px; overflow: hidden; background-color: #f5f5f5; }
.hero-fruit-img { width: 100%; height: 100%; object-fit: cover; }
.glass-location-tag { position: absolute; bottom: 12px; left: 12px; font-size: 11.5px; color: #4338ca; font-weight: 600; background-color: rgba(238, 242, 254, 0.88); backdrop-filter: blur(8px); border-radius: 30px; padding: 5px 12px; display: flex; align-items: center; gap: 4px; }
.card-detail-pane { padding: 18px 8px 14px 8px; display: flex; flex-direction: column; gap: 8px; }
.fruit-display-name { font-size: 18px; font-weight: 700; color: #1c1917; margin: 0; }
.watermelon-note { font-size: 11px; color: #a8a29e; margin-top: -4px; margin-bottom: 4px; }
.price-typography-row { display: flex; align-items: baseline; color: #ff8a3d; }
.currency-symbol { font-size: 13px; font-weight: 700; margin-right: 2px; }
.price-number { font-size: 23px; font-weight: 800; line-height: 1; }
.unit-text { font-size: 13px; color: #78716c; font-weight: 500; }
.minimal-add-cart-btn { width: 100%; background-color: transparent; color: #ff8a3d; border: 1.5px solid #ff8a3d; border-radius: 16px; padding: 13px; font-size: 14px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.25s ease; }
.minimal-add-cart-btn:hover { background-color: #ff8a3d; color: #ffffff; box-shadow: 0 6px 16px rgba(255, 138, 61, 0.25); }
.premium-empty-state { text-align: center; color: #a8a29e; padding: 120px 0; }
</style>