# Testing Guide

This document outlines the comprehensive testing strategy and guidelines for the chat bot application.

## Test Structure

The project uses pytest for testing with a comprehensive test suite covering all microservices:

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── auth/                # Authentication service tests
│   ├── __init__.py
│   ├── test_routes.py   # API endpoint tests
│   ├── test_crud.py     # Database operations tests
│   └── test_utils.py    # Utility functions tests
├── api/                 # API service tests
│   ├── __init__.py
│   └── test_routes.py   # Main API endpoints tests
├── admin/               # Admin service tests
│   ├── __init__.py
│   ├── test_routes.py   # Admin panel endpoints tests
│   └── test_crud.py     # Admin operations tests
├── chat/                # Chat service tests
│   ├── __init__.py
│   ├── test_routes.py   # Chat endpoints tests
│   └── test_crud.py     # Chat operations tests
├── graph/               # LangGraph and AI components tests
│   ├── __init__.py
│   ├── test_builder.py  # Graph construction tests
│   └── test_nodes.py    # Graph nodes and state tests
└── services/            # Core services tests
    ├── __init__.py
    ├── test_history.py   # Conversation history tests
    └── test_llm.py       # LLM service tests
```

## Test Categories

### 1. Authentication Service Tests (`tests/auth/`)

#### Routes Tests (`test_routes.py`)
- User registration (success, validation, duplicates)
- User login (success, invalid credentials, inactive users)
- Token refresh and validation
- Current user retrieval
- Profile updates and password changes
- Password reset functionality
- Authentication middleware

#### CRUD Tests (`test_crud.py`)
- User creation and retrieval
- User authentication and validation
- User updates and deactivation
- Password management
- User pagination and counting
- Database error handling

#### Utils Tests (`test_utils.py`)
- Password hashing and verification
- JWT token creation and validation
- Token expiry and security
- Utility function edge cases

### 2. API Service Tests (`tests/api/`)

#### Routes Tests (`test_routes.py`)
- Health check endpoint
- Chat endpoint with authentication
- Message processing and validation
- Webhook handling and verification
- Rate limiting and concurrent requests
- Error handling and CORS
- LLM integration testing

### 3. Admin Service Tests (`tests/admin/`)

#### Routes Tests (`test_routes.py`)
- Dashboard statistics and analytics
- User management (CRUD operations)
- Chat session management
- System statistics and monitoring
- Data export functionality
- User search and bulk operations
- Audit logs and security
- Admin authorization checks

#### CRUD Tests (`test_crud.py`)
- Dashboard data aggregation
- User management operations
- Chat session and message handling
- Search functionality
- Bulk operations
- Data export and reporting
- System statistics

### 4. Chat Service Tests (`tests/chat/`)

#### Routes Tests (`test_routes.py`)
- Chat session management (CRUD)
- Message handling and processing
- WebSocket connections
- Rate limiting and security
- Session sharing and templates
- Context management
- Message reactions and editing
- AI response generation

#### CRUD Tests (`test_crud.py`)
- Session creation and management
- Message storage and retrieval
- Search functionality
- Statistics and analytics
- Data export and archiving
- Context retrieval for AI
- Popular topics analysis

### 5. Graph Service Tests (`tests/graph/`)

#### Builder Tests (`test_builder.py`)
- Graph construction and validation
- Node configuration and connections
- Execution flow testing
- Error handling and recovery
- Performance and memory efficiency
- Concurrent execution
- Custom configuration support

#### Nodes Tests (`test_nodes.py`)
- GraphState TypedDict validation
- Message type handling
- LLM integration and mocking
- State preservation and immutability
- Conversation history management
- Metadata and API info handling
- Special character support
- Concurrent processing

### 6. Services Tests (`tests/services/`)

#### History Service Tests (`test_history.py`)
- Conversation history loading
- Message type conversion
- Database query optimization
- Error handling and edge cases
- Large conversation handling
- Concurrent access
- Performance testing

#### LLM Service Tests (`test_llm.py`)
- LLM provider configuration
- OpenAI and DeepSeek integration
- Parameter validation
- Error handling and fallbacks
- Provider switching
- Concurrent access
- Configuration edge cases

## Test Configuration

### Shared Fixtures (`conftest.py`)

The `conftest.py` file provides shared fixtures for all tests:

- **Database fixtures**: In-memory SQLite for testing
- **Client fixtures**: Sync and async test clients
- **User fixtures**: Test users (regular and admin)
- **Chat fixtures**: Test sessions and messages
- **Mock fixtures**: LLM and external service mocks

### Key Fixtures

```python
@pytest.fixture
async def test_db():
    """Provides an in-memory test database."""

@pytest.fixture
async def async_client():
    """Provides an async test client."""

@pytest.fixture
def test_user():
    """Creates a test user."""

@pytest.fixture
def admin_user():
    """Creates an admin user."""

@pytest.fixture
def mock_llm():
    """Provides a mocked LLM service."""
```

## Running Tests

### Using the Test Runner

The project includes a comprehensive test runner script:

```bash
# Run all tests
python run_tests.py

# Run specific service tests
python run_tests.py --service auth
python run_tests.py --service chat
python run_tests.py --service graph

