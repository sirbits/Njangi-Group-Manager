# Njangi Group Manager

A comprehensive web application for managing Njangi groups (rotating savings and credit associations) with automated payout scheduling and professional PDF report generation.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Application Architecture](#application-architecture)
- [Database Schema](#database-schema)
- [PDF Report Structure](#pdf-report-structure)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Overview

Njangi Group Manager is a Streamlit-based web application designed to streamline the administration of traditional rotating savings and credit associations (ROSCAs). The application automates complex payout calculations, manages participant assignments through a unique fruit-based identification system, and generates comprehensive PDF reports for group transparency and record-keeping.

The application addresses common challenges in Njangi group management including:
- Manual calculation errors in payout schedules
- Participant tracking and assignment conflicts
- Professional documentation and reporting
- Data persistence and group configuration management

## Features

### Core Functionality
- **Multi-Group Management**: Create, persist, and manage multiple Njangi groups simultaneously
- **Intelligent Payout Scheduling**: Automated calculation of monthly collections, payouts, and residue management
- **Unique Participant Assignment**: Fruit-based identification system with conflict prevention
- **Professional PDF Reports**: Multi-section reports with detailed schedules, summaries, and branding
- **Data Persistence**: SQLite-based storage for group configurations and historical data

### Advanced Features
- **Interactive Fruit Assignment**: Real-time constraint validation preventing duplicate assignments
- **Flexible Group Parameters**: Configurable group sizes, contribution amounts, and cycle durations
- **Comprehensive Validation**: Input validation with user feedback and error prevention
- **Responsive Design**: Clean, tabbed interface optimized for various screen sizes
- **Auto-save Functionality**: Automatic progress saving with conflict resolution

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies
Install the required packages using pip:

```bash
pip install streamlit
pip install reportlab
pip install sqlite3
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd njangi-group-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Launch the application:
```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

### Alternative Launch Method
The application includes automatic Streamlit launcher functionality. You can also run:
```bash
python app.py
```

This will automatically detect the runtime environment and launch the Streamlit server with proper environment configuration.

## Usage

### Application Workflow

#### 1. Group Setup
Configure fundamental group parameters:
- **Group Name**: Unique identifier for the Njangi group
- **Participant Count**: Number of group members (1 to 110 maximum)
- **Monthly Contribution**: Individual contribution amount in FCFA
- **Duration**: Cycle length in months
- **Start Date**: Beginning month and year for the group cycle

The application provides real-time calculation of:
- Monthly total collection
- Individual payout amounts
- Total pool value

#### 2. Participant Management
Manage group members and assignments:
- **Participant Entry**: Individual name input with auto-completion
- **Fruit Assignment**: Unique fruit identifier assignment with conflict prevention
- **Bulk Operations**: Random assignment and auto-naming utilities
- **Progress Saving**: Incremental save functionality

The fruit assignment system ensures:
- No duplicate fruit assignments
- Interactive reassignment when conflicts occur
- Visual feedback for assignment status

#### 3. Report Generation
Create professional documentation:
- **Validation Checks**: Comprehensive input validation
- **Summary Preview**: Pre-generation group metrics review
- **PDF Creation**: Professional multi-section reports
- **Download Management**: Secure file download with custom naming

## Application Architecture

### Core Components

#### DatabaseManager Class
Handles all database operations including:
- SQLite database initialization
- Group CRUD operations
- Session management
- Data serialization/deserialization

#### Njangi Class
Core business logic implementation:
- Payout calculation algorithms
- Schedule generation
- PDF report compilation
- Participant management with duplicate handling

#### Streamlit Interface
Multi-tab interface providing:
- Session state management
- Form validation and user feedback
- Interactive components with real-time updates
- File download capabilities

### Key Algorithms

#### Unique Participant Handling
The application implements sophisticated duplicate name handling:
- Internal unique identifier generation
- Display name preservation for PDF output
- Conflict resolution in payout assignments

#### Fruit Assignment Logic
Interactive constraint system ensuring:
- Real-time validation of unique assignments
- Automatic reassignment cascade when conflicts occur
- Preservation of user selections where possible

## Database Schema

### njangi_groups Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Unique group identifier |
| name | TEXT UNIQUE NOT NULL | Group name |
| size | INTEGER NOT NULL | Number of participants |
| loan | INTEGER NOT NULL | Monthly contribution amount |
| time | INTEGER NOT NULL | Duration in months |
| base | INTEGER | Payout amount per participant |
| start_month | INTEGER | Starting month (1-12) |
| start_year | INTEGER | Starting year |
| participants | TEXT | JSON array of participant names |
| fruits | TEXT | JSON array of assigned fruits |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last modification timestamp |

### njangi_sessions Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Session identifier |
| group_id | INTEGER | Foreign key to njangi_groups |
| session_data | TEXT | JSON session information |
| created_at | TIMESTAMP | Session creation time |

## PDF Report Structure

Generated reports include five main sections:

1. **Title Section**: Group identification and period information
2. **Assigned Fruits Table**: Complete list of fruit identifiers
3. **Participants & Fruits Table**: Member details with monthly tracking columns
4. **Payout Schedule Table**: Detailed monthly breakdown including:
   - Monthly collections
   - Available funds
   - Number of payouts
   - Recipient names
   - Residue calculations
5. **Summary Section**: Financial totals and key metrics

### Report Features
- Professional branding with headers/footers
- Color-coded tables for easy reading
- Automatic page breaks and formatting
- Watermark protection
- Comprehensive financial summaries

## Configuration

### Customization Options

#### Fruit Master List
Modify the `fruits_master` list to customize available fruits:
```python
fruits_master = [
    'custom_fruit_1', 'custom_fruit_2', ...
]
```

#### Database Configuration
Change database location by modifying the DatabaseManager initialization:
```python
db_manager = DatabaseManager("custom_database_name.db")
```

#### PDF Styling
Customize report appearance in the `generate_pdf()` method:
- Color schemes and themes
- Table layouts and column widths
- Font styles and sizes
- Header/footer content

#### Financial Calculations
Modify calculation formulas in the Njangi class:
- Base payout calculations
- Residue handling logic
- Collection algorithms

## API Reference

### DatabaseManager Methods
- `init_database()`: Initialize database schema
- `save_group()`: Persist group configuration
- `load_group()`: Retrieve group data
- `get_all_groups()`: List all saved groups
- `delete_group()`: Remove group from database

### Njangi Methods
- `monthly_collection()`: Calculate monthly total
- `pool()`: Calculate total pool value
- `generate_pdf()`: Create comprehensive report

### Session State Variables
- `current_group_data`: Active group configuration
- `participants`: Participant name list
- `fruits`: Assigned fruit list
- `fruit_keys`: Fruit assignment tracking

## Development

### Code Structure
```
app.py                  # Main application file
├── DatabaseManager     # Database operations class
├── Njangi             # Core business logic class
├── Session Management # Streamlit state management
└── UI Components      # Interface tabs and forms
```

### Testing
Run the application in development mode:
```bash
streamlit run app.py --server.runOnSave true
```

### Debugging
Enable debug mode with:
```bash
streamlit run app.py --server.enableXsrfProtection false --server.enableCORS false
```

## Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings for all methods
- Include type hints where appropriate
- Maintain backward compatibility

### Issue Reporting
Please report issues with:
- Detailed reproduction steps
- System environment information
- Expected vs. actual behavior
- Screenshots if applicable

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with Streamlit for rapid web application development
- ReportLab for professional PDF generation
- SQLite for reliable data persistence
- Designed for Njangi communities worldwide

---

**Developed by Team [zeru] - "steady - calm - driven"**
