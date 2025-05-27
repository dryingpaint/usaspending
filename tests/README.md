# Test Suite Documentation

This directory contains comprehensive tests for the federal clean energy funding analysis project. The test suite is designed to ensure reliability, maintainability, and correctness of all data processing components.

## Test Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Pytest configuration and shared fixtures
├── README.md                       # This documentation
└── test_data_processor/            # Data processor component tests
    ├── __init__.py
    ├── test_api_client.py          # USASpending API client tests
    ├── test_data_transformer.py    # Data transformation tests
    ├── test_analytics_engine.py    # Analytics and insights tests
    └── test_core_processor.py      # Core orchestrator tests
```

## Test Categories

### Unit Tests
Fast, isolated tests that test individual functions and methods without external dependencies.
- **Marked with**: `@pytest.mark.unit`
- **Run with**: `python run_tests.py unit`

### Integration Tests
Tests that verify component interactions and may require network access to test real API endpoints.
- **Marked with**: `@pytest.mark.integration`
- **Run with**: `python run_tests.py integration`

### Slow Tests
Tests that take longer to run, typically involving large datasets or complex computations.
- **Marked with**: `@pytest.mark.slow`

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py all

# Run only fast unit tests
python run_tests.py unit

# Run specific component tests
python run_tests.py api_client
python run_tests.py transformer
python run_tests.py analytics
python run_tests.py core
```

### Advanced Usage
```bash
# Run with coverage report
python run_tests.py coverage

# Run with verbose output
python run_tests.py verbose

# Run integration tests (may require network)
python run_tests.py integration

# Run specific test file directly
pytest tests/test_data_processor/test_api_client.py -v

# Run specific test method
pytest tests/test_data_processor/test_api_client.py::TestUSASpendingAPIClient::test_search_awards_success -v
```

## Test Components

### 1. API Client Tests (`test_api_client.py`)

Tests for the USASpending API client functionality:

**Key Test Areas:**
- Client initialization and configuration
- Filter building (date, keyword, geographic)
- API endpoint interactions (awards, geography, time series)
- Error handling and network failures
- Pagination and rate limiting
- Data collection workflows

**Mock Strategy:**
- Uses `unittest.mock` to mock HTTP requests
- Tests both success and failure scenarios
- Includes integration tests for real API access

**Example:**
```python
def test_search_awards_success(self, mock_post):
    """Test successful awards search."""
    # Mock API response
    mock_response = Mock()
    mock_response.json.return_value = {"results": [...]}
    mock_post.return_value = mock_response
    
    result = self.client.search_awards(filters)
    assert "results" in result
```

### 2. Data Transformer Tests (`test_data_transformer.py`)

Tests for data cleaning, transformation, and categorization:

**Key Test Areas:**
- Data cleaning and validation
- Technology categorization
- Recipient type classification
- Geographic aggregation
- Time series creation
- Visualization data preparation

**Test Data:**
- Uses realistic sample data mimicking API responses
- Tests edge cases (empty data, invalid values, special characters)
- Validates data type conversions and column transformations

**Example:**
```python
def test_categorize_by_technology(self):
    """Test technology categorization."""
    data = self.create_sample_data()
    result = self.transformer.categorize_by_technology(data)
    
    assert "technology_category" in result.columns
    solar_mask = result["description"].str.contains("solar", case=False)
    assert result.loc[solar_mask, "technology_category"].iloc[0] == "Solar"
```

### 3. Analytics Engine Tests (`test_analytics_engine.py`)

Tests for statistical analysis and insights generation:

**Key Test Areas:**
- Summary statistics calculation
- Trend detection and analysis
- Correlation analysis
- Geographic pattern analysis
- Recipient clustering
- Insight generation

**Statistical Validation:**
- Tests mathematical correctness of calculations
- Validates statistical significance tests
- Ensures proper handling of edge cases (constant values, insufficient data)

**Example:**
```python
def test_detect_trends_increasing(self):
    """Test trend detection with increasing trend."""
    # Create data with clear upward trend
    data = pd.DataFrame({
        "start_date": dates,
        "award_amount": [1000000 + i * 50000 for i in range(50)]
    })
    
    result = self.engine.detect_trends(data)
    assert result["trend_direction"] == "increasing"
    assert result["slope"] > 0
```

