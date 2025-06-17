# Data Dictionary and Metadata Documentation

## Overview

This document provides comprehensive information about the data structures, schemas, sources, and metadata for the TB Resistance Hub platform. All data follows standardized formats aligned with WHO tuberculosis surveillance guidelines and international clinical standards.

## Database Schema

### Core Tables

#### tb_cases

**Purpose**: Primary table storing tuberculosis case information and clinical data
**Source**: Clinical laboratories, healthcare facilities, surveillance systems
**Update Frequency**: Real-time as cases are reported

| Column Name               | Data Type    | Constraints                                   | Description                      | Example Values                      |
| ------------------------- | ------------ | --------------------------------------------- | -------------------------------- | ----------------------------------- |
| id                        | SERIAL       | PRIMARY KEY                                   | Unique case identifier           | 1, 2, 3...                          |
| patient_id                | VARCHAR(50)  | UNIQUE, NOT NULL                              | Anonymous patient identifier     | TB2024001, MDR_NYC_001              |
| age                       | INTEGER      | CHECK (age > 0 AND age < 150)                 | Patient age in years             | 25, 45, 67                          |
| gender                    | VARCHAR(10)  | CHECK (gender IN ('Male', 'Female', 'Other')) | Patient gender                   | Male, Female                        |
| location                  | VARCHAR(100) | NOT NULL                                      | Geographic location              | New York, Mumbai, Cape Town         |
| country                   | VARCHAR(50)  | NOT NULL                                      | Country code (ISO 3166-1)        | USA, IND, ZAF                       |
| diagnosis_date            | DATE         | NOT NULL                                      | Date of TB diagnosis             | 2024-03-15                          |
| tb_type                   | VARCHAR(50)  | NOT NULL                                      | TB classification                | Drug-susceptible TB, MDR-TB, XDR-TB |
| resistance_pattern        | TEXT         |                                               | Detailed resistance description  | INH+RIF+EMB, Extensive resistance   |
| treatment_outcome         | VARCHAR(50)  |                                               | Final treatment result           | Cured, Treatment Completed, Failed  |
| treatment_start_date      | DATE         |                                               | Treatment initiation date        | 2024-03-20                          |
| treatment_end_date        | DATE         |                                               | Treatment completion date        | 2024-09-20                          |
| inh_resistant             | BOOLEAN      | DEFAULT FALSE                                 | Isoniazid resistance status      | true, false                         |
| rif_resistant             | BOOLEAN      | DEFAULT FALSE                                 | Rifampicin resistance status     | true, false                         |
| emb_resistant             | BOOLEAN      | DEFAULT FALSE                                 | Ethambutol resistance status     | true, false                         |
| pza_resistant             | BOOLEAN      | DEFAULT FALSE                                 | Pyrazinamide resistance status   | true, false                         |
| sm_resistant              | BOOLEAN      | DEFAULT FALSE                                 | Streptomycin resistance status   | true, false                         |
| fluoroquinolone_resistant | BOOLEAN      | DEFAULT FALSE                                 | Fluoroquinolone resistance       | true, false                         |
| injectable_resistant      | BOOLEAN      | DEFAULT FALSE                                 | Injectable drug resistance       | true, false                         |
| hiv_status                | VARCHAR(20)  |                                               | HIV co-infection status          | Positive, Negative, Unknown         |
| previous_tb_treatment     | BOOLEAN      | DEFAULT FALSE                                 | Prior TB treatment history       | true, false                         |
| culture_positive          | BOOLEAN      |                                               | Culture confirmation status      | true, false                         |
| smear_positive            | BOOLEAN      |                                               | Smear microscopy result          | true, false                         |
| xpert_result              | VARCHAR(50)  |                                               | GeneXpert MTB/RIF result         | MTB Detected/RIF Resistance         |
| dst_performed             | BOOLEAN      | DEFAULT FALSE                                 | Drug susceptibility testing done | true, false                         |
| created_at                | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP                     | Record creation timestamp        | 2024-06-16 10:30:00                 |
| updated_at                | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP                     | Last update timestamp            | 2024-06-16 15:45:00                 |

