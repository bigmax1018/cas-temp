// web-vue/src/main.ts
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './assets/styles/main.css'
import './assets/styles/variables.css'

/**
 * Initialize the Vue application
 */
const app = createApp(App)

// Plugins
app.use(createPinia())
app.use(router)

// Mount the app
app.mount('#app')