### 4. Core Processor Tests (`test_core_processor.py`)

Tests for the main orchestrator that coordinates all data operations:

**Key Test Areas:**
- End-to-end data processing workflows
- Component integration
- Caching functionality
- Analysis orchestration
- Data export capabilities
- Error handling across components

**Integration Focus:**
- Tests complete data pipelines
- Validates component interactions
- Ensures proper error propagation

**Example:**
```python
@patch.object(DataProcessor, 'collect_clean_energy_data')
def test_get_comprehensive_analysis(self, mock_collect):
    """Test comprehensive analysis."""
    mock_collect.return_value = sample_data
    
    result = self.processor.get_comprehensive_analysis()
    
    assert "data_summary" in result
    assert "geographic" in result
    assert "technology" in result
```

## Test Fixtures

The test suite uses pytest fixtures defined in `conftest.py` for consistent test data:

### Data Fixtures
- `sample_raw_api_data`: Raw API response data
- `sample_cleaned_data`: Processed and cleaned data
- `sample_time_series_data`: Time series data for trend analysis
- `sample_geographic_data`: Geographic distribution data
- `empty_dataframe`: Empty DataFrame for edge case testing

### Utility Fixtures
- `mock_api_response`: Mock API response structure
- `cleanup_test_files`: Automatic test file cleanup

### Helper Functions
- `assert_dataframe_structure()`: Validate DataFrame structure
- `assert_analysis_result_structure()`: Validate analysis results
- `generate_funding_data()`: Generate synthetic test data

## Test Configuration

### Pytest Settings (`pytest.ini`)
```ini
[tool:pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers --disable-warnings --color=yes
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (may require network access)
    slow: Slow running tests
```

### Coverage Configuration
The test suite supports code coverage reporting:
```bash
python run_tests.py coverage
```

This generates:
- Terminal coverage report
- HTML coverage report in `htmlcov/`

## Best Practices

### Writing New Tests

1. **Use descriptive test names**: `test_search_awards_with_invalid_filters`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test edge cases**: Empty data, invalid inputs, network failures
4. **Use appropriate fixtures**: Leverage existing fixtures for consistency
5. **Mock external dependencies**: Use mocks for API calls, file operations

### Test Organization

1. **Group related tests**: Use test classes to group related functionality
2. **Use setup/teardown**: Leverage `setup_method()` for test initialization
3. **Mark tests appropriately**: Use `@pytest.mark.unit` or `@pytest.mark.integration`
4. **Document complex tests**: Add docstrings explaining test purpose

### Example Test Structure
```python
class TestDataTransformer:
    """Test suite for DataTransformer."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.transformer = DataTransformer()

    def test_clean_award_data_basic(self):
        """Test basic data cleaning functionality."""
        # Arrange
        raw_data = self.create_sample_data()
        
        # Act
        result = self.transformer.clean_award_data(raw_data)
        
        # Assert
        assert "award_amount" in result.columns
        assert pd.api.types.is_numeric_dtype(result["award_amount"])
```

## Continuous Integration

The test suite is designed to work with CI/CD pipelines:

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    python run_tests.py unit
    python run_tests.py coverage
```

### Local Development
```bash
# Quick test before committing
python run_tests.py unit

# Full test suite
python run_tests.py all
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path (handled by `conftest.py`)
2. **Network Tests Failing**: Integration tests may fail without internet access
3. **Missing Dependencies**: Install test dependencies with `pip install -r requirements.txt`

### Debug Mode
```bash
# Run with verbose output and no capture
pytest tests/ -vv -s

# Run specific failing test
pytest tests/test_data_processor/test_api_client.py::test_name -vv -s
```

### Test Data Issues
- Check fixture data in `conftest.py`
- Verify mock configurations
- Ensure test data matches expected formats

## Contributing

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Ensure good coverage** (aim for >90%)
3. **Test edge cases** and error conditions
4. **Update documentation** if needed
5. **Run full test suite** before submitting

### Test Checklist
- [ ] Unit tests for new functions
- [ ] Integration tests for component interactions
- [ ] Edge case testing
- [ ] Error handling tests
- [ ] Documentation updates
- [ ] All tests passing 