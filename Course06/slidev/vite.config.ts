import { defineConfig } from 'vite'
import { viteSingleFile } from 'vite-plugin-singlefile'

// The deck is published as ONE self-contained file, Course06/interactive.html:
// scripts, styles and fonts are all inlined, so it works both from GitHub Pages
// and from a file:// URL: a browser refuses to load ES modules next to a local
// file, so a split build opens blank when the file is double-clicked.
export default defineConfig({
  plugins: [
    // Slidev sets its own manualChunks, which rollup rejects alongside
    // inlineDynamicImports; drop it at the last moment, after the merge.
    {
      name: 'single-file-drop-manual-chunks',
      enforce: 'post',
      outputOptions(options: Record<string, unknown>) {
        delete options.manualChunks
        options.inlineDynamicImports = true
        return options
      },
    },
    viteSingleFile({ removeViteModuleLoader: true }),
  ],
  build: {
    // inline every font and image rather than emitting a sibling asset
    assetsInlineLimit: Number.MAX_SAFE_INTEGER,
    cssCodeSplit: false,
  },
})
