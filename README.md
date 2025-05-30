# TB-AMR - TB Resistance Hub

A comprehensive digital solution for tuberculosis (TB) resistance intelligence, clinical decision-making, and global health research collaboration.

## Overview

The TB Resistance Hub is an advanced web-based platform designed to enhance tuberculosis antibiotic resistance surveillance and support healthcare providers in making informed treatment decisions. The platform integrates multiple data sources, provides intelligent analytics, and facilitates global collaboration in TB research.

## Key Features

### 🏠 Dashboard & Analytics

- **Consolidated Dashboard**: Single-page interface with tabbed navigation for all features
- **Real-time Metrics**: Key performance indicators including total cases, MDR-TB prevalence, and treatment success rates
- **Interactive Visualizations**: Treatment outcomes by TB type, geographical distribution, resistance trends, and drug resistance heatmaps
- **Resistance Pattern Analysis**: Advanced analytics for identifying emerging resistance patterns

### 🔍 Smart Medical Search

- **Autocomplete Functionality**: Intelligent search suggestions using fuzzy string matching
- **Comprehensive Terminology**: Over 50 pre-loaded medical terms across 5 categories:
  - TB Types (MDR-TB, XDR-TB, TDR-TB, etc.)
  - Medications (Isoniazid, Rifampicin, Bedaquiline, etc.)
  - Side Effects (Hepatotoxicity, Peripheral neuropathy, etc.)
  - Diagnostic Terms (GeneXpert, WGS, DST, etc.)
  - Resistance Patterns (Primary resistance, Acquired resistance, etc.)
- **Category Filtering**: Filter search results by medical terminology categories
- **Admin Term Management**: Administrators can add new medical terms to the database

### 🩺 Clinical Decision Support

- **Treatment Recommendation Engine**: AI-powered regimen suggestions based on patient data
- **Patient Assessment Form**: Comprehensive intake including demographics, resistance patterns, and comorbidities
- **Drug Interaction Checker**: Identification of potential adverse drug reactions
- **TB Type Classification**: Automated classification based on resistance patterns

### 📊 Data Management

- **Multi-format Import**: Support for CSV, Excel, and API data sources
- **Flexible Export**: Export data in multiple formats (CSV, Excel, JSON)
- **Database Integration**: PostgreSQL backend with robust data validation
- **Schema Management**: Structured tables for TB cases, users, and medical terminology

### 🌍 Global Collaboration

- **Research Opportunities**: Platform for connecting with international TB research initiatives
- **Data Sharing**: Secure, anonymized data sharing with configurable privacy levels
- **Collaborative Projects**: Integration with WHO, TB Alliance, and CDC initiatives

### 👤 User Management & Onboarding

- **Role-based Authentication**: Secure login with admin and user roles
- **Personalized Onboarding**: Guided walkthrough for new users with role-specific customization
- **Feature Tours**: Interactive tutorials for each platform section
- **Help System**: Comprehensive FAQ and support resources

## Technical Architecture

### Backend Components

#### Database Layer (`db_manager.py`)

- PostgreSQL database with connection pooling
- Automated schema initialization and migration support
- SQLAlchemy integration for ORM operations
- Backup and restore functionality

#### Data Processing (`data_processor.py`)

- TB data preprocessing and validation
- Resistance pattern extraction and categorization
- Geographical distribution analysis
- Treatment outcome calculations

#### Analytics Engine (`analytics.py`)

- Statistical analysis of resistance trends
- Visualization generation using Plotly
- Key metrics calculation
- Report generation capabilities

#### Clinical Support (`decision_support.py`)

- Treatment regimen recommendation algorithms
- Drug interaction database
- Patient risk assessment
- Adverse reaction monitoring

#### Medical Search (`medical_search.py`)

- Fuzzy string matching for autocomplete
- Medical terminology database management
- Category-based search filtering
- Dynamic suggestion generation

### Frontend Components

#### Main Application (`app.py`)

- Streamlit-based web interface
- Responsive design with modern CSS styling
- Tabbed navigation system
- Real-time data visualization

#### Authentication (`auth.py`)

- SHA-256 password hashing
- Session state management
- Role-based access control
- User credential verification

#### User Experience (`onboarding.py`)

- Multi-step onboarding process
- User preference management
- Feature tour system
- Help and support integration

## Installation & Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Required Python packages (see `pyproject.toml`)

### Environment Setup

1. Clone the repository
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database and configure environment variables:
   - `DATABASE_URL`
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