# Run with coverage
python run_tests.py --coverage

# Run in verbose mode
python run_tests.py --verbose

# Run with parallel execution
python run_tests.py --parallel 4

# Run specific test markers
python run_tests.py --markers "not slow"

# Stop on first failure
python run_tests.py --failfast

# Run only failed tests from last run
python run_tests.py --lf
```

### Direct pytest Commands

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/auth/test_routes.py

# Run specific test function
pytest tests/auth/test_routes.py::test_register_user_success

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run with markers
pytest tests/ -m "not slow"

# Run in parallel
pytest tests/ -n 4
```

### Test Environment Setup

```bash
# Check test environment
python run_tests.py check

# View available test categories
python run_tests.py categories

# Generate comprehensive test report
python run_tests.py report
```

### Test Dependencies

The project includes a comprehensive `requirements-test.txt` file with all testing dependencies:

```bash
# Install all test dependencies
pip install -r requirements-test.txt

# Or install core testing packages only
pip install pytest pytest-asyncio pytest-cov httpx faker factory-boy pytest-xdist pytest-mock
```

**Key Testing Libraries:**
- **pytest**: Core testing framework with fixtures and plugins
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting
- **pytest-xdist**: Parallel test execution
- **pytest-mock**: Enhanced mocking capabilities
- **httpx**: HTTP client for API testing
- **faker**: Test data generation
- **factory-boy**: Object factory for test fixtures
- **responses**: HTTP request mocking
- **fakeredis**: Redis mocking for tests
- **freezegun**: Time manipulation in tests
- **hypothesis**: Property-based testing
- **locust**: Load testing (optional)
- **allure-pytest**: Advanced test reporting

The project includes a comprehensive `pytest.ini` configuration file that sets up:
- Test discovery patterns
- Markers for different test categories
- Async support
- Logging configuration
- Warning filters
- Environment variables for testing

Environment variables are automatically set via `pytest.ini`, but you can override them:

```bash
export TESTING=true
export DATABASE_URL="sqlite+aiosqlite:///:memory:"
export SECRET_KEY="test-secret-key"
export OPENAI_API_KEY="test-key"
export DEEPSEEK_API_KEY="test-key"
```

### Pytest Configuration

The `pytest.ini` file provides comprehensive test configuration:

**Test Discovery:**
- Automatically finds test files matching `test_*.py` and `*_test.py`
- Discovers test classes starting with `Test*`
- Finds test functions starting with `test_*`

**Default Options:**
- Verbose output with colored results
- Short traceback format
- Shows local variables on failure
- Displays slowest 10 tests
- Strict marker and config validation

**Async Support:**
- Automatic asyncio mode for async tests
- Proper handling of async fixtures and test functions

**Logging:**
- Live logging during test execution
- Configurable log levels and formats
- Filtered warnings for cleaner output

**Parallel Execution:**
- Ready for pytest-xdist parallel execution
- Configurable worker count
- Shared test database handling

## Test Markers

The test suite uses pytest markers to categorize tests (defined in `pytest.ini`):

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.fast` - Fast running tests
- `@pytest.mark.auth` - Authentication related tests
- `@pytest.mark.chat` - Chat functionality tests
- `@pytest.mark.admin` - Admin functionality tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.graph` - LangGraph and AI component tests
- `@pytest.mark.services` - Core services tests
- `@pytest.mark.database` - Database related tests
- `@pytest.mark.llm` - LLM service tests
- `@pytest.mark.websocket` - WebSocket tests
- `@pytest.mark.security` - Security related tests
- `@pytest.mark.performance` - Performance tests

Run specific test categories:

```bash
# Run only unit tests
python run_tests.py --markers unit

# Run only fast tests
pytest -m "fast"

# Run auth and api tests
pytest -m "auth or api"

# Run everything except slow tests
pytest -m "not slow"

# Run performance tests
pytest -m "performance"
```

## Mocking Strategy

### External Services

- **LLM Services**: Mock OpenAI and DeepSeek APIs
- **Database**: Use in-memory SQLite for tests
- **Redis**: Mock Redis connections
- **Email**: Mock email sending
- **File Storage**: Mock file operations

### Mock Examples

```python
# Mock LLM service
@patch('app.services.llm.get_llm')
async def test_chat_with_mocked_llm(mock_get_llm):
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AIMessage(content="Test response")
    mock_get_llm.return_value = mock_llm
    # Test implementation

# Mock database operations
@patch('app.crud.auth.get_user_by_email')
async def test_login_with_mocked_db(mock_get_user):
    mock_get_user.return_value = test_user
    # Test implementation
```

## Test Data Management

### Using Faker

The project uses Faker for generating realistic test data:

```python
from faker import Faker
fake = Faker()

# Generate test data
test_email = fake.email()
test_username = fake.user_name()
test_message = fake.sentence()
test_timestamp = fake.date_time()
```

### Test Data Factories

```python
def create_test_user(**kwargs):
    """Factory for creating test users."""
    defaults = {
        'email': fake.email(),
        'username': fake.user_name(),
        'hashed_password': fake.password(),
        'is_active': True,
        'is_admin': False
    }
    defaults.update(kwargs)
    return User(**defaults)
```

