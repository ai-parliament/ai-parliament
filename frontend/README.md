# Frontend Interface 🌐

The frontend module provides an intuitive web interface built with Streamlit for configuring and running AI Parliament simulations. It offers a user-friendly way to set up political parties, politicians, and legislative topics, then visualize the entire parliamentary process.

## 🏗️ Architecture

The frontend follows a modular Streamlit architecture:

```
Streamlit App
├── Configuration Manager (YAML-based)
├── Session State Management
├── API Integration (Backend Communication)
├── UI Components (Sidebar + Main Area)
└── Real-time Updates
```

## 📁 Structure

```
frontend/
├── 📄 Dockerfile                    # Container configuration
├── 📄 pyproject.toml                # Module configuration
├── 📄 requirements.txt              # Dependencies
├── 📁 config/                       # Configuration files
│   ├── app_config.yml               # Application settings
│   ├── default_parties.yml          # Pre-configured parties
│   └── texts.yml                    # UI text and labels
└── 📁 src/
    ├── 📄 app.py                    # Main Streamlit application
    └── 📄 config_manager.py         # Configuration management system
```

## 🎨 User Interface

### Sidebar Configuration Panel

**LLM Settings:**
- Model selection (GPT-4, GPT-3.5-turbo, etc.)
- Temperature control (0.0 - 1.0)
- Max tokens slider (500 - 4000)

**Parliament Configuration:**
- Number of parties (1-10)
- Party names and abbreviations
- Politicians per party (1-5)
- Individual politician details (name, role)

**Control Buttons:**
- Start Simulation
- Reset Configuration

### Main Content Area

**Welcome Screen:**
- Introduction and instructions
- Getting started guide

**Topic Input:**
- Legislative topic text input
- Topic submission form
- Help text and examples

**Simulation Actions:**
- Run Intra-Party Deliberation
- Run Inter-Party Debate
- Conduct Final Voting
- Generate Summary

**Results Display:**
- Real-time chat interface
- Formatted discussion summaries
- Vote tallies and breakdowns
- Final simulation summary

## 🔧 Core Components

### Main Application (`app.py`)

The central Streamlit application with key functions:

#### `setup_page()`
Configures Streamlit page settings:
- Page title and icon
- Layout configuration
- Sidebar state

#### `initialize_session_state()`
Manages application state:
- Default values from config
- Persistent session data
- State synchronization

#### `sidebar_ui()`
Creates the configuration sidebar:
- LLM parameter controls
- Party and politician setup
- Dynamic form generation
- Validation and submission

#### `main_screen()`
Renders the main content area:
- Welcome message
- Topic input form
- Simulation controls
- Results display

#### `call_backend_api()`
Handles API communication:
- HTTP request management
- Error handling
- Response processing
- User feedback

### Configuration Manager (`config_manager.py`)

Comprehensive configuration system:

#### YAML Configuration Loading
- `app_config.yml`: Application settings
- `texts.yml`: UI text and internationalization
- `default_parties.yml`: Pre-configured political parties

#### Environment Integration
- Backend API URL configuration
- Docker environment detection
- Debug mode settings

#### Dynamic Configuration
- LLM model options
- UI color schemes
- Session state defaults
- Party and politician templates

## 📋 Configuration Files

### Application Config (`app_config.yml`)

```yaml
llm:
  default_model: "gpt-4o-mini"
  available_models:
    - "gpt-3.5-turbo"
    - "gpt-4"
    - "gpt-4o-mini"
  temperature:
    default: 0.7
    min: 0.0
    max: 1.0
    step: 0.1
  max_tokens:
    default: 2000
    min: 500
    max: 4000
    step: 100

parliament:
  parties:
    default_count: 2
    min_count: 1
    max_count: 10
  mps:
    default_per_party: 2
    min_per_party: 1
    max_per_party: 5

ui:
  page:
    title: "AI Parliament"
    icon: "🏛️"
    layout: "wide"
    sidebar_state: "expanded"
  colors:
    system_message:
      background: "#f0f2f6"
      border: "#4e8cff"
    party_message:
      background: "#e6f3ff"
      border: "#0068c9"
    politician_message:
      background: "#f5f5f5"
      border: "#ff9500"
```

### Text Configuration (`texts.yml`)

```yaml
titles:
  app_title: "AI Parliament Simulator"
  configuration_title: "Configuration"
  session_title: "Parliamentary Session"

labels:
  model_label: "AI Model"
  temperature_label: "Temperature"
  max_tokens_label: "Max Tokens"
  party_name_label: "Party Name"
  politician_name_label: "Politician Name"

buttons:
  start_simulation: "Start Simulation"
  reset: "Reset"
  start_discussion: "Start Discussion"

messages:
  success:
    simulation_created: "Simulation created successfully!"
    topic_set: "Topic set successfully!"
  error:
    simulation_failed: "Failed to create simulation"
    topic_failed: "Failed to set topic"
```

### Default Parties (`default_parties.yml`)

```yaml
parties:
  "Prawo i Sprawiedliwość":
    abbreviation: "PiS"
    politicians:
      - name: "Jarosław Kaczyński"
        role: "Chairman"
      - name: "Antoni Macierewicz"
        role: "Member"
  
  "Platforma Obywatelska":
    abbreviation: "PO"
    politicians:
      - name: "Donald Tusk"
        role: "Chairman"
      - name: "Grzegorz Schetyna"
        role: "Member"
```

