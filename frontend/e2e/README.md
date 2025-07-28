# E2E Testing for Stock AI Agent Frontend

This directory contains End-to-End (E2E) tests for the Stock AI Agent frontend application using Playwright.

## Overview

The E2E tests cover the main functionality of the stock dashboard:

- **Dashboard loading and basic UI elements**
- **Stock search functionality** 
- **PE ratio cards display and interactions**
- **Popular stock buttons**
- **Loading states and error handling**
- **Responsive design elements**

## Test Files

- `basic.spec.ts` - Basic setup and page loading tests
- `dashboard.spec.ts` - Main dashboard functionality tests
- `stock-cards.spec.ts` - PE ratio cards and data display tests

## Running Tests

### Prerequisites

1. Ensure the frontend development server is running or will be auto-started
2. Playwright is installed with dependencies

### Commands

```bash
# Run all E2E tests
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test dashboard.spec.ts

# Run tests with specific browser
npx playwright test --project=chromium
```

## Test Coverage

### Dashboard Tests (`dashboard.spec.ts`)
- ✅ Page loading and title verification
- ✅ Search section display and functionality
- ✅ Popular stock buttons interaction
- ✅ Stats section display
- ✅ Input validation and form handling
- ✅ Responsive layout verification
- ✅ Accessibility checks

### Stock Cards Tests (`stock-cards.spec.ts`)
- ✅ PE ratio cards display
- ✅ Loading states and data refresh
- ✅ Stock information formatting
- ✅ PE ratio classifications and styling
- ✅ Error handling for invalid searches
- ✅ Stats updates when data changes

### Basic Tests (`basic.spec.ts`)
- ✅ Application loading verification
- ✅ Basic page title checks

## Configuration

The tests are configured in `playwright.config.ts`:

- **Base URL**: `http://localhost:3000`
- **Browser**: Chrome/Chromium
- **Auto-start**: Development server starts automatically
- **Retries**: 2 retries on CI, 0 locally
- **Reporter**: HTML report generated

## Test Strategy

The E2E tests focus on:

1. **User Journeys**: Testing complete user workflows
2. **UI Interactions**: Verifying all interactive elements work
3. **Data Display**: Ensuring stock data is properly rendered
4. **Error Handling**: Testing error states and edge cases
5. **Responsive Design**: Verifying layout works across viewports

## CI/CD Integration

Tests are configured to run in CI environments with:
- Proper retry logic
- Headless mode by default
- HTML reporting
- Error screenshots and traces on failure

## Debugging

When tests fail:

1. Check the HTML report: `npx playwright show-report`
2. Run in headed mode to see browser: `npm run test:e2e:headed`
3. Use debug mode for step-by-step execution: `npm run test:e2e:debug`
4. Review screenshots and traces in test results

## Best Practices

- Tests are isolated and can run in parallel
- Each test starts with a fresh page state
- Proper wait strategies for dynamic content
- Accessible element selection strategies
- Meaningful test descriptions and assertions