import { createRouter, createWebHistory } from 'vue-router'
import FruitStore from './components/FruitStore.vue'
import LoginView from './components/LoginView.vue'
import CartAndCheckout from './components/CartAndCheckout.vue'

const routes = [
  {
    path: '/',
    name: 'store',
    component: FruitStore
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    props: { initialMode: 'login' }
  },
  {
    path: '/register',
    name: 'register',
    component: LoginView,
    props: { initialMode: 'register' }
  },
  {
    path: '/cart',
    name: 'cart',
    component: CartAndCheckout,
    props: { viewMode: 'cart' }
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: CartAndCheckout,
    props: { viewMode: 'checkout' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
