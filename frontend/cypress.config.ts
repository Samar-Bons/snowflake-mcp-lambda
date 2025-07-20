import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    env: {
      apiUrl: 'http://localhost:8000',
    },
    setupNodeEvents(_on, _config) {
      // implement node event listeners here
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.ts',
  },
  component: {
    devServer: {
      framework: 'react',
      bundler: 'vite',
    },
  },
})
