# API Documentation

## Overview

The TB Resistance Hub provides a comprehensive API for programmatic access to TB resistance data, analytics, and clinical decision support functions. This REST API enables integration with external systems, automated data exchange, and custom application development.

## Base URL and Versioning

```http
Base URL: https://api.tbresistancehub.org/v1/
Version: 1.0
Content-Type: application/json
```

## Authentication

### API Key Authentication

```http
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### Obtaining API Keys

1. Log into the TB Resistance Hub dashboard
2. Navigate to User Settings > API Access
3. Generate a new API key
4. Store the key securely (it won't be shown again)

### Authentication Example

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.tbresistancehub.org/v1/tb-cases
```

## Rate Limiting

- **Rate Limit**: 1000 requests per hour per API key
- **Burst Limit**: 100 requests per minute
- **Headers**: Rate limit information included in response headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Data Endpoints

### TB Cases

#### Get TB Cases

Retrieve tuberculosis case data with filtering and pagination.

```http
GET /v1/tb-cases
```

**Query Parameters:**

| Parameter          | Type    | Description                           | Example    |
| ------------------ | ------- | ------------------------------------- | ---------- |
| limit              | integer | Number of records (max 1000)          | 100        |
| offset             | integer | Pagination offset                     | 0          |
| start_date         | date    | Filter by diagnosis date (YYYY-MM-DD) | 2024-01-01 |
| end_date           | date    | Filter by diagnosis date (YYYY-MM-DD) | 2024-12-31 |
| location           | string  | Filter by geographic location         | "New York" |
| tb_type            | string  | Filter by TB classification           | "MDR-TB"   |
| resistance_pattern | string  | Filter by resistance pattern          | "INH+RIF"  |

**Example Request:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.tbresistancehub.org/v1/tb-cases?limit=50&tb_type=MDR-TB&start_date=2024-01-01"
```

**Response:**

```json
{
  "data": [
    {
      "id": 1,
      "patient_id": "TB2024001",
      "age": 45,
      "gender": "Male",
      "location": "New York",
      "country": "USA",
      "diagnosis_date": "2024-03-15",
      "tb_type": "MDR-TB",
      "resistance_pattern": "INH+RIF+EMB",
      "treatment_outcome": "Cured",
      "inh_resistant": true,
      "rif_resistant": true,
      "emb_resistant": true,
      "pza_resistant": false,
      "hiv_status": "Negative",
      "created_at": "2024-03-15T10:30:00Z"
    }
  ],
  "pagination": {
    "total": 1500,
    "limit": 50,
    "offset": 0,
    "has_next": true,
    "has_prev": false
  },
  "metadata": {
    "query_time": "0.123s",
    "filters_applied": ["tb_type", "start_date"]
  }
}
```

#### Create TB Case

Add a new tuberculosis case to the database.

```http
POST /v1/tb-cases
```

**Request Body:**

```json
{
  "patient_id": "TB2024002",
  "age": 35,
  "gender": "Female",
  "location": "Mumbai",
  "country": "IND",
  "diagnosis_date": "2024-06-16",
  "tb_type": "Drug-susceptible TB",
  "resistance_pattern": "None",
  "inh_resistant": false,
  "rif_resistant": false,
  "emb_resistant": false,
  "pza_resistant": false,
  "hiv_status": "Unknown",
  "culture_positive": true,
  "smear_positive": true
}
```

**Response:**

```json
{
  "id": 1501,
  "patient_id": "TB2024002",
  "status": "created",
  "created_at": "2024-06-16T14:22:00Z",
  "message": "TB case created successfully"
}
```

#### Update TB Case

Update an existing tuberculosis case.

```http
PUT /v1/tb-cases/{id}
```

**Request Body:**

```json
{
  "treatment_outcome": "Treatment Completed",
  "treatment_end_date": "2024-12-16"
}
```

#### Get TB Case by ID

Retrieve a specific tuberculosis case.

```http
GET /v1/tb-cases/{id}
```

**Response:**

```json
{
  "id": 1,
  "patient_id": "TB2024001",
  "age": 45,
  "gender": "Male",
  "location": "New York",
  "country": "USA",
  "diagnosis_date": "2024-03-15",
  "tb_type": "MDR-TB",
  "resistance_pattern": "INH+RIF+EMB",
  "treatment_outcome": "Cured",
  "treatment_start_date": "2024-03-20",
  "treatment_end_date": "2024-09-20",
  "inh_resistant": true,
  "rif_resistant": true,
  "emb_resistant": true,
  "pza_resistant": false,
  "hiv_status": "Negative",
  "previous_tb_treatment": false,
  "culture_positive": true,
  "smear_positive": true,
  "xpert_result": "MTB Detected/RIF Resistance",
  "dst_performed": true,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-09-20T16:45:00Z"
}
```

### Medical Terminology

#### Search Medical Terms

Search the medical terminology database.

```http
GET /v1/medical-terms
```

**Query Parameters:**

| Parameter | Type    | Description                 | Example    |
| --------- | ------- | --------------------------- | ---------- |
| q         | string  | Search query                | "MDR"      |
| category  | string  | Filter by category          | "tb_types" |
| limit     | integer | Number of results (max 100) | 10         |

**Example Request:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.tbresistancehub.org/v1/medical-terms?q=resistance&category=resistance_patterns"
```

