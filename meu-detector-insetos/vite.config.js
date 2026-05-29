import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    // Proxy das chamadas da API para o backend FastAPI.
    // Assim o frontend faz requisições same-origin (/detectar) e não há CORS.
    proxy: {
      '/detectar': {
        target: 'http://127.0.0.1:5555',
        changeOrigin: true,
      },
    },
  },
})