**Indexes**:

- `idx_tb_cases_diagnosis_date` ON diagnosis_date
- `idx_tb_cases_location` ON location
- `idx_tb_cases_tb_type` ON tb_type
- `idx_tb_cases_resistance_pattern` ON resistance_pattern

#### users

**Purpose**: User authentication and role management
**Source**: Internal user management system
**Update Frequency**: As needed for user administration

| Column Name   | Data Type    | Constraints               | Description             | Example Values                             |
| ------------- | ------------ | ------------------------- | ----------------------- | ------------------------------------------ |
| id            | SERIAL       | PRIMARY KEY               | Unique user identifier  | 1, 2, 3...                                 |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL          | User login name         | admin, researcher01                        |
| password_hash | VARCHAR(64)  | NOT NULL                  | SHA-256 hashed password | 8c6976e5b5410415bde908bd4dee15dfb167a9c... |
| role          | VARCHAR(20)  | DEFAULT 'user'            | User access level       | admin, user, researcher                    |
| full_name     | VARCHAR(100) |                           | User's full name        | Dr. Jane Smith                             |
| email         | VARCHAR(100) | UNIQUE                    | User email address      | <jane.smith@hospital.org>                  |
| organization  | VARCHAR(100) |                           | Affiliated organization | City Hospital, WHO                         |
| created_at    | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Account creation date   | 2024-01-15 09:00:00                        |
| last_login    | TIMESTAMP    |                           | Last login timestamp    | 2024-06-16 08:30:00                        |
| active        | BOOLEAN      | DEFAULT TRUE              | Account status          | true, false                                |

#### medical_terminology

**Purpose**: Standardized medical terminology and definitions
**Source**: WHO guidelines, medical literature, clinical standards
**Update Frequency**: Monthly updates, immediate for critical terms

| Column Name | Data Type    | Constraints               | Description            | Example Values                       |
| ----------- | ------------ | ------------------------- | ---------------------- | ------------------------------------ |
| id          | SERIAL       | PRIMARY KEY               | Unique term identifier | 1, 2, 3...                           |
| category    | VARCHAR(50)  | NOT NULL                  | Terminology category   | tb_types, drugs, side_effects        |
| term        | VARCHAR(255) | NOT NULL                  | Medical term           | MDR-TB, Isoniazid, Hepatotoxicity    |
| definition  | TEXT         | NOT NULL                  | Detailed definition    | Multi-drug resistant tuberculosis... |
| synonyms    | TEXT[]       |                           | Alternative terms      | {"Multidrug-resistant TB", "MDR TB"} |
| source      | VARCHAR(100) |                           | Definition source      | WHO Guidelines 2023                  |
| created_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Term addition date     | 2024-01-01 00:00:00                  |
| updated_at  | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Last update date       | 2024-06-01 10:00:00                  |

**Categories**:

- `tb_types`: TB classifications and resistance patterns
- `drugs`: Anti-tuberculosis medications
- `side_effects`: Adverse drug reactions
- `diagnostic_terms`: Laboratory and clinical diagnostics
- `resistance_patterns`: Specific resistance classifications

#### user_preferences

**Purpose**: Personalized user settings and onboarding data
**Source**: User input during onboarding and settings management
**Update Frequency**: User-driven updates