**Response:**

```json
{
  "data": [
    {
      "id": 15,
      "category": "resistance_patterns",
      "term": "MDR-TB",
      "definition": "Multi-drug resistant tuberculosis (resistant to at least INH and RIF).",
      "synonyms": ["Multidrug-resistant TB", "MDR TB"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "suggestions": [
    "INH resistance",
    "RIF resistance",
    "Primary resistance",
    "Acquired resistance"
  ],
  "total": 1
}
```

#### Add Medical Term

Add a new medical term (requires admin privileges).

```http
POST /v1/medical-terms
```

**Request Body:**

```json
{
  "category": "drugs",
  "term": "Pretomanid",
  "definition": "Novel anti-TB drug that inhibits mycolic acid biosynthesis and respiratory poisoning.",
  "synonyms": ["PA-824"]
}
```

## Analytics Endpoints

### Resistance Statistics

Get aggregated resistance statistics.

```http
GET /v1/analytics/resistance-stats
```

**Query Parameters:**

| Parameter  | Type   | Description             | Example    |
| ---------- | ------ | ----------------------- | ---------- |
| start_date | date   | Start date for analysis | 2024-01-01 |
| end_date   | date   | End date for analysis   | 2024-12-31 |
| location   | string | Filter by location      | "India"    |
| group_by   | string | Group results by field  | "month"    |

**Response:**

```json
{
  "summary": {
    "total_cases": 1500,
    "drug_susceptible": 1200,
    "inh_resistant": 180,
    "rif_resistant": 150,
    "mdr_cases": 120,
    "xdr_cases": 25
  },
  "trends": [
    {
      "period": "2024-01",
      "total": 125,
      "mdr_rate": 8.0,
      "xdr_rate": 1.6
    },
    {
      "period": "2024-02",
      "total": 135,
      "mdr_rate": 8.9,
      "xdr_rate": 2.2
    }
  ],
  "by_location": [
    {
      "location": "New York",
      "total": 250,
      "mdr_rate": 6.4
    },
    {
      "location": "Mumbai",
      "total": 400,
      "mdr_rate": 12.5
    }
  ]
}
```

### Treatment Outcomes

Analyze treatment outcomes and success rates.

```http
GET /v1/analytics/treatment-outcomes
```

**Response:**

```json
{
  "overall_success_rate": 78.5,
  "by_tb_type": [
    {
      "tb_type": "Drug-susceptible TB",
      "total_cases": 1200,
      "success_rate": 85.2,
      "outcomes": {
        "cured": 720,
        "treatment_completed": 300,
        "failed": 60,
        "died": 45,
        "lost_to_followup": 75
      }
    },
    {
      "tb_type": "MDR-TB",
      "total_cases": 120,
      "success_rate": 62.5,
      "outcomes": {
        "cured": 45,
        "treatment_completed": 30,
        "failed": 25,
        "died": 10,
        "lost_to_followup": 10
      }
    }
  ]
}
```

### Geographic Distribution

Get geographic distribution of TB cases.

```http
GET /v1/analytics/geographic-distribution
```

**Response:**

```json
{
  "by_country": [
    {
      "country": "USA",
      "country_code": "US",
      "total_cases": 500,
      "mdr_rate": 3.2,
      "coordinates": {
        "lat": 39.8283,
        "lng": -98.5795
      }
    },
    {
      "country": "India",
      "country_code": "IN",
      "total_cases": 800,
      "mdr_rate": 15.6,
      "coordinates": {
        "lat": 20.5937,
        "lng": 78.9629
      }
    }
  ],
  "by_region": [
    {
      "region": "Americas",
      "total_cases": 600,
      "mdr_rate": 4.2
    },
    {
      "region": "South-East Asia",
      "total_cases": 900,
      "mdr_rate": 14.8
    }
  ]
}
```

