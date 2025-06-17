# Technical Architecture Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Interaction Flow](#component-interaction-flow)
- [Core Components](#core-components)
- [Database Schema](#database-schema)
- [Security Architecture](#security-architecture)
- [Performance Optimization](#performance-optimization)
- [Monitoring and Logging](#monitoring-and-logging)
- [Integration Points](#integration-points)
- [Development Guidelines](#development-guidelines)
- [Future Architecture Considerations](#future-architecture-considerations)

## System Overview

The TB Resistance Hub is built as a modern web application using a microservices-inspired architecture with clear separation of concerns across data, business logic, and presentation layers.

### Architecture Diagram

```mermaid
graph TD
    subgraph "Presentation Layer"
        A[Streamlit Frontend<br/>app.py]
        A1[Authentication Module<br/>auth.py]
        A2[Dashboard Components]
        A3[Medical Search Interface]
        A4[User Onboarding System]
        A --> A1
        A --> A2
        A --> A3
        A --> A4
    end

    subgraph "Business Logic Layer"
        B1[Analytics Engine<br/>analytics.py]
        B2[Clinical Decision Support<br/>decision_support.py]
        B3[Data Processing<br/>data_processor.py]
        B4[Medical Search Engine<br/>medical_search.py]
        B5[Global Collaboration<br/>global_collaboration.py]
        B6[Utility Functions<br/>utils.py]
    end

    subgraph "Data Access Layer"
        C[Database Manager<br/>db_manager.py]
        C1[Connection Pool Management]
        C2[Query Abstraction]
        C3[Transaction Management]
        C4[Schema Migration Support]
        C --> C1
        C --> C2
        C --> C3
        C --> C4
    end

    subgraph "Data Storage Layer"
        D[PostgreSQL Database]
        D1[tb_cases<br/>Patient and case data]
        D2[users<br/>Authentication and roles]
        D3[user_preferences<br/>Personalization]
        D4[medical_terminology<br/>Search terms]
        D5[collaboration_requests<br/>Data sharing]
        D --> D1
        D --> D2
        D --> D3
        D --> D4
        D --> D5
    end

    A --> B1
    A --> B2
    A --> B3
    A --> B4
    A --> B5
    A --> B6

    B1 --> C
    B2 --> C
    B3 --> C
    B4 --> C
    B5 --> C
    B6 --> C

    C --> D
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Streamlit Frontend
    participant Auth as Authentication
    participant Analytics as Analytics Engine
    participant Search as Medical Search
    participant Decision as Decision Support
    participant DB as Database Manager
    participant PostgreSQL as Database

    User->>Frontend: Access Application
    Frontend->>Auth: Authenticate User
    Auth->>DB: Verify Credentials
    DB->>PostgreSQL: Query User Table
    PostgreSQL-->>DB: User Data
    DB-->>Auth: Authentication Result
    Auth-->>Frontend: Login Status

    User->>Frontend: Request Dashboard
    Frontend->>Analytics: Get TB Statistics
    Analytics->>DB: Query TB Cases
    DB->>PostgreSQL: Execute Query
    PostgreSQL-->>DB: Case Data
    DB-->>Analytics: Processed Data
    Analytics-->>Frontend: Charts & Metrics

    User->>Frontend: Search Medical Terms
    Frontend->>Search: Process Search Query
    Search->>DB: Query Medical Terms
    DB->>PostgreSQL: Search Database
    PostgreSQL-->>DB: Matching Terms
    DB-->>Search: Search Results
    Search-->>Frontend: Formatted Results

    User->>Frontend: Request Treatment Recommendation
    Frontend->>Decision: Analyze Case Data
    Decision->>DB: Get Resistance Patterns
    DB->>PostgreSQL: Query Resistance Data
    PostgreSQL-->>DB: Resistance Info
    DB-->>Decision: Analysis Data
    Decision-->>Frontend: Treatment Recommendations
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

### Database Schema Diagram

```mermaid
erDiagram
    tb_cases {
        int id PK
        string patient_id UK
        int age
        string gender
        string location
        date diagnosis_date
        string tb_type
        text resistance_pattern
        string treatment_outcome
        boolean inh_resistant
        boolean rif_resistant
        boolean emb_resistant
        boolean pza_resistant
        timestamp created_at
    }

    users {
        int id PK
        string username UK
        string password_hash
        string role
        timestamp created_at
        timestamp last_login
    }

    user_preferences {
        int id PK
        int user_id FK
        string role
        text[] interests
        string data_focus
        string experience_level
        text[] preferred_pages
        timestamp created_at
    }

    medical_terminology {
        int id PK
        string category
        string term
        text definition
        timestamp created_at
    }

    collaboration_requests {
        int id PK
        int requester_id FK
        string request_type
        text request_details
        string status
        timestamp created_at
        timestamp updated_at
    }

    users ||--o{ user_preferences : "has"
    users ||--o{ collaboration_requests : "creates"
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