## Coverage Requirements

### Target Coverage

- **Overall**: 90%+ code coverage
- **Critical paths**: 95%+ coverage
- **Authentication**: 95%+ coverage
- **Chat functionality**: 90%+ coverage
- **Admin operations**: 85%+ coverage

### Coverage Reports

```bash
# Generate HTML coverage report
pytest tests/ --cov=app --cov-report=html:htmlcov

# Generate XML coverage report
pytest tests/ --cov=app --cov-report=xml

# Show missing lines
pytest tests/ --cov=app --cov-report=term-missing
```

## Performance Testing

### Load Testing

```python
@pytest.mark.slow
async def test_concurrent_chat_requests():
    """Test handling of concurrent chat requests."""
    tasks = []
    for i in range(100):
        task = send_chat_message(f"Message {i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    assert len(results) == 100
```

### Memory Testing

```python
@pytest.mark.slow
async def test_large_conversation_memory():
    """Test memory usage with large conversations."""
    # Create large conversation
    messages = [create_message() for _ in range(1000)]
    
    # Test memory efficiency
    result = await process_conversation(messages)
    assert result is not None
```

## Continuous Integration

### GitHub Actions

The project includes CI/CD configuration for automated testing:

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Best Practices

### Test Organization

1. **One test class per module/feature**
2. **Descriptive test names**
3. **Arrange-Act-Assert pattern**
4. **Independent tests**
5. **Proper cleanup**

### Test Writing Guidelines

1. **Test both success and failure cases**
2. **Test edge cases and boundary conditions**
3. **Use appropriate assertions**
4. **Mock external dependencies**
5. **Keep tests focused and simple**

### Example Test Structure

```python
class TestUserAuthentication:
    """Test user authentication functionality."""
    
    async def test_login_success(self, test_user, async_client):
        """Test successful user login."""
        # Arrange
        login_data = {
            "email": test_user.email,
            "password": "test_password"
        }
        
        # Act
        response = await async_client.post("/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    async def test_login_invalid_credentials(self, async_client):
        """Test login with invalid credentials."""
        # Arrange
        login_data = {
            "email": "invalid@example.com",
            "password": "wrong_password"
        }
        
        # Act
        response = await async_client.post("/auth/login", json=login_data)
        
        # Assert
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
```

## Advanced Testing Features

### Parallel Test Execution

```bash
# Run tests in parallel using all CPU cores
pytest -n auto

# Run tests using specific number of workers
pytest -n 4

# Run tests in parallel with coverage
pytest -n auto --cov=app --cov-report=html
```

### Property-Based Testing

Using Hypothesis for property-based testing:

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=1000))
def test_message_content_validation(content):
    # Test that any valid string content is handled correctly
    message = ChatMessage(content=content, type="human")
    assert message.content == content
```

### Load Testing

```bash
# Run load tests with Locust
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Run performance benchmarks
pytest --benchmark-only
```

### Snapshot Testing

```python
def test_api_response_format(snapshot):
    response = client.get("/api/chat/sessions")
    assert response.json() == snapshot
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
python run_tests.py --verbose

# Run with pdb on failure
pytest --pdb

# Run last failed tests
pytest --lf

# Run with ipdb for better debugging
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb

# Run specific test with maximum verbosity
pytest tests/api/test_routes.py::test_chat_endpoint -vvv -s
```

### Test Profiling

```bash
# Profile test execution time
pytest --durations=0

# Memory profiling
pytest --memprof

# Generate test timeline
pytest --profile
```

### Common Issues

1. **Database Connection Issues**: Ensure test database is properly configured
2. **Async Test Failures**: Check that async fixtures are properly awaited
3. **Mock Issues**: Verify that mocks are properly configured and reset
4. **Import Errors**: Check that all dependencies are installed
5. **Flaky Tests**: Use `pytest-rerunfailures` for unstable tests
6. **Memory Leaks**: Monitor memory usage in long-running test suites

### Test Data Inspection

```python
# Add debugging prints in tests
def test_example(db_session, caplog):
    with caplog.at_level(logging.DEBUG):
        user = create_test_user()
        print(f"Created user: {user.id}")
        # ... rest of test
    
    # Check logs
    assert "User created" in caplog.text
```

## Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml

# Generate terminal coverage report
pytest --cov=app --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Advanced Reporting

```bash
# Generate Allure reports
pytest --alluredir=allure-results
allure serve allure-results

# Generate JSON report
pytest --json-report --json-report-file=report.json

# Generate HTML report
pytest --html=report.html --self-contained-html
```

## Maintenance

### Regular Tasks

1. **Update test dependencies**
2. **Review and update test data**
3. **Monitor test performance**
4. **Update coverage requirements**
5. **Refactor slow or flaky tests**

### Test Health Monitoring

```bash
# Check test execution time
pytest tests/ --durations=10

# Check test collection
pytest tests/ --collect-only

# Validate test markers
pytest tests/ --strict-markers
```

This comprehensive testing strategy ensures high code quality, reliability, and maintainability of the chat bot application across all its microservices and components.