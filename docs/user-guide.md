# User Guide - TB Resistance Hub

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Medical Search](#medical-search)
4. [Analytics](#analytics)
5. [Clinical Decision Support](#clinical-decision-support)
6. [Data Management](#data-management)
7. [Global Collaboration](#global-collaboration)
8. [User Settings](#user-settings)
9. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Screen resolution: 1024x768 minimum (1920x1080 recommended)

### First Time Login

1. Navigate to the TB Resistance Hub web address
2. Enter your username and password
3. Complete the onboarding process if this is your first login

**Default Login Credentials**:

- Username: `admin`
- Password: `admin123`

### User Onboarding

When you first log in, you'll be guided through a personalized setup process:

1. **Role Selection**: Choose your primary role (Clinician, Researcher, Administrator, Public Health Officer)
2. **Interests**: Select your areas of focus (MDR-TB, XDR-TB, Pediatric TB, etc.)
3. **Data Focus**: Specify your primary data interests (Treatment Outcomes, Resistance Patterns, Epidemiology)
4. **Experience Level**: Indicate your TB expertise (Beginner, Intermediate, Expert)
5. **Preferred Features**: Select which platform sections you use most frequently

This information personalizes your experience and provides relevant guidance throughout the platform.

## Dashboard Overview

The main dashboard is organized into six tabs, each serving specific functions:

### Overview Tab

The Overview tab provides a high-level summary of TB resistance data:

#### Key Metrics Cards

- **Total Cases**: Number of TB cases in the database
- **MDR-TB Cases**: Count of multi-drug resistant cases
- **Treatment Success Rate**: Percentage of successful treatment outcomes
- **Recent Cases**: Cases reported in the past 90 days

#### Visualizations

- **Treatment Outcomes Chart**: Shows treatment success rates by TB type
- **Geographical Distribution Map**: Displays case distribution by location

### Navigation Tips

- Use the tabs at the top to switch between different sections
- Look for the help icon (?) for contextual assistance
- Access feature tours from the sidebar for guided walkthroughs

## Medical Search

The Medical Search feature provides intelligent search capabilities for TB-related terminology.

### Using the Search Interface

#### Basic Search

1. Click on the "Medical Search" tab
2. Type your search term in the search box
3. Results appear automatically as you type
4. Click on any result to view the full definition

#### Autocomplete Suggestions

- Start typing any medical term (minimum 2 characters)
- Suggestions appear below the search box
- Click on a suggestion to select it
- Fuzzy matching helps find terms even with slight misspellings

#### Category Filtering

1. Use the "Category" dropdown to filter results
2. Available categories:
   - **TB Types**: Classifications like MDR-TB, XDR-TB
   - **Medications**: Anti-TB drugs and their properties
   - **Side Effects**: Adverse reactions and monitoring
   - **Diagnostic Terms**: Laboratory tests and procedures
   - **Resistance Patterns**: Specific resistance classifications

#### Search Examples

- Search for "MDR" to find multi-drug resistance information
- Type "isoniazid" to learn about this first-line TB drug
- Search "hepatotoxicity" for liver-related side effects
- Look up "GeneXpert" for molecular diagnostic information

### Managing Medical Terms (Admin Only)

Administrators can add new medical terms:

1. Scroll to the bottom of the Medical Search page
2. Fill out the "Add New Medical Term" form:
   - Select the appropriate category
   - Enter the term name
   - Provide a comprehensive definition
3. Click "Add Term" to save

## Analytics

The Analytics tab provides comprehensive data analysis and visualization tools.

### Resistance Trends

- **Time Series Charts**: View resistance patterns over time
- **Trend Lines**: Identify increasing or decreasing resistance rates
- **Interactive Controls**: Filter by date range, location, or TB type

### Drug Resistance Patterns

- **Heatmap Visualization**: Shows resistance intensity across different drugs
- **Pattern Analysis**: Identifies common resistance combinations
- **Comparative Views**: Compare resistance patterns between regions

### Top Resistance Patterns

- **Ranked List**: Most common resistance patterns in your dataset
- **Frequency Analysis**: How often each pattern occurs
- **Clinical Significance**: Impact on treatment decisions

### Using Analytics Tools

1. Select the time period you want to analyze
2. Choose specific locations or populations if needed
3. Use the interactive charts to drill down into specific data points
4. Export charts and data for presentations or reports

## Clinical Decision Support

The Clinical Decision Support system helps healthcare providers make informed treatment decisions.

### Patient Assessment Form

#### Basic Information

- **Patient Age**: Enter age in years
- **Gender**: Select Male, Female, or Other
- **Weight**: Enter weight in kilograms (used for dosing calculations)

#### Clinical Data

- **Resistance Pattern**: Select from dropdown menu
  - None (drug-susceptible TB)
  - INH (isoniazid resistance only)
  - RIF (rifampicin resistance)
  - INH+RIF (multi-drug resistance)
  - More complex patterns available
- **HIV Status**: Positive, Negative, or Unknown
- **Comorbidities**: Select all applicable conditions

#### Treatment Recommendations

After entering patient data, click "Generate Recommendation" to receive:

1. **TB Type Classification**: Automatic classification based on resistance pattern
2. **Recommended Drug Regimen**: Specific medications and dosages
3. **Treatment Duration**: Expected length of treatment
4. **Special Considerations**: Important notes about the patient's specific situation

### Interpreting Recommendations

- **Standard Regimens**: Follow WHO guidelines for drug-susceptible TB
- **Modified Regimens**: Adjusted for resistance patterns or comorbidities
- **Monitoring Requirements**: Specific tests or follow-up needed
- **Drug Interactions**: Potential conflicts with other medications

### Clinical Notes and Warnings

Pay attention to:

- Age-specific dosing adjustments
- Contraindications based on comorbidities
- Monitoring requirements for specific drugs
- Expected duration variations

## Data Management

The Data Management section handles importing, exporting, and viewing TB data.

### Importing Data

#### CSV File Import

1. Go to the "Data Management" tab
2. Select "Import Data" sub-tab
3. Choose "CSV File" from the dropdown
4. Click "Upload CSV File" and select your file
5. Review the data preview
6. Click "Process Data" to import

#### Excel File Import

1. Select "Excel File" as the import source
2. Upload files with .xlsx or .xls extensions
3. Choose the appropriate worksheet if multiple sheets exist
4. Map columns to database fields
5. Validate and import the data

#### API Data Import

1. Select "API" as the import source
2. Enter the API URL
3. Provide authentication credentials if required
4. Configure data mapping settings
5. Test the connection and import data

### Exporting Data

#### Export Options

1. Navigate to the "Export Data" sub-tab
2. Choose export format (CSV, Excel, or JSON)
3. Select the table to export
4. Choose specific fields to include (optional)
5. Click "Export Data" to generate the file

#### Bulk Export

- Export entire datasets for backup or analysis
- Include metadata and data quality indicators
- Generate reports in multiple formats
- Schedule regular automated exports

### Database Tables View

- **Sample Data Display**: View representative records from each table
- **Data Quality Metrics**: Completeness and accuracy indicators
- **Record Counts**: Total number of records in each table
- **Last Update Information**: When data was last modified

## Global Collaboration

The Global Collaboration feature connects TB programs and researchers worldwide.

### Research Opportunities

#### Viewing Available Projects

1. Go to the "Collaboration" tab
2. Browse current research opportunities
3. Each project shows:
   - Project title and lead organization
   - Application deadline
   - Project description and requirements
   - Contact information

#### Expressing Interest

1. Click "Express Interest" on relevant projects
2. Provide your organization details
3. Describe your potential contribution
4. Submit your expression of interest
5. Await contact from the project organizers

### Data Sharing

#### Configuring Sharing Settings

1. Choose your data sharing level using the slider:
   - **No Sharing**: Keep data private
   - **Minimal Sharing**: Basic aggregated statistics only
   - **Moderate Sharing**: Anonymized case-level data
   - **Full Sharing**: Complete data with full anonymization

#### Data Elements Selection

Choose which types of data to share:

- **Resistance Patterns**: Drug susceptibility test results
- **Treatment Outcomes**: Success rates and failure patterns
- **Geographic Data**: Regional distribution information
- **Demographic Data**: Age and gender distributions

#### Privacy and Security

- All shared data is automatically anonymized
- Patient identifiers are removed or encrypted
- Geographic data is aggregated to protect privacy
- Sharing agreements include data use restrictions

### Available Shared Datasets

- View datasets shared by other organizations
- Filter by organization, data type, or geographic region
- Request access to specific datasets
- Contribute to collaborative research projects

## User Settings

### Account Management

#### Updating Profile Information

1. Click on your username in the sidebar
2. Select "Profile Settings"
3. Update your:
   - Full name and contact information
   - Organization affiliation
   - Professional role and expertise areas
   - Notification preferences

#### Changing Password

1. Go to Account Settings
2. Enter your current password
3. Provide a new secure password
4. Confirm the password change
5. You'll be prompted to log in again

### Customizing Your Experience

#### Dashboard Preferences

- Rearrange dashboard widgets
- Choose default time periods for charts
- Set preferred geographic regions
- Configure alert thresholds

#### Notification Settings

- Email notifications for system updates
- In-app alerts for new research opportunities
- Data quality alerts for your submissions
- Collaboration request notifications

### Data Preferences

#### Default Filters

- Set default date ranges for analysis
- Choose preferred geographic focus areas
- Configure default patient population filters
- Set standard export formats

#### Quality Thresholds

- Define minimum data quality requirements
- Set completeness thresholds for analysis
- Configure accuracy requirements
- Establish consistency validation rules

## Troubleshooting

### Common Issues and Solutions

#### Login Problems

**Issue**: Can't log in with provided credentials
**Solution**:

1. Verify username and password are entered correctly
2. Check if Caps Lock is enabled
3. Clear browser cookies and cache
4. Try a different browser
5. Contact your system administrator

#### Slow Performance

**Issue**: Pages load slowly or timeout
**Solution**:

1. Check your internet connection
2. Close unnecessary browser tabs
3. Clear browser cache
4. Try during off-peak hours
5. Use Chrome or Firefox for best performance

#### Data Import Errors

**Issue**: File upload fails or data doesn't import correctly
**Solution**:

1. Verify file format matches requirements
2. Check file size limits (maximum 100MB)
3. Ensure all required fields are present
4. Validate data formats (dates, numbers)
5. Review error messages for specific issues

#### Search Not Working

**Issue**: Medical search doesn't return expected results
**Solution**:

1. Check spelling of search terms
2. Try alternative terms or synonyms
3. Use category filters to narrow results
4. Clear search filters and try again
5. Contact support if terms are missing

#### Chart Display Issues

**Issue**: Visualizations don't display or appear broken
**Solution**:

1. Refresh the page
2. Check if JavaScript is enabled
3. Update your browser to the latest version
4. Disable browser extensions temporarily
5. Try a different browser

### Getting Help

#### Built-in Help System

- Click the help icon (?) for contextual assistance
- Use the "Feature Tour" for guided walkthroughs
- Access the FAQ section for common questions
- View video tutorials for complex features

#### Contacting Support

- Use the "Get Help" button in the sidebar
- Submit support tickets through the help system
- Include specific error messages and screenshots
- Provide details about your browser and operating system

#### User Community

- Join monthly user webinars
- Participate in user forums
- Share best practices with other users
- Contribute to documentation improvements

### System Requirements Check

#### Browser Compatibility

- **Chrome**: Version 90 or higher
- **Firefox**: Version 88 or higher
- **Safari**: Version 14 or higher
- **Edge**: Version 90 or higher

#### Network Requirements

- Stable internet connection (minimum 1 Mbps)
- Unrestricted access to the application domain
- JavaScript enabled
- Cookies enabled for the application domain

#### Display Requirements

- Minimum resolution: 1024x768
- Recommended resolution: 1920x1080 or higher
- Color depth: 16-bit minimum, 32-bit recommended

### Data Quality Guidelines

#### Best Practices for Data Entry

1. **Completeness**: Fill all required fields
2. **Accuracy**: Double-check critical information
3. **Consistency**: Use standardized formats and terminology
4. **Timeliness**: Enter data promptly after patient encounters
5. **Validation**: Review data before submission

#### Common Data Quality Issues

- Missing required fields
- Inconsistent date formats
- Invalid resistance patterns
- Duplicate patient entries
- Incomplete treatment outcome data

This user guide provides comprehensive instructions for effectively using all features of the TB Resistance Hub platform. For additional assistance, use the built-in help system or contact your system administrator.
