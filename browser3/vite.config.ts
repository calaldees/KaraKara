import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import svgr from 'vite-plugin-svgr'
import { VitePWA } from 'vite-plugin-pwa'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr(),
    VitePWA({
      injectRegister: null, manifest: {
        name: 'KaraKara',
        short_name: 'KaraKara',
        description: 'KaraKara Song Browser',
        theme_color: '#e9e9e9',
        icons: [
          {
            src: 'favicon.svg',
            sizes: '192x192',
            type: 'image/svg'
          },
          {
            src: 'favicon.svg',
            sizes: '512x512',
            type: 'image/svg'
          }
        ]
      }
    })
  ],
})
