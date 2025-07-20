// ABOUTME: Custom Cypress commands for testing authentication and common flows
// ABOUTME: Reusable test utilities and helper functions

/// <reference types="cypress" />

// Add custom commands here
declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to check if API health endpoint is accessible
       */
      checkApiHealth(): Chainable<void>
    }
  }
}

Cypress.Commands.add('checkApiHealth', () => {
  cy.request({
    method: 'GET',
    url: 'http://localhost:8000/health',
    failOnStatusCode: false,
  }).then((response) => {
    expect(response.status).to.eq(200)
  })
})
