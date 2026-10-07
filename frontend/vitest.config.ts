import { defineConfig, mergeConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { reactCompilerPreset } from '@vitejs/plugin-react'

const viteConfig = {
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
}

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./vitest.setup.ts'],
      include: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
    },
  })
)
