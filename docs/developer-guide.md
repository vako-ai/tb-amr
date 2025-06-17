# Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [API Reference](#api-reference)
5. [Database Operations](#database-operations)
6. [Testing Guidelines](#testing-guidelines)
7. [Deployment Guide](#deployment-guide)
8. [Contributing Guidelines](#contributing-guidelines)

## Development Environment Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 13+ (local or remote)
- Git for version control
- Code editor (VS Code recommended)

### Installation Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/vako-ai/tb-amr
   cd tb-resistance-hub
   ```

2. **Set Up Python Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Configuration**
   Create a `.env` file in the project root:

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/tb_resistance_hub
   PGHOST=localhost
   PGPORT=5432
   PGUSER=your_username
   PGPASSWORD=your_password
   PGDATABASE=tb_resistance_hub
   ```

4. **Initialize Database**

   ```bash
   python -c "import db_manager; db_manager.initialize_database()"
   ```

5. **Seed Demo Data**

   ```bash
   python seed_demo_data.py
   ```

6. **Run the Application**

   ```bash
   streamlit run app.py --server.port 5000
   ```

### Development Tools

#### Recommended VS Code Extensions

- Python
- PostgreSQL
- GitLens
- Python Docstring Generator
- Black Formatter

#### Code Formatting

```bash
pip install black flake8 isort
black .
flake8 .
isort .
```

## Project Structure

```bash
tb-resistance-hub/
├── app.py                      # Main Streamlit application
├── auth.py                     # Authentication system
├── db_manager.py               # Database management
├── data_processor.py           # Data processing pipeline
├── analytics.py                # Analytics and visualization
├── decision_support.py         # Clinical decision support
├── medical_search.py           # Medical terminology search
├── onboarding.py              # User onboarding system
├── global_collaboration.py     # Collaboration features
├── utils.py                   # Utility functions
├── models.py                  # Data models
├── seed_demo_data.py          # Database seeding
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── docs/                      # Documentation
│   ├── technical-architecture.md
│   ├── developer-guide.md
│   ├── user-guide.md
│   └── data-dictionary.md
└── tests/                     # Test files
    ├── test_auth.py
    ├── test_db_manager.py
    └── test_analytics.py
```

## Coding Standards

### Python Style Guide

#### Function Documentation

```python
def process_tb_data(df, validation_rules=None):
    """
    Process TB data with validation and transformation.

    Parameters:
    df (pandas.DataFrame): Raw TB data
    validation_rules (dict, optional): Custom validation rules

    Returns:
    pandas.DataFrame: Processed TB data

    Raises:
    ValueError: If required columns are missing
    ValidationError: If data validation fails
    """
    # Implementation here
    pass
```

#### Error Handling

```python
def get_patient_data(patient_id):
    """Retrieve patient data with proper error handling."""
    try:
        conn = get_connection()
        if not conn:
            raise DatabaseConnectionError("Failed to connect to database")

        # Database operations
        return result

    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"Failed to retrieve patient data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if conn:
            conn.close()
```

#### Configuration Management

```python
# Use environment variables for configuration
import os
from typing import Optional

class Config:
    """Application configuration management."""

    DATABASE_URL: str = os.getenv('DATABASE_URL', '')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'development-key')

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        required = ['DATABASE_URL']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        return True
```

### Database Best Practices

#### Query Parameterization

```python
# Good - Parameterized query
def get_tb_cases_by_location(location):
    query = "SELECT * FROM tb_cases WHERE location = %s"
    return fetch_data(conn, query, (location,))

# Bad - String concatenation (SQL injection risk)
def get_tb_cases_by_location_bad(location):
    query = f"SELECT * FROM tb_cases WHERE location = '{location}'"
    return fetch_data(conn, query)
```

#### Transaction Management

```python
def update_patient_treatment(patient_id, treatment_data):
    """Update patient treatment with transaction safety."""
    conn = get_connection()
    try:
        conn.autocommit = False
        cursor = conn.cursor()

        # Multiple related operations
        cursor.execute(
            "UPDATE tb_cases SET treatment_outcome = %s WHERE patient_id = %s",
            (treatment_data['outcome'], patient_id)
        )

        cursor.execute(
            "INSERT INTO treatment_history (patient_id, treatment, date) VALUES (%s, %s, %s)",
            (patient_id, treatment_data['regimen'], treatment_data['date'])
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        conn.close()
```

## API Reference

### Core Modules

#### db_manager.py

```python
def get_connection() -> psycopg2.connection:
    """Create database connection."""

def execute_query(conn, query: str, params: tuple = None) -> bool:
    """Execute SQL query with parameters."""

def fetch_data(conn, query: str, params: tuple = None) -> list:
    """Fetch data from database."""

def dataframe_to_database(df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
    """Save DataFrame to database."""

def query_to_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Execute query and return DataFrame."""
```

#### analytics.py

```python
def load_tb_data(conn) -> pd.DataFrame:
    """Load TB data for analytics."""

def create_resistance_trend_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure:
    """Create resistance trend visualization."""

def create_geo_distribution_chart(df: pd.DataFrame) -> plotly.graph_objects.Figure:
    """Create geographical distribution chart."""

def calculate_key_metrics(df: pd.DataFrame) -> dict:
    """Calculate dashboard metrics."""

def generate_report(df: pd.DataFrame, report_type: str = 'summary') -> str:
    """Generate HTML report."""
```

#### decision_support.py

```python
def determine_tb_type(resistance_data: dict) -> str:
    """Classify TB type based on resistance."""

def generate_regimen_recommendation(patient_data: dict) -> dict:
    """Generate treatment recommendations."""

def get_drug_interactions(drugs: list) -> list:
    """Check for drug interactions."""

def check_for_adverse_reactions(symptoms: list, drugs: list) -> dict:
    """Check for adverse drug reactions."""
```

#### medical_search.py

```python
def get_medical_terms(category: str = None, search_term: str = None) -> pd.DataFrame:
    """Retrieve medical terms from database."""

def get_term_suggestions(partial_term: str, limit: int = 10) -> list:
    """Get autocomplete suggestions."""

def add_medical_term(category: str, term: str, definition: str) -> bool:
    """Add new medical term."""

def search_medical_terms(search_text: str) -> pd.DataFrame:
    """Search medical terms."""
```

## Database Operations

### Schema Management

#### Creating New Tables

```python
def create_new_table(conn, table_name, schema):
    """Create new database table with proper error handling."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})")
        conn.commit()
        logger.info(f"Table {table_name} created successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to create table {table_name}: {e}")
        raise
```

#### Schema Migrations

```python
def apply_migration(conn, migration_sql):
    """Apply database schema migration."""
    try:
        cursor = conn.cursor()
        cursor.execute(migration_sql)
        conn.commit()
        logger.info("Migration applied successfully")
    except Exception as e:
        conn.rollback()
        logger.error(f"Migration failed: {e}")
        raise
```

### Data Access Patterns

#### Repository Pattern

```python
class TBCaseRepository:
    """Repository for TB case data operations."""

    def __init__(self, conn):
        self.conn = conn

    def get_by_id(self, case_id: int) -> dict:
        """Get TB case by ID."""
        query = "SELECT * FROM tb_cases WHERE id = %s"
        result = fetch_data(self.conn, query, (case_id,))
        return result[0] if result else None

    def get_by_resistance_pattern(self, pattern: str) -> list:
        """Get cases by resistance pattern."""
        query = "SELECT * FROM tb_cases WHERE resistance_pattern LIKE %s"
        return fetch_data(self.conn, query, (f"%{pattern}%",))

    def create(self, case_data: dict) -> int:
        """Create new TB case."""
        query = """
        INSERT INTO tb_cases (patient_id, age, gender, location, tb_type)
        VALUES (%(patient_id)s, %(age)s, %(gender)s, %(location)s, %(tb_type)s)
        RETURNING id
        """
        cursor = self.conn.cursor()
        cursor.execute(query, case_data)
        return cursor.fetchone()[0]
```

## Testing Guidelines

### Test Structure

```bash
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_db_manager.py
│   └── test_analytics.py
├── integration/
│   ├── test_database_integration.py
│   └── test_api_integration.py
└── fixtures/
    ├── sample_data.csv
    └── test_database.sql
```

### Unit Testing Example

```python
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from analytics import calculate_key_metrics, create_resistance_trend_chart

class TestAnalytics(unittest.TestCase):
    """Test cases for analytics module."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003'],
            'tb_type': ['MDR-TB', 'Drug-susceptible TB', 'XDR-TB'],
            'treatment_outcome': ['Cured', 'Treatment Completed', 'Failed'],
            'diagnosis_date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })

    def test_calculate_key_metrics(self):
        """Test key metrics calculation."""
        metrics = calculate_key_metrics(self.sample_data)

        self.assertEqual(metrics['total_cases'], 3)
        self.assertEqual(metrics['mdr_count'], 1)
        self.assertEqual(metrics['success_rate'], 67)  # 2/3 * 100

    def test_resistance_trend_chart(self):
        """Test resistance trend chart creation."""
        chart = create_resistance_trend_chart(self.sample_data)

        self.assertIsNotNone(chart)
        self.assertEqual(chart.layout.title.text, 'TB Resistance Trends Over Time')

    @patch('analytics.get_connection')
    def test_load_tb_data_connection_error(self, mock_get_connection):
        """Test handling of database connection errors."""
        mock_get_connection.return_value = None

        from analytics import load_tb_data
        result = load_tb_data(None)

        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
import unittest
import os
import psycopg2
from db_manager import get_connection, initialize_database

class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests for database operations."""

    @classmethod
    def setUpClass(cls):
        """Set up test database."""
        cls.test_db_url = os.getenv('TEST_DATABASE_URL')
        if not cls.test_db_url:
            cls.skipTest(cls, "TEST_DATABASE_URL not set")

        # Initialize test database
        initialize_database()

    def test_database_connection(self):
        """Test database connection."""
        conn = get_connection()
        self.assertIsNotNone(conn)

        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)

        conn.close()

    def test_table_creation(self):
        """Test that required tables exist."""
        conn = get_connection()
        cursor = conn.cursor()

        # Check if tb_cases table exists
        cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_name = 'tb_cases'
        """)

        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/unit/test_analytics.py

# Run with coverage
python -m pytest --cov=. tests/

# Run integration tests only
python -m pytest tests/integration/
```

## Deployment Guide

### Production Environment Setup

#### Environment Variables

```env
# Production configuration
DATABASE_URL=postgresql://user:password@production-host:5432/tb_resistance_hub
SECRET_KEY=your-production-secret-key
DEBUG=False
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=5000
```

#### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

#### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/tb_resistance_hub
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=tb_resistance_hub
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Health Checks

```python
def health_check():
    """Application health check endpoint."""
    try:
        # Test database connection
        conn = get_connection()
        if not conn:
            return {"status": "unhealthy", "reason": "database_connection_failed"}

        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()

        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
```

## Contributing Guidelines

### Git Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m "Add your feature"`
4. Push to branch: `git push origin feature/your-feature`
5. Create Pull Request

### Code Review Checklist

- [ ] Code follows Python style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Database migrations included if needed

### Release Process

1. Update version number in `__init__.py`
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to staging environment
5. Run integration tests
6. Deploy to production

### Performance Guidelines

#### Database Query Optimization

```python
# Use indexes for frequent queries
CREATE INDEX idx_tb_cases_diagnosis_date ON tb_cases(diagnosis_date);
CREATE INDEX idx_tb_cases_location ON tb_cases(location);
CREATE INDEX idx_tb_cases_resistance_pattern ON tb_cases(resistance_pattern);

# Use EXPLAIN to analyze query performance
EXPLAIN ANALYZE SELECT * FROM tb_cases WHERE location = 'New York';
```

#### Caching Strategy

```python
import functools
import time

def cache_with_ttl(ttl_seconds=300):
    """Decorator for caching function results with TTL."""
    def decorator(func):
        cache = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result

        return wrapper
    return decorator

@cache_with_ttl(300)  # Cache for 5 minutes
def get_resistance_statistics():
    """Get resistance statistics with caching."""
    # Expensive database operation
    pass
```

This developer guide provides comprehensive information for setting up, developing, testing, and deploying the TB Resistance Hub application.
