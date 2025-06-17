# Technical Architecture Documentation

## System Overview

The TB Resistance Hub is built as a modern web application using a microservices-inspired architecture with clear separation of concerns across data, business logic, and presentation layers.

### Architecture Diagram

```mermaid
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Streamlit Frontend (app.py)                               │
│  ├── Authentication Module (auth.py)                       │
│  ├── Dashboard Components                                  │
│  ├── Medical Search Interface                              │
│  └── User Onboarding System                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                     │
├─────────────────────────────────────────────────────────────┤
│  ├── Analytics Engine (analytics.py)                       │
│  ├── Clinical Decision Support (decision_support.py)       │
│  ├── Data Processing (data_processor.py)                   │
│  ├── Medical Search Engine (medical_search.py)             │
│  ├── Global Collaboration (global_collaboration.py)        │
│  └── Utility Functions (utils.py)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Data Access Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Database Manager (db_manager.py)                          │
│  ├── Connection Pool Management                            │
│  ├── Query Abstraction                                     │
│  ├── Transaction Management                                │
│  └── Schema Migration Support                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage Layer                     │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                        │
│  ├── tb_cases (Patient and case data)                      │
│  ├── users (Authentication and roles)                      │
│  ├── user_preferences (Personalization)                    │
│  ├── medical_terminology (Search terms)                    │
│  └── collaboration_requests (Data sharing)                 │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Layer (Streamlit)

**File**: `app.py`
**Purpose**: User interface and interaction management
**Technologies**: Streamlit, HTML/CSS, JavaScript

#### Key Features

- Single-page application with tabbed navigation
- Real-time data visualization using Plotly
- Responsive design with modern CSS styling
- Session state management
- Form handling and validation

#### Dependencies

```python
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.1.0
numpy>=1.24.0
```

### 2. Authentication System

**File**: `auth.py`
**Purpose**: User authentication and authorization
**Security**: SHA-256 password hashing, session management

#### Implementation Details

- Password hashing using hashlib.sha256
- Role-based access control (admin, user)
- Session state persistence
- Secure credential validation

```python
def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode()).hexdigest()
```

### 3. Database Management

**File**: `db_manager.py`
**Purpose**: Database abstraction and connection management
**Database**: PostgreSQL with psycopg2 driver

#### Key Functions

- Connection pooling and management
- Automatic schema initialization
- Query execution with parameter binding
- Transaction management
- SQLAlchemy integration for DataFrame operations

#### Connection Configuration

```python
def get_connection():
    """Create a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT'),
            database=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD')
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None
```

### 4. Analytics Engine

**File**: `analytics.py`
**Purpose**: Statistical analysis and visualization generation

#### Capabilities

- Resistance trend analysis over time
- Geographical distribution mapping
- Treatment outcome analysis
- Drug resistance pattern visualization
- Key performance metrics calculation

#### Visualization Components

- Time series charts for resistance trends
- Choropleth maps for geographical data
- Heatmaps for drug resistance patterns
- Bar charts for treatment outcomes
- KPI cards for dashboard metrics

### 5. Clinical Decision Support

**File**: `decision_support.py`
**Purpose**: Treatment recommendation engine

#### Algorithm Components

- TB type classification based on resistance patterns
- Drug regimen recommendation logic
- Drug interaction checking
- Adverse reaction monitoring
- Patient risk assessment

#### Decision Logic

```python
def determine_tb_type(resistance_data):
    """Determines TB type based on resistance data"""
    if resistance_data.get('inh_resistant') and resistance_data.get('rif_resistant'):
        if resistance_data.get('fluoroquinolone_resistant') and resistance_data.get('injectable_resistant'):
            return 'XDR-TB'
        return 'MDR-TB'
    elif resistance_data.get('rif_resistant'):
        return 'RR-TB'
    elif resistance_data.get('inh_resistant'):
        return 'INH-resistant TB'
    return 'Drug-susceptible TB'
```

### 6. Medical Search Engine

**File**: `medical_search.py`
**Purpose**: Intelligent medical terminology search

#### Features

- Fuzzy string matching using fuzzywuzzy library
- Category-based filtering
- Autocomplete suggestions
- Real-time search results
- Admin term management

#### Search Algorithm

```python
def get_term_suggestions(partial_term, limit=10):
    """Get suggestions for autocomplete based on partial term"""
    if len(partial_term) < 2:
        return []

    df = get_medical_terms()
    all_terms = df['term'].tolist()
    matches = process.extractBests(partial_term, all_terms, limit=limit, score_cutoff=60)
    return [match[0] for match in matches]
```

### 7. Data Processing Pipeline

**File**: `data_processor.py`
**Purpose**: Data validation, transformation, and analysis

#### Processing Steps

1. Data validation and cleaning
2. Resistance pattern extraction
3. TB type categorization
4. Geographical distribution calculation
5. Treatment outcome analysis

## Database Schema

### Core Tables

#### tb_cases

```sql
CREATE TABLE tb_cases (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(10),
    location VARCHAR(100),
    diagnosis_date DATE,
    tb_type VARCHAR(50),
    resistance_pattern TEXT,
    treatment_outcome VARCHAR(50),
    inh_resistant BOOLEAN DEFAULT FALSE,
    rif_resistant BOOLEAN DEFAULT FALSE,
    emb_resistant BOOLEAN DEFAULT FALSE,
    pza_resistant BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### users

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### medical_terminology

```sql
CREATE TABLE medical_terminology (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    term VARCHAR(255) NOT NULL,
    definition TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category, term)
);
```

#### user_preferences

```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(50),
    interests TEXT[],
    data_focus VARCHAR(100),
    experience_level VARCHAR(50),
    preferred_pages TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Architecture

### Authentication Security

- SHA-256 password hashing with salt
- Session-based authentication
- Role-based access control
- Session timeout management

### Data Security

- SQL injection prevention through parameterized queries
- Input validation and sanitization
- Secure database connections
- Data anonymization for sharing

### Application Security

- Environment variable configuration
- Secure session state management
- HTTPS enforcement (production)
- Error handling without information disclosure

## Performance Optimization

### Database Optimization

- Connection pooling
- Query optimization
- Indexed columns for frequent searches
- Lazy loading of large datasets

### Application Performance

- Streamlit caching for expensive operations
- Efficient data processing with pandas
- Optimized visualization rendering
- Memory management for large datasets

### Caching Strategy

```python
@st.cache_data
def load_tb_data(conn):
    """Cache TB data loading for improved performance"""
    query = "SELECT * FROM tb_cases ORDER BY diagnosis_date DESC"
    return pd.read_sql_query(query, conn)
```

## Deployment Architecture

### Environment Configuration

- Development: Local PostgreSQL, Streamlit dev server
- Production: Managed PostgreSQL, containerized deployment
- Environment variables for configuration management

### Scaling Considerations

- Horizontal scaling for web tier
- Database connection pooling
- Load balancing for multiple instances
- CDN for static assets

## Monitoring and Logging

### Application Monitoring

- Streamlit built-in metrics
- Database query performance monitoring
- User activity tracking
- Error logging and alerting

### Health Checks

- Database connectivity monitoring
- Application health endpoints
- Performance metrics collection
- Automated alerting for issues

## Integration Points

### External API Integration

- RESTful API support for data import
- Authentication token management
- Rate limiting and retry logic
- Error handling and fallback mechanisms

### Data Import/Export

- CSV/Excel file processing
- API data ingestion
- Batch processing capabilities
- Data validation and transformation

## Development Guidelines

### Code Organization

- Modular architecture with clear separation of concerns
- Consistent naming conventions
- Comprehensive error handling
- Extensive documentation and comments

### Testing Strategy

- Unit tests for core business logic
- Integration tests for database operations
- End-to-end testing for user workflows
- Performance testing for large datasets

### Version Control

- Git-based version control
- Feature branch workflow
- Code review requirements
- Automated testing on commits

## Future Architecture Considerations

### Microservices Migration

- API gateway implementation
- Service decomposition strategy
- Inter-service communication
- Distributed data management

### Cloud-Native Features

- Container orchestration
- Auto-scaling capabilities
- Managed database services
- Serverless function integration

### Advanced Analytics

- Machine learning model integration
- Real-time data streaming
- Advanced visualization capabilities
- Predictive analytics pipeline
