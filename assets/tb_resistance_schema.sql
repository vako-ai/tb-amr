-- TB Resistance Hub Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL,
    last_login TEXT
);

-- TB cases table
CREATE TABLE IF NOT EXISTS tb_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT,
    age INTEGER,
    gender TEXT,
    location TEXT,
    diagnosis_date TEXT,
    tb_type TEXT,
    resistance_pattern TEXT,
    treatment_regimen TEXT,
    treatment_start_date TEXT,
    treatment_end_date TEXT,
    treatment_outcome TEXT,
    hiv_status TEXT,
    comorbidities TEXT,
    created_by INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Resistance details table for drug-specific resistance data
CREATE TABLE IF NOT EXISTS resistance_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER,
    drug_name TEXT,
    is_resistant INTEGER,
    test_method TEXT,
    test_date TEXT,
    FOREIGN KEY (case_id) REFERENCES tb_cases (id)
);

-- Patient data for clinical decision support
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT UNIQUE,
    data TEXT,
    created_at TEXT,
    last_updated TEXT
);

-- Sharing preferences for global collaboration
CREATE TABLE IF NOT EXISTS sharing_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    data_elements TEXT,
    anonymization_level TEXT,
    regions_allowed TEXT,
    auto_update INTEGER,
    sharing_token TEXT UNIQUE,
    created_at TEXT,
    last_updated TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Collaboration requests table
CREATE TABLE IF NOT EXISTS collaboration_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER,
    provider_token TEXT,
    request_date TEXT,
    response_date TEXT,
    status TEXT,
    FOREIGN KEY (requester_id) REFERENCES users (id),
    FOREIGN KEY (provider_token) REFERENCES sharing_preferences (sharing_token)
);

-- Activity log table for audit trail
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    activity_type TEXT,
    details TEXT,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Models table for machine learning models
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    model_type TEXT,
    created_by INTEGER,
    created_at TEXT,
    file_path TEXT,
    metrics TEXT,
    is_active INTEGER DEFAULT 0,
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_tb_cases_patient_id ON tb_cases(patient_id);
CREATE INDEX IF NOT EXISTS idx_tb_cases_tb_type ON tb_cases(tb_type);
CREATE INDEX IF NOT EXISTS idx_tb_cases_location ON tb_cases(location);
CREATE INDEX IF NOT EXISTS idx_tb_cases_diagnosis_date ON tb_cases(diagnosis_date);
CREATE INDEX IF NOT EXISTS idx_resistance_details_case_id ON resistance_details(case_id);
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_sharing_preferences_user_id ON sharing_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_sharing_preferences_token ON sharing_preferences(sharing_token);
CREATE INDEX IF NOT EXISTS idx_collaboration_requests_provider ON collaboration_requests(provider_token);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_timestamp ON activity_log(timestamp);

-- Comments on key tables
PRAGMA table_info(tb_cases); -- Main table for TB case data
PRAGMA table_info(resistance_details); -- Detailed drug resistance information
PRAGMA table_info(patients); -- Patient data for clinical decision support
PRAGMA table_info(sharing_preferences); -- Data sharing preferences for global collaboration
