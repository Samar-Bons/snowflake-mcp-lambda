// ABOUTME: End-to-end tests for authentication flow and health checks
// ABOUTME: Tests login redirect behavior and API connectivity

describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('redirects unauthenticated users to login page', () => {
    cy.url().should('include', '/login')
    cy.contains('Snowflake Chat').should('be.visible')
    cy.contains('Welcome back').should('be.visible')
  })

  it('displays Google OAuth login button', () => {
    cy.visit('/login')
    cy.contains('Continue with Google').should('be.visible')
    cy.get('button').contains('Continue with Google').should('not.be.disabled')
  })

  it('shows loading state initially', () => {
    cy.visit('/login')
    // Should eventually show the login form after loading
    cy.contains('Welcome back', { timeout: 5000 }).should('be.visible')
  })
})

describe('API Health Check', () => {
  it('can reach the backend health endpoint', () => {
    cy.checkApiHealth()
  })

  it('handles API errors gracefully', () => {
    cy.request({
      method: 'GET',
      url: 'http://localhost:8000/nonexistent',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404)
    })
  })
})