| Column Name           | Data Type    | Constraints               | Description                    | Example Values                          |
| --------------------- | ------------ | ------------------------- | ------------------------------ | --------------------------------------- |
| id                    | SERIAL       | PRIMARY KEY               | Unique preference record       | 1, 2, 3...                              |
| user_id               | INTEGER      | REFERENCES users(id)      | Associated user                | 1, 2, 3...                              |
| role                  | VARCHAR(50)  |                           | User's primary role            | Clinician, Researcher, Administrator    |
| interests             | TEXT[]       |                           | Areas of interest              | {"MDR-TB", "Pediatric TB"}              |
| data_focus            | VARCHAR(100) |                           | Primary data focus             | Treatment Outcomes, Resistance Patterns |
| experience_level      | VARCHAR(50)  |                           | TB expertise level             | Beginner, Intermediate, Expert          |
| preferred_pages       | TEXT[]       |                           | Favorite platform sections     | {"Analytics", "Clinical Support"}       |
| dashboard_layout      | JSONB        |                           | Custom dashboard configuration | {"widgets": ["metrics", "charts"]}      |
| notification_settings | JSONB        |                           | Alert preferences              | {"email": true, "in_app": false}        |
| created_at            | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Preference creation date       | 2024-03-01 14:20:00                     |
| updated_at            | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Last modification date         | 2024-06-10 16:30:00                     |

### Lookup Tables

#### countries

**Purpose**: Standardized country codes and geographic information
**Source**: ISO 3166-1 country codes, WHO regional classifications

| Column Name  | Data Type    | Description               | Example Values                     |
| ------------ | ------------ | ------------------------- | ---------------------------------- |
| code         | VARCHAR(3)   | ISO 3166-1 alpha-3 code   | USA, IND, ZAF                      |
| name         | VARCHAR(100) | Official country name     | United States, India, South Africa |
| region       | VARCHAR(50)  | WHO region                | Americas, South-East Asia, Africa  |
| income_level | VARCHAR(50)  | World Bank classification | High income, Lower middle income   |
| tb_burden    | VARCHAR(20)  | TB burden classification  | High, Medium, Low                  |

#### drug_codes

**Purpose**: Standardized anti-TB drug codes and information
**Source**: WHO Essential Medicines List, drug databases

| Column Name | Data Type    | Description         | Example Values                  |
| ----------- | ------------ | ------------------- | ------------------------------- |
| code        | VARCHAR(10)  | Standard drug code  | INH, RIF, EMB, PZA              |
| name        | VARCHAR(100) | Generic drug name   | Isoniazid, Rifampicin           |
| category    | VARCHAR(50)  | Drug classification | First-line, Second-line         |
| mechanism   | TEXT         | Mode of action      | Inhibits mycolic acid synthesis |

## Data Sources and Collection

### Primary Data Sources

#### Clinical Laboratories

- **Source Type**: Direct laboratory reporting systems
- **Data Elements**: Culture results, DST findings, molecular test results
- **Update Frequency**: Real-time as results become available
- **Quality Assurance**: Laboratory certification, proficiency testing
- **Geographic Coverage**: Global network of certified laboratories

#### Healthcare Facilities

- **Source Type**: Electronic health records, case reporting forms
- **Data Elements**: Patient demographics, treatment history, outcomes
- **Update Frequency**: Daily batch updates
- **Quality Assurance**: Data validation rules, clinical verification
- **Coverage**: Public and private healthcare providers

#### National TB Programs

- **Source Type**: National surveillance systems
- **Data Elements**: Aggregated case notifications, program indicators
- **Update Frequency**: Monthly reporting cycles
- **Quality Assurance**: WHO validation protocols
- **Standards**: WHO TB surveillance guidelines

#### Research Institutions

- **Source Type**: Clinical trials, observational studies
- **Data Elements**: Detailed clinical data, genomic information
- **Update Frequency**: Study-specific schedules
- **Quality Assurance**: Research ethics approval, data monitoring

### Data Collection Methodology

#### Data Validation Pipeline

1. **Input Validation**: Format checking, range validation, required field verification
2. **Clinical Validation**: Medical logic checks, consistency verification
3. **Quality Scoring**: Completeness assessment, accuracy rating
4. **Anomaly Detection**: Statistical outlier identification, pattern recognition

#### Data Standardization