### Database Initialization

The application automatically initializes the PostgreSQL database with required tables:

- `tb_cases`: Patient and case data
- `users`: User authentication and roles
- `user_preferences`: Personalization settings
- `medical_terminology`: Search terms and definitions

### Demo Data

Run the seed script to populate the database with demonstration data:

```bash
python seed_demo_data.py
```

This creates 150 sample TB cases with realistic resistance patterns and outcomes.

## Usage

### Starting the Application

```bash
streamlit run app.py --server.port 5000
```

### Default Login Credentials

- **Username**: admin
- **Password**: admin123

### Navigation

The application uses a single-page design with six main tabs:

1. **Overview**: Dashboard with key metrics and visualizations
2. **Analytics**: In-depth resistance trend analysis
3. **Clinical Support**: Treatment recommendation tools
4. **Data Management**: Import/export functionality
5. **Collaboration**: Global research opportunities
6. **Medical Search**: Smart terminology search with autocomplete

## File Structure

```bash
├── app.py                  # Main Streamlit application
├── auth.py                 # User authentication system
├── db_manager.py           # Database connection and management
├── data_processor.py       # Data processing and analysis
├── analytics.py            # Statistical analysis and visualization
├── decision_support.py     # Clinical decision support tools
├── medical_search.py       # Smart search functionality
├── onboarding.py          # User onboarding and help system
├── global_collaboration.py # Collaboration features
├── utils.py               # Utility functions
├── models.py              # Data models and schemas
├── seed_demo_data.py      # Database seeding script
├── pyproject.toml         # Project dependencies
└── README.md              # This documentation
```

## Key Database Tables

### tb_cases

Stores patient and TB case information including:

- Patient demographics (age, gender, location)
- Diagnosis details (date, TB type, resistance pattern)
- Treatment information (drugs, duration, outcome)
- Laboratory results (culture, DST, molecular tests)

### medical_terminology

Contains searchable medical terms with:

- Category classification (tb_types, drugs, side_effects, etc.)
- Term definitions and descriptions
- Search optimization metadata

### users

User management with:

- Authentication credentials
- Role assignments (admin, user)
- Activity tracking

## Features Implementation Status

### ✅ Fully Functional

- User authentication and role management
- Dashboard with real-time metrics
- Interactive data visualizations
- Clinical decision support
- Data import/export capabilities
- Medical terminology search with autocomplete
- Global collaboration interface
- User onboarding and help system
- PostgreSQL database integration

### 🔄 Requires External Integration

- Genomic sequencing (WGS) data processing
- Advanced AI prediction models
- Real-time synchronization with external databases
- Patient engagement mobile application
- Provider forum and messaging system

## Security Features

- SHA-256 password hashing
- Session-based authentication
- Role-based access control
- SQL injection prevention
- Data anonymization for sharing
- Secure database connections

## Performance Optimization

- Database connection pooling
- Lazy loading of large datasets
- Caching of frequently accessed data
- Optimized SQL queries
- Responsive web design

## API Integration

The platform supports integration with external data sources:

- RESTful API endpoints for data import
- Configurable API authentication
- Error handling and retry mechanisms
- Data validation and transformation

## Collaboration Features

### Data Sharing

- Configurable anonymization levels
- Secure sharing tokens
- Audit trails for data access
- Partner organization management

### Research Integration

- WHO Collaborative Research Network
- International TB Research Consortium
- Global Health AI Initiative
- Custom research project support

## Support and Documentation

### Built-in Help System

- Interactive feature tours
- Contextual help tooltips
- FAQ and troubleshooting guides
- Video tutorials and documentation

### External Resources

- User manual and training materials
- API documentation
- Developer guides
- Community forum

## Version History

### v1.0 (Current)

- Initial release with core functionality
- PostgreSQL database integration
- Smart medical search implementation
- Consolidated dashboard interface
- User onboarding system

## Contributing

For contributions and development:

1. Follow the existing code structure and naming conventions
2. Add appropriate documentation for new features
3. Include unit tests for new functionality
4. Update this README for significant changes

## License

This project is developed for global health research and clinical decision support in tuberculosis care.

## Contact

For technical support or collaboration inquiries:

- Technical Support: Contact your system administrator
- Research Collaboration: Use the platform's collaboration features
- Development: Refer to the developer documentation

---

_TB Resistance Hub - Enhancing global tuberculosis resistance intelligence through data-driven insights and collaborative research._
