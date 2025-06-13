# Tests 🧪

This directory contains test files and test results for the AI Parliament system. It includes both automated tests and manual testing notebooks to ensure the system works correctly.

## 📁 Structure

```
tests/
├── 📄 README.md                           # This documentation
├── 📄 party_discussion_test.ipynb         # Jupyter notebook for testing party discussions
└── 📁 test_results/                       # Test output files and results
    └── party_discussion_result3.txt       # Sample test results from party discussions
```

## 🧪 Test Types

### Jupyter Notebook Tests

#### Party Discussion Test (`party_discussion_test.ipynb`)

Interactive notebook for testing party discussion functionality:
- **Purpose**: Manual testing of intra-party deliberation logic
- **Features**: 
  - Step-by-step execution
  - Visual output inspection
  - Parameter adjustment
  - Result analysis
- **Usage**: Open in Jupyter Lab/Notebook for interactive testing

**Test Scenarios:**
- Basic party discussion flow
- Multi-politician debates
- Consensus building
- Edge cases and error handling

### Test Results

#### Test Results Directory (`test_results/`)

Contains output files from test runs:
- **party_discussion_result3.txt**: Sample output from party discussion tests
- Formatted conversation logs
- Performance metrics
- Error reports (if any)

**Result Format:**
- Timestamped entries
- Agent identification
- Message content
- Metadata and statistics

## 🚀 Running Tests

### Jupyter Notebook Tests

1. **Install Jupyter:**
   ```bash
   pip install jupyter notebook
   # or
   pip install jupyterlab
   ```

2. **Start Jupyter:**
   ```bash
   # From project root
   jupyter notebook tests/party_discussion_test.ipynb
   # or
   jupyter lab tests/party_discussion_test.ipynb
   ```

3. **Run Test Cells:**
   - Execute cells sequentially
   - Modify parameters as needed
   - Observe outputs and results

### Automated Testing (Future)

For automated test execution:
```bash
# From project root
python -m pytest tests/
```

## 📊 Test Coverage

Current test coverage includes:
- ✅ Party discussion functionality
- ✅ Agent interaction patterns
- ✅ Basic conversation flow
- ⏳ Inter-party debate (planned)
- ⏳ Voting system (planned)
- ⏳ Full simulation integration (planned)

## 🔧 Test Configuration

### Environment Setup

Tests require the same environment variables as the main application:
```env
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL_NAME=gpt-4o-mini
LANGSMITH_API_KEY=your_langsmith_key  # Optional
```

### Test Data

Test data includes:
- Sample political parties
- Mock politician profiles
- Test legislation topics
- Expected conversation patterns

## 📝 Test Results Analysis

### Reading Test Results

Test result files contain:
1. **Header Information:**
   - Test timestamp
   - Configuration used
   - Participants

2. **Conversation Log:**
   - Speaker identification
   - Message content
   - Timestamps

3. **Summary Statistics:**
   - Message counts
   - Response times
   - Success/failure rates

### Performance Metrics

Key metrics tracked:
- **Response Time**: Average time per agent response
- **Token Usage**: OpenAI API token consumption
- **Success Rate**: Percentage of successful interactions
- **Conversation Quality**: Subjective assessment of outputs

## 🐛 Debugging Tests

### Common Issues

1. **API Key Issues:**
   - Verify environment variables
   - Check API key validity
   - Monitor rate limits

2. **Notebook Kernel Issues:**
   - Restart kernel if needed
   - Clear output and re-run
   - Check Python environment

3. **Import Errors:**
   - Ensure all dependencies installed
   - Check PYTHONPATH configuration
   - Verify module structure

### Debug Mode

Enable debug logging in notebooks:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Adding New Tests

### Creating Test Notebooks

1. **Create New Notebook:**
   ```bash
   jupyter notebook tests/new_test.ipynb
   ```

2. **Standard Structure:**
   ```python
   # Cell 1: Imports and setup
   import sys
   sys.path.append('../')
   from ai.src.agents import *
   
   # Cell 2: Configuration
   test_config = {...}
   
   # Cell 3: Test execution
   results = run_test(test_config)
   
   # Cell 4: Results analysis
   analyze_results(results)
   ```

3. **Save Results:**
   ```python
   # Save to test_results directory
   with open('test_results/new_test_result.txt', 'w') as f:
       f.write(str(results))
   ```

### Test Best Practices

- **Isolation**: Each test should be independent
- **Documentation**: Clear comments and markdown cells
- **Reproducibility**: Fixed random seeds where applicable
- **Cleanup**: Proper resource cleanup after tests
- **Validation**: Assert expected outcomes

## 🔄 Continuous Testing

### Automated Test Runs

Future implementation will include:
- GitHub Actions integration
- Scheduled test execution
- Performance regression detection
- Automated result comparison

### Test Reporting

Planned features:
- HTML test reports
- Performance dashboards
- Trend analysis
- Alert notifications

## 📚 Further Reading

- [Jupyter Notebook Documentation](https://jupyter-notebook.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [AI Testing Strategies](https://www.deeplearning.ai/ai-notes/testing-ai-systems/)