- **Terminology**: Standardized medical terms and codes
- **Formats**: ISO date formats, standardized geographic codes
- **Units**: Metric system, standardized laboratory units
- **Classifications**: WHO TB classification system

## Data Access and Security

### Access Control Matrix

| User Role  | tb_cases              | users             | medical_terminology | user_preferences |
| ---------- | --------------------- | ----------------- | ------------------- | ---------------- |
| Admin      | Read/Write/Delete     | Read/Write/Delete | Read/Write          | Read/Write       |
| Researcher | Read (anonymized)     | Read (limited)    | Read                | Read/Write (own) |
| Clinician  | Read/Write (assigned) | Read (limited)    | Read                | Read/Write (own) |
| User       | Read (limited)        | Read (own)        | Read                | Read/Write (own) |

### Data Anonymization

#### Patient Data Protection

- **Direct Identifiers**: Removed or encrypted
- **Quasi-identifiers**: Generalized or suppressed
- **Sensitive Attributes**: Protected through k-anonymity
- **Geographic Data**: Aggregated to appropriate levels

#### Anonymization Levels

1. **High**: Full de-identification, geographic aggregation
2. **Medium**: Partial anonymization, date shifting
3. **Low**: Pseudonymization, minimal aggregation

### Data Retention

#### Retention Policies

- **Clinical Data**: 10 years from last patient contact
- **Aggregated Analytics**: Indefinite retention
- **User Activity Logs**: 2 years
- **System Logs**: 1 year

#### Archival Process

- **Active Data**: High-performance database storage
- **Historical Data**: Compressed archival storage
- **Backup Strategy**: Daily incremental, weekly full backups
- **Recovery Testing**: Monthly recovery verification

## Data Quality Framework

### Quality Dimensions

#### Completeness

- **Metric**: Percentage of non-null required fields
- **Target**: 95% completeness for core clinical data
- **Monitoring**: Real-time dashboard alerts

#### Accuracy

- **Metric**: Validation rule compliance rate
- **Target**: 98% accuracy for critical fields
- **Verification**: Cross-reference with external sources

#### Consistency

- **Metric**: Inter-field logical consistency checks
- **Target**: 99% consistency for related data elements
- **Validation**: Automated consistency rules

#### Timeliness

- **Metric**: Time from data generation to availability
- **Target**: 24 hours for routine data, 4 hours for urgent
- **Monitoring**: Processing time tracking

### Quality Assurance Procedures

#### Data Entry Validation

```sql
-- Example validation rules
ALTER TABLE tb_cases ADD CONSTRAINT valid_age
CHECK (age > 0 AND age <= 120);

ALTER TABLE tb_cases ADD CONSTRAINT valid_outcome
CHECK (treatment_outcome IN ('Cured', 'Treatment Completed', 'Failed', 'Died', 'Lost to follow-up', 'Not evaluated'));

ALTER TABLE tb_cases ADD CONSTRAINT valid_dates
CHECK (treatment_start_date >= diagnosis_date);
```

#### Regular Quality Audits

- **Frequency**: Monthly comprehensive audits
- **Scope**: Data completeness, accuracy, consistency
- **Reporting**: Quality scorecards, trend analysis
- **Actions**: Corrective measures, process improvements

## Metadata Management

### Data Lineage

#### Source Tracking

- **Original Source**: Laboratory, facility, program
- **Collection Method**: Manual entry, API import, file upload
- **Processing History**: Transformations, validations applied
- **Quality Scores**: Completeness, accuracy metrics

#### Transformation Documentation

```json
{
  "transformation_id": "normalize_resistance_pattern",
  "description": "Standardize resistance pattern encoding",
  "input_format": "Free text resistance description",
  "output_format": "Structured boolean flags",
  "business_rules": [
    "Map 'resistant to INH' to inh_resistant=true",
    "Map 'MDR' to inh_resistant=true AND rif_resistant=true"
  ],
  "implementation_date": "2024-01-15",
  "version": "1.2"
}
```