## Clinical Decision Support

### Treatment Recommendations

Get treatment recommendations for a patient.

```http
POST /v1/clinical/treatment-recommendation
```

**Request Body:**

```json
{
  "patient_data": {
    "age": 45,
    "gender": "Male",
    "weight": 70,
    "resistance_pattern": "INH+RIF",
    "hiv_status": "Negative",
    "comorbidities": ["Diabetes"],
    "previous_tb_treatment": false
  }
}
```

**Response:**

```json
{
  "tb_type": "MDR-TB",
  "confidence": 0.95,
  "recommended_regimen": {
    "intensive_phase": {
      "duration_months": 8,
      "drugs": [
        {
          "name": "Bedaquiline",
          "dosage": "400mg daily for 2 weeks, then 200mg 3x/week",
          "route": "Oral"
        },
        {
          "name": "Levofloxacin",
          "dosage": "750mg daily",
          "route": "Oral"
        },
        {
          "name": "Clofazimine",
          "dosage": "100mg daily",
          "route": "Oral"
        },
        {
          "name": "Cycloserine",
          "dosage": "750mg daily (divided doses)",
          "route": "Oral"
        },
        {
          "name": "Ethambutol",
          "dosage": "1200mg daily",
          "route": "Oral"
        }
      ]
    },
    "continuation_phase": {
      "duration_months": 12,
      "drugs": [
        {
          "name": "Levofloxacin",
          "dosage": "750mg daily",
          "route": "Oral"
        },
        {
          "name": "Clofazimine",
          "dosage": "100mg daily",
          "route": "Oral"
        },
        {
          "name": "Cycloserine",
          "dosage": "750mg daily (divided doses)",
          "route": "Oral"
        },
        {
          "name": "Ethambutol",
          "dosage": "1200mg daily",
          "route": "Oral"
        }
      ]
    }
  },
  "monitoring": [
    "Monthly clinical assessment",
    "Quarterly audiometry (hearing tests)",
    "Monthly liver function tests",
    "ECG monitoring for QT prolongation"
  ],
  "special_considerations": [
    "Monitor blood glucose closely due to diabetes",
    "Consider vitamin B6 supplementation",
    "Ensure DOT (directly observed therapy)"
  ],
  "drug_interactions": [
    {
      "drug1": "Cycloserine",
      "drug2": "Alcohol",
      "severity": "Major",
      "description": "Increased risk of seizures"
    }
  ]
}
```

### Drug Interactions

Check for drug interactions.

```http
POST /v1/clinical/drug-interactions
```

**Request Body:**

```json
{
  "tb_drugs": ["Bedaquiline", "Levofloxacin"],
  "other_medications": ["Metformin", "Lisinopril"]
}
```

**Response:**

```json
{
  "interactions": [
    {
      "drug1": "Bedaquiline",
      "drug2": "Levofloxacin",
      "severity": "Moderate",
      "description": "Both drugs can prolong QT interval",
      "recommendation": "Monitor ECG regularly"
    }
  ],
  "total_interactions": 1,
  "severity_summary": {
    "major": 0,
    "moderate": 1,
    "minor": 0
  }
}
```

## Data Management

### Bulk Import

Import multiple TB cases in batch.

```http
POST /v1/import/tb-cases
```

**Request Body:**

```json
{
  "format": "json",
  "validate": true,
  "data": [
    {
      "patient_id": "BULK001",
      "age": 28,
      "gender": "Female",
      "location": "Delhi",
      "diagnosis_date": "2024-05-15",
      "tb_type": "Drug-susceptible TB"
    },
    {
      "patient_id": "BULK002",
      "age": 52,
      "gender": "Male",
      "location": "Delhi",
      "diagnosis_date": "2024-05-16",
      "tb_type": "INH-resistant TB"
    }
  ]
}
```

**Response:**

```json
{
  "import_id": "imp_20240616_001",
  "status": "completed",
  "summary": {
    "total_records": 2,
    "successful": 2,
    "failed": 0,
    "duplicates": 0
  },
  "created_ids": [1502, 1503],
  "errors": [],
  "processing_time": "0.456s"
}
```

### Export Data

Export TB cases in various formats.

```http
GET /v1/export/tb-cases
```

**Query Parameters:**