## 🎯 Features

### Dynamic Party Configuration
- Add/remove parties dynamically
- Customizable party names and abbreviations
- Flexible politician assignment
- Default party templates

### Real-time Simulation Monitoring
- Live chat interface
- Step-by-step progress tracking
- Formatted message display
- Color-coded message types

### Responsive Design
- Mobile-friendly interface
- Collapsible sidebar
- Adaptive layouts
- Consistent styling

### Configuration Persistence
- Session state management
- Form data retention
- Reset functionality
- Default value restoration

## 🐳 Docker Configuration

### Dockerfile Features

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Configure Streamlit
EXPOSE 8501
ENV PYTHONPATH=/app
ENV BACKEND_API_URL=http://backend:8000/api

# Start application
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables

```env
# Backend Integration
BACKEND_API_URL=http://backend:8000/api

# Optional: AI Configuration
OPENAI_API_KEY=your_openai_api_key
GPT_MODEL_NAME=gpt-4o-mini

# Optional: LangSmith Monitoring
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=ai-parliament
LANGSMITH_TRACING=true
```

## 📋 Dependencies

### Core Dependencies
- **Streamlit**: Web application framework
- **Requests**: HTTP client for API communication
- **PyYAML**: YAML configuration parsing
- **python-dotenv**: Environment variable management

### Optional Dependencies
- **Plotly**: Advanced data visualization
- **Pandas**: Data manipulation
- **Altair**: Statistical visualizations

## 🚀 Usage

### Development Mode

```bash
cd frontend
pip install -r requirements.txt
streamlit run src/app.py
```

Access the application at `http://localhost:8501`

### Production Mode

```bash
# Using Docker
docker build -t ai-parliament-frontend .
docker run -p 8501:8501 --env-file .env ai-parliament-frontend

# Using Docker Compose
docker-compose up frontend
```

### Configuration Customization

1. **Modify UI Settings:**
   ```bash
   # Edit application configuration
   nano config/app_config.yml
   ```

2. **Update Text Content:**
   ```bash
   # Edit UI text and labels
   nano config/texts.yml
   ```

3. **Add Default Parties:**
   ```bash
   # Edit default party configurations
   nano config/default_parties.yml
   ```

## 🎨 Customization

### Adding New UI Components

1. **Create Component Function:**
   ```python
   def new_component():
       with st.container():
           st.markdown("## New Component")
           # Component logic here
   ```

2. **Integrate with Main App:**
   ```python
   def main_screen():
       # Existing code...
       new_component()
   ```

### Custom Styling

1. **Add CSS Styles:**
   ```python
   def get_custom_css():
       return """
       <style>
       .custom-component {
           background-color: #f0f0f0;
           padding: 1rem;
           border-radius: 0.5rem;
       }
       </style>
       """
   
   st.markdown(get_custom_css(), unsafe_allow_html=True)
   ```

### Configuration Extensions

1. **Add New Config Section:**
   ```yaml
   # In app_config.yml
   new_feature:
     enabled: true
     settings:
       option1: "value1"
       option2: "value2"
   ```

2. **Access in Code:**
   ```python
   new_feature_enabled = config.get_nested_config("new_feature", "enabled", default=False)
   ```

## 🧪 Testing

### Manual Testing

1. **UI Components:**
   - Test all form inputs
   - Verify button functionality
   - Check responsive design

2. **API Integration:**
   - Test backend connectivity
   - Verify error handling
   - Check response processing

3. **Configuration:**
   - Test YAML file loading
   - Verify default values
   - Check environment variables

### Automated Testing

```bash
cd frontend
python -m pytest tests/
```

### User Acceptance Testing

1. **Simulation Workflow:**
   - Create parties and politicians
   - Set legislative topic
   - Run complete simulation
   - Verify results display

2. **Error Scenarios:**
   - Test with invalid inputs
   - Simulate backend failures
   - Check error messages

## 🐛 Troubleshooting

### Common Issues

1. **Streamlit Not Starting:**
   ```bash
   # Check port availability
   lsof -i :8501
   
   # Try different port
   streamlit run src/app.py --server.port=8502
   ```

2. **Backend Connection Issues:**
   - Verify backend is running
   - Check `BACKEND_API_URL` environment variable
   - Test API endpoints manually

3. **Configuration Loading Errors:**
   - Validate YAML syntax
   - Check file permissions
   - Verify file paths

4. **Session State Issues:**
   - Clear browser cache
   - Restart Streamlit server
   - Check session state initialization

### Performance Optimization

- **Caching:** Use `@st.cache_data` for expensive operations
- **Session State:** Minimize session state usage
- **API Calls:** Implement request caching
- **UI Updates:** Use `st.rerun()` judiciously

## 📱 Mobile Responsiveness

The interface is optimized for mobile devices:
- Responsive sidebar
- Touch-friendly controls
- Readable text sizes
- Optimized layouts

## 🌐 Internationalization

The system supports multiple languages through the text configuration:

1. **Add Language Files:**
   ```yaml
   # config/texts_es.yml (Spanish)
   titles:
     app_title: "Simulador del Parlamento IA"
   ```

2. **Language Selection:**
   ```python
   language = st.selectbox("Language", ["en", "es", "fr"])
   config.load_language(language)
   ```

## 📚 Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)
- [YAML Specification](https://yaml.org/spec/)
- [Python Requests Documentation](https://requests.readthedocs.io/)