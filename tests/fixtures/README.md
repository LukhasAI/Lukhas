# Test Fixtures

Shared test fixtures and setup files.

## Structure
- `sample_data/` - Sample data files for testing
- `mocks/` - Mock objects and responses  
- `configs/` - Test configuration files

## Usage
Fixtures are available through pytest fixtures defined in `conftest.py`:

```python
def test_with_fixture(fixtures_dir):
    data_file = fixtures_dir / "sample_data" / "example.json"
    # use fixture
```