| Parameter | Type   | Description                      | Example           |
| --------- | ------ | -------------------------------- | ----------------- |
| format    | string | Export format (json, csv, excel) | csv               |
| fields    | string | Comma-separated field list       | id,patient_id,age |
| filters   | object | Same filters as GET /tb-cases    |                   |

**Response Headers:**

```http
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="tb_cases_20240616.csv"
```

## Webhooks

### Webhook Configuration

Configure webhooks for real-time notifications.

```http
POST /v1/webhooks
```

**Request Body:**

```json
{
  "url": "https://your-system.com/webhook/tb-updates",
  "events": ["case.created", "case.updated", "resistance.detected"],
  "secret": "your-webhook-secret",
  "active": true
}
```

### Webhook Events

Available webhook events:

- `case.created`: New TB case added
- `case.updated`: Existing case modified
- `case.deleted`: Case removed
- `resistance.detected`: New resistance pattern identified
- `outcome.updated`: Treatment outcome changed

**Webhook Payload Example:**

```json
{
  "event": "case.created",
  "timestamp": "2024-06-16T14:30:00Z",
  "data": {
    "id": 1504,
    "patient_id": "TB2024003",
    "tb_type": "MDR-TB",
    "location": "Bangkok"
  },
  "signature": "sha256=abc123..."
}
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "age",
        "message": "Age must be between 0 and 120"
      }
    ],
    "request_id": "req_20240616_001"
  }
}
```

### HTTP Status Codes

| Code | Description                             |
| ---- | --------------------------------------- |
| 200  | OK - Request successful                 |
| 201  | Created - Resource created              |
| 400  | Bad Request - Invalid input             |
| 401  | Unauthorized - Invalid API key          |
| 403  | Forbidden - Insufficient permissions    |
| 404  | Not Found - Resource doesn't exist      |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error - Server error    |

### Error Codes

| Code                     | Description                     |
| ------------------------ | ------------------------------- |
| INVALID_API_KEY          | API key is invalid or expired   |
| RATE_LIMIT_EXCEEDED      | Too many requests               |
| VALIDATION_ERROR         | Input validation failed         |
| RESOURCE_NOT_FOUND       | Requested resource not found    |
| DUPLICATE_RECORD         | Record already exists           |
| INSUFFICIENT_PERMISSIONS | User lacks required permissions |

## SDK and Libraries

### Python SDK

```python
from tb_resistance_hub import TBResistanceAPI

# Initialize client
client = TBResistanceAPI(api_key="your_api_key")

# Get TB cases
cases = client.tb_cases.list(limit=50, tb_type="MDR-TB")

# Create new case
new_case = client.tb_cases.create({
    "patient_id": "PY001",
    "age": 35,
    "gender": "Female",
    "location": "Mumbai",
    "tb_type": "Drug-susceptible TB"
})

# Get treatment recommendation
recommendation = client.clinical.get_treatment_recommendation({
    "age": 45,
    "resistance_pattern": "INH+RIF",
    "hiv_status": "Negative"
})
```

### JavaScript SDK

```javascript
import { TBResistanceAPI } from "tb-resistance-hub-js";

// Initialize client
const client = new TBResistanceAPI({
  apiKey: "your_api_key",
  baseURL: "https://api.tbresistancehub.org/v1",
});

// Get TB cases
const cases = await client.tbCases.list({
  limit: 50,
  tbType: "MDR-TB",
});

// Create new case
const newCase = await client.tbCases.create({
  patientId: "JS001",
  age: 35,
  gender: "Female",
  location: "Mumbai",
  tbType: "Drug-susceptible TB",
});
```

## API Testing

### Using cURL

```bash
# Test API connectivity
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.tbresistancehub.org/v1/health

# Create test case
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"patient_id":"TEST001","age":30,"gender":"Male","location":"Test City","tb_type":"Drug-susceptible TB"}' \
     https://api.tbresistancehub.org/v1/tb-cases
```

### Postman Collection

A Postman collection is available with pre-configured requests for all endpoints:

- Download: [TB Resistance Hub API.postman_collection.json]
- Import into Postman
- Set environment variable `api_key` with your API key

## Rate Limiting and Best Practices

### Efficient API Usage

1. **Batch Operations**: Use bulk import/export for large datasets
2. **Pagination**: Use appropriate page sizes (50-100 records)
3. **Filtering**: Apply filters to reduce response sizes
4. **Caching**: Cache responses when appropriate
5. **Compression**: Use gzip compression for large responses

### Retry Logic

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session
```
