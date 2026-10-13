import { defineConfig } from 'vite'

// The deck is published as a single file, Course03/interactive.html, with
// everything it loads beside it in Course03/interactive-assets/. Slidev's own
// rollup config emits some chunks under assets/modules/, so the output names
// are set here too, to keep the published course folder to one extra directory.
const OUT = 'interactive-assets'

export default defineConfig({
  build: {
    assetsDir: OUT,
    rollupOptions: {
      output: {
        entryFileNames: `${OUT}/[name]-[hash].js`,
        chunkFileNames: `${OUT}/[name]-[hash].js`,
        assetFileNames: `${OUT}/[name]-[hash].[ext]`,
      },
    },
  },
})
