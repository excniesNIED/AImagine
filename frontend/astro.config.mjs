import { defineConfig } from 'astro/config';
import vue from '@astrojs/vue';
import tailwind from '@astrojs/tailwind';
// Removed invalid CommonJS named import from '@vue/devtools-api' which breaks Vite SSR

export default defineConfig({
  integrations: [
    vue({
      appEntrypoint: '/src/vue-plugins',
      template: {
        compilerOptions: {
          isCustomElement: tag => tag.startsWith('prime-')
        }
      }
    }),
    tailwind({
      applyBaseStyles: false,
    })
  ],
  // Use static output for static hosting; add an adapter if SSR is needed
  output: 'static',
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
        }
      }
    }
  }
});