# 💰 Njangi Group Manager

A comprehensive Streamlit application for managing and generating professional reports for Njangi groups (rotating savings and credit associations).

## 📋 Overview

Njangi Group Manager simplifies the management of traditional rotating savings groups by automatically calculating payouts, tracking participants, and generating professional PDF reports with detailed schedules and summaries.

## ✨ Features

### Core Functionality
- **Group Management**: Create, save, load, and delete multiple Njangi groups
- **Participant Management**: Add and manage group members with unique fruit assignments
- **Automatic Calculations**: Calculate monthly collections, payouts, and schedules
- **Professional Reports**: Generate detailed PDF reports with schedules and summaries

### Advanced Features
- **Unique Fruit Assignment**: Interactive fruit assignment system preventing duplicates
- **Flexible Scheduling**: Customizable start dates and duration
- **Data Persistence**: SQLite database for storing group configurations
- **Multi-table Reports**: Comprehensive PDF reports with fruit assignments, participant details, and payout schedules

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Dependencies
```bash
pip install streamlit
pip install reportlab
pip install sqlite3  # Usually included with Python
```

### Quick Start
1. Clone or download the application
2. Install dependencies
3. Run the application:
```bash
python app.py
```

The application will automatically launch Streamlit and open in your default browser.

## 📖 Usage Guide

### 1. Group Setup Tab
Configure basic group information:
- **Group Name**: Unique identifier for your Njangi group
- **Participants**: Number of group members (1-100+)
- **Monthly Contribution**: Amount each member contributes (in FCFA)
- **Duration**: Length of the cycle in months
- **Start Date**: Month and year when the group begins

### 2. Participants Tab
Manage group members and fruit assignments:
- **Add Participants**: Enter names for each group member
- **Fruit Assignment**: Each participant gets a unique fruit identifier
- **Auto-Assignment**: Use random assignment or manual selection
- **Quick Actions**: Bulk operations for participants and fruits

### 3. Generate Tab
Create and download professional reports:
- **Validation**: Automatic checks for data completeness
- **Summary Preview**: Review group metrics before generation
- **PDF Generation**: Create comprehensive reports
- **Download**: Get your professional PDF report

## 🔧 Technical Details

### Database Schema
The application uses SQLite with two main tables:

#### njangi_groups
- `id`: Primary key
- `name`: Group name (unique)
- `size`: Number of participants
- `loan`: Monthly contribution amount
- `time`: Duration in months
- `base`: Payout amount per person
- `start_month`/`start_year`: Start date
- `participants`: JSON array of participant names
- `fruits`: JSON array of assigned fruits
- `created_at`/`updated_at`: Timestamps

#### njangi_sessions
- `id`: Primary key
- `group_id`: Foreign key to njangi_groups
- `session_data`: JSON session information
- `created_at`: Timestamp

### PDF Report Structure
Generated reports include:
1. **Title Page**: Group name and period information
2. **Assigned Fruits Table**: List of all fruits used
3. **Participants & Fruits Table**: Member details with monthly tracking
4. **Payout Schedule**: Detailed monthly breakdown with collections and payouts
5. **Summary Section**: Key metrics and totals

### Calculation Logic
- **Monthly Collection**: `participants × monthly_contribution`
- **Total Pool**: `monthly_collection × duration`
- **Payout per Person**: `monthly_contribution × duration`
- **Residue Management**: Automatic handling of remaining funds

## 🎯 Key Features Explained

### Unique Fruit Assignment System
The application ensures each participant gets a unique fruit identifier:
- Interactive dropdown selection
- Automatic reassignment when conflicts occur
- Visual feedback for duplicate prevention
- Random assignment option available

### Flexible Group Configurations
- Support for groups of varying sizes
- Customizable contribution amounts
- Flexible duration settings
- Multiple start date options

### Professional PDF Reports
- Branded headers and footers
- Color-coded tables
- Automatic page breaks
- Watermark protection
- Summary calculations

## 📁 File Structure
```
njangi_app.py           # Main application file
njangi_groups.db        # SQLite database (auto-created)
generated_reports/      # PDF output directory (auto-created)
```

## 🔧 Configuration Options

### Database Configuration
Default database name: `njangi_groups.db`
- Modify `DatabaseManager.__init__()` to change database location

### PDF Styling
Customize report appearance by modifying:
- Color schemes in `generate_pdf()` method
- Table layouts and column widths
- Header and footer designs
- Font styles and sizes

### Fruit Master List
The application includes 100+ fruit names. Modify `fruits_master` list to:
- Add regional fruits
- Remove unwanted options
- Customize for specific cultures

## 🚀 Advanced Usage

### Bulk Group Management
- Import/export group configurations
- Batch operations for multiple groups
- Historical group tracking

### Custom Calculations
- Modify base calculation formulas
- Add interest calculations
- Implement penalty systems

### Report Customization
- Add company logos
- Customize report layouts
- Include additional metrics

## 🛠️ Troubleshooting

### Common Issues
1. **Database Connection**: Ensure write permissions in application directory
2. **PDF Generation**: Check ReportLab installation and dependencies
3. **Streamlit Startup**: Verify Python and Streamlit installation

### Error Messages
- **"size >= time"**: Ensure participant count meets or exceeds duration
- **"Duplicate fruits"**: Check fruit assignment system
- **"Group name exists"**: Use unique names or update existing group

## 📈 Performance Considerations
- SQLite database handles thousands of groups efficiently
- PDF generation optimized for groups up to 100 participants
- Memory usage scales linearly with group size

## 🔮 Future Enhancements
- Multi-language support
- Mobile-responsive interface
- Cloud database integration
- Advanced reporting analytics
- Email report distribution
- WhatsApp integration

## 📝 License
This project is open source and available under standard software licenses.

## 🤝 Contributing
Contributions welcome! Please feel free to submit pull requests or report issues.

## 📞 Support
For technical support or feature requests, please create an issue in the project repository.

---

**Built with ❤️ for Njangi communities worldwide**
