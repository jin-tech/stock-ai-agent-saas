# E2E Backend Testing

This document describes the comprehensive End-to-End (E2E) testing strategy implemented for the Stock AI Agent SaaS backend API.

## Overview

The E2E test suite validates the complete backend functionality including:
- API endpoint functionality
- Database operations and persistence
- Input validation and error handling
- Complete CRUD workflows
- Edge cases and boundary conditions

## Test Architecture

### Test Isolation
- Each test uses an isolated in-memory SQLite database
- No external dependencies required (PostgreSQL, Redis, etc.)
- Tests can run in parallel without conflicts
- Clean database state for each test function

### Test Categories

#### 1. Health Endpoints (`TestHealthEndpoints`)
- Root endpoint functionality
- Health check endpoint
- API documentation accessibility

#### 2. Alert Creation (`TestAlertCreation`)
- Valid alert creation with all fields
- Symbol normalization (lowercase to uppercase)
- Optional field handling
- Input validation and error cases
- Multiple alert creation

#### 3. Alert Retrieval (`TestAlertRetrieval`)
- Empty database scenarios
- Retrieving alerts with data
- Individual alert retrieval by ID
- Filtering by symbol and active status
- Pagination functionality
- Non-existent resource handling

#### 4. Alert Updates (`TestAlertUpdate`)
- Full alert updates
- Partial alert updates
- Symbol normalization during updates
- Non-existent resource handling

#### 5. Alert Deletion (`TestAlertDeletion`)
- Successful alert deletion
- Non-existent resource handling
- Deletion persistence verification

#### 6. Error Handling (`TestErrorHandling`)
- Invalid JSON request handling
- Large numerical values
- Negative threshold values
- Special characters in messages

#### 7. Complete Workflows (`TestCompleteWorkflow`)
- Full CRUD lifecycle testing
- Bulk operations workflows
- Cross-operation persistence verification

## Running Tests

### Local Development

```bash
# Run E2E tests directly
cd backend
python -m pytest test_e2e_backend.py -v

# Use the test runner script
./run_e2e_tests.sh
```

### CI/CD Integration

The tests are integrated with GitHub Actions and will run automatically on:
- Pushes to `main` or `develop` branches
- Pull requests targeting `main` or `develop` branches
- Only when backend files are modified

## Test Data Management

### Fixtures

The test suite uses pytest fixtures for consistent test data:

- `client`: Provides isolated test client with in-memory database
- `sample_alert_data`: Standard alert data for single alert tests
- `multiple_alerts_data`: Multiple alert data for filtering/pagination tests

### Database Setup

Each test function gets a fresh SQLite in-memory database:

```python
@pytest.fixture(scope="function")
def client(self):
    """Create a test client with isolated in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:", ...)
    # ... setup code
```

## Test Coverage

The E2E test suite provides comprehensive coverage of:

✅ **API Endpoints**
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /api/alerts/` - Create alert
- `GET /api/alerts/` - List alerts with filtering
- `GET /api/alerts/{id}` - Get specific alert
- `PUT /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert

✅ **Database Operations**
- Record creation and persistence
- Data retrieval with filtering
- Record updates (full and partial)
- Record deletion
- Database constraint validation

✅ **Input Validation**
- Required field validation
- Field length validation
- Data type validation
- Invalid JSON handling

✅ **Business Logic**
- Symbol normalization to uppercase
- Default value handling
- Active/inactive filtering
- Pagination logic

✅ **Error Scenarios**
- 404 for non-existent resources
- 422 for validation errors
- Proper error message formatting

## Test Quality Assurance

### Principles

1. **Isolation**: Each test is independent and doesn't affect others
2. **Repeatability**: Tests produce consistent results across runs
3. **Comprehensiveness**: Cover happy paths, edge cases, and error scenarios
4. **Performance**: Fast execution using in-memory database
5. **Maintainability**: Clear structure and documentation

### Best Practices

- Use descriptive test names that explain the scenario
- Arrange-Act-Assert pattern for test structure
- Comprehensive assertions to verify all expected behavior
- Proper cleanup and resource management
- Consistent test data patterns

## Integration with Development Workflow

### Pre-commit Checks
```bash
# Run tests before committing
./run_e2e_tests.sh
```

### Pull Request Validation
- E2E tests run automatically on PR creation
- Tests must pass before merging
- Test results are uploaded as artifacts

### Continuous Integration
- Tests run on every push to main branches
- Results are available in GitHub Actions
- Failed tests block deployment

## Extending the Test Suite

When adding new features:

1. **Add test cases** for new endpoints or functionality
2. **Update fixtures** if new test data patterns are needed
3. **Maintain isolation** - ensure new tests don't affect existing ones
4. **Document test scenarios** in the test docstrings
5. **Run full suite** to ensure no regressions

### Example: Adding a new endpoint test

```python
def test_new_endpoint_functionality(self, client, sample_data):
    """Test description of what this endpoint should do."""
    # Arrange
    setup_data = {...}
    
    # Act
    response = client.post("/api/new-endpoint/", json=setup_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["expected_field"] == "expected_value"
```

## Dependencies

The E2E test suite requires:

- `pytest>=8.4.1` - Test framework
- `pytest-asyncio>=1.1.0` - Async test support
- `httpx` - HTTP client for testing (included with FastAPI)
- `sqlalchemy` - Database operations (included with main dependencies)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Tests use SQLite, no external DB needed
3. **Path Issues**: Run tests from the `backend` directory
4. **Permission Issues**: Ensure test runner script is executable

### Debug Mode

Run tests with more verbose output:

```bash
python -m pytest test_e2e_backend.py -v -s --tb=long
```

## Performance

The E2E test suite is optimized for:
- **Speed**: In-memory database, no I/O overhead
- **Parallelization**: Tests can run in parallel
- **Resource Usage**: Minimal memory footprint
- **CI/CD Efficiency**: Fast feedback for developers

Current metrics:
- 28 test cases run in ~1 second
- Zero external dependencies
- 100% test isolation