### Data Catalog

#### Dataset Inventory

| Dataset Name  | Description          | Update Frequency | Size            | Quality Score |
| ------------- | -------------------- | ---------------- | --------------- | ------------- |
| TB Cases      | Clinical case data   | Daily            | 150,000 records | 94%           |
| Medical Terms | Terminology database | Monthly          | 500 terms       | 99%           |
| User Activity | Platform usage logs  | Real-time        | 50,000 events   | 97%           |

#### Field-Level Metadata

```json
{
  "field_name": "tb_type",
  "table": "tb_cases",
  "data_type": "VARCHAR(50)",
  "description": "Classification of tuberculosis based on drug resistance pattern",
  "business_definition": "Categorization following WHO guidelines for TB resistance classification",
  "valid_values": [
    "Drug-susceptible TB",
    "INH-resistant TB",
    "RR-TB",
    "MDR-TB",
    "XDR-TB",
    "TDR-TB"
  ],
  "source_system": "Laboratory Information System",
  "business_owner": "TB Program Manager",
  "technical_owner": "Database Administrator",
  "last_updated": "2024-06-01",
  "data_quality_rules": [
    "Not null for confirmed TB cases",
    "Must match predefined classification list",
    "Consistent with resistance pattern flags"
  ]
}
```

### Change Management

#### Schema Evolution

- **Version Control**: Git-based schema versioning
- **Migration Scripts**: Automated database migrations
- **Rollback Procedures**: Tested rollback capabilities
- **Impact Assessment**: Change impact analysis

#### Documentation Updates

- **Trigger Events**: Schema changes, new data sources, policy updates
- **Review Process**: Technical and business stakeholder approval
- **Publication**: Automated documentation generation
- **Distribution**: Stakeholder notification system

## Integration Specifications

### API Data Ingestion

#### Supported Formats

- **JSON**: Structured clinical data
- **CSV**: Bulk laboratory results
- **HL7 FHIR**: Healthcare interoperability standard
- **XML**: Legacy system integration

#### Data Mapping Specifications

```json
{
  "api_endpoint": "/api/v1/tb-cases",
  "method": "POST",
  "content_type": "application/json",
  "schema": {
    "patient_id": { "type": "string", "required": true, "max_length": 50 },
    "age": { "type": "integer", "required": true, "min": 0, "max": 120 },
    "diagnosis_date": {
      "type": "date",
      "required": true,
      "format": "YYYY-MM-DD"
    },
    "resistance_tests": {
      "type": "object",
      "properties": {
        "isoniazid": {
          "type": "string",
          "enum": ["Susceptible", "Resistant", "Indeterminate"]
        },
        "rifampicin": {
          "type": "string",
          "enum": ["Susceptible", "Resistant", "Indeterminate"]
        }
      }
    }
  },
  "validation_rules": [
    "diagnosis_date must not be in the future",
    "age must be reasonable for TB diagnosis",
    "patient_id must be unique within submitting organization"
  ]
}
```

### External System Integration

#### Laboratory Information Systems (LIS)

- **Protocol**: HL7 v2.5, RESTful APIs
- **Data Elements**: Culture results, DST findings, molecular diagnostics
- **Frequency**: Real-time result reporting
- **Authentication**: OAuth 2.0, API keys

#### Electronic Health Records (EHR)

- **Protocol**: HL7 FHIR R4
- **Data Elements**: Patient demographics, treatment history, outcomes
- **Frequency**: Daily synchronization
- **Authentication**: SMART on FHIR

#### National Surveillance Systems

- **Protocol**: Custom APIs, batch file transfer
- **Data Elements**: Case notifications, aggregate indicators
- **Frequency**: Monthly reporting cycles
- **Authentication**: Certificate-based authentication

This comprehensive data dictionary provides the foundation for understanding, maintaining, and extending the TB Resistance Hub data infrastructure while ensuring compliance with international standards and best practices for health data management.
