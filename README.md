
---

# Njangi Group Manager

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://njangi.streamlit.app/)

A comprehensive web application for managing **Njangi groups** (rotating savings and credit associations) with automated payout scheduling, flexible assignment modes, and professional PDF report generation.

> ✨ **Try it live**: [https://njangi.streamlit.app/](https://njangi.streamlit.app/)

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Application Architecture](#application-architecture)
- [Database Schema](#database-schema)
- [PDF Report Structure](#pdf-report-structure)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **Njangi Group Manager** is a Streamlit-based web application designed to simplify the administration of traditional rotating savings and credit associations (ROSCAs), commonly known as *Njangi* in parts of Africa.

It solves real-world challenges such as:
- Manual errors in payout calculations
- Participant tracking (especially with duplicate names)
- Lack of professional documentation
- Loss of group data between meetings
- Inflexible assignment strategies

The app uses a **fruit-based identification system** to uniquely map participants—ensuring clarity during physical fruit-picking sessions—while generating polished, printable PDF reports for transparency and record-keeping.

---

## Features

### Core Functionality
- ✅ **Multi-group management** with persistent SQLite storage  
- 📊 **Automated payout scheduling** based on contributions, group size, and duration  
- 🍎 **Unique fruit assignment** per participant (110+ fruits available)  
- 📄 **Professional PDF reports** with schedules, summaries, and rules  
- 💾 **Auto-save & load** of group progress  

### Advanced Capabilities
- **Three assignment modes**:
  - **Automatic**: Fully random assignment at PDF generation
  - **Manual**: Full user control over who gets paid when
  - **Semi-Automatic**: Lock key participants, auto-fill the rest
- **Duplicate name handling**: UI shows `Name [1]`, `Name [2]` for clarity—but PDFs preserve original names
- **Real-time validation**: Prevents duplicate fruits, over-assignments, or invalid group sizes
- **Loan & interest support**: Optional interest-bearing loans with configurable rates and terms
- **Custom group rules**: Add your own bylaws (e.g., penalties, attendance policies)
- **Responsive tabbed interface**: Clean UX across desktop and tablet

---

## Installation

### Prerequisites
- Python 3.8+
- `pip`

### Setup
```bash
# Clone (if hosted on GitHub)
git clone https://github.com/your-username/njangi-group-manager.git
cd njangi-group-manager

# Install dependencies
pip install streamlit reportlab

# Run the app
streamlit run app.py
```

> 💡 **Note**: The script includes a self-launcher. You can also run `python app.py`, and it will auto-start the Streamlit server.

The app opens at: `http://localhost:8501`

---

## Usage

### Step-by-Step Workflow

1. **Group Setup**  
   - Enter group name, size (1–110), monthly contribution (FCFA), duration (months), and start date.
   - View auto-calculated metrics: monthly pool, individual payout, total collected.

2. **Participants & Fruits**  
   - Add participant names (or auto-generate as "Member 1", etc.)
   - Assign unique fruits from a curated list of 110+ global fruits
   - Use “Random Fruits” or “Auto-name” for quick setup

3. **Payout Assignment**  
   Choose a mode:
   - **Automatic**: No input needed—randomized at PDF time
   - **Manual/Semi-Auto**: Drag-and-drop participants into months using a multiselect UI
   - See real-time counts of assigned/unassigned members

4. **Add Rules (Optional)**  
   - Define group bylaws (e.g., “Late fee: 500 FCFA”)

5. **Enable Loans (Optional)**  
   - Toggle interest-based lending
   - Set annual interest rate (%) and loan duration (months)

6. **Generate Report**  
   - Click **Generate PDF Report**
   - Download a branded, multi-page PDF with:
     - Fruit list
     - Participant-to-fruit mapping
     - Monthly payout schedule
     - Financial summary
     - Rules & loan details (if enabled)

---

## Application Architecture

### Key Classes
- **`DatabaseManager`**: Handles SQLite CRUD operations with schema migration support
- **`Njangi`**: Core logic for payout calculations, assignment modes, and PDF generation
- **Streamlit UI**: 6-tab interface with session state management

### Assignment Logic
- **Fruit uniqueness** is enforced via real-time dropdown filtering
- **Manual assignments** store participant *indices* (not names)—robust to name changes
- **Semi-auto mode** locks user selections and fills gaps randomly at PDF time

### PDF Engine
- Built with **ReportLab**
- Includes watermark, header/footer, color-coded tables, and page breaks
- Outputs clean, print-ready documents

---

## Database Schema

### `njangi_groups`
| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `name` | TEXT | Unique group name |
| `size`, `loan`, `time` | INTEGER | Core parameters |
| `base` | INTEGER | Payout = `loan × time` |
| `start_month`, `start_year` | INTEGER | Cycle start |
| `participants`, `fruits` | TEXT (JSON) | Arrays of strings |
| `manual_assignments` | TEXT (JSON) | `{ "month_0": [2,5], ... }` |
| `rules` | TEXT | Custom group rules |
| `has_loans`, `interest_rate`, `loan_duration` | Flags & numbers | Loan settings |
| `created_at`, `updated_at` | TIMESTAMP | Audit trail |

### `njangi_sessions`  
*(Reserved for future use—currently unused in UI)*

---

## PDF Report Structure

Each report includes:
1. **Cover**: Group name, period, contribution info  
2. **Fruit Sheet**: List of all assigned fruits (for physical distribution)  
3. **Participants & Fruits**: Table linking names to fruits + monthly payout columns  
4. **Payout Schedule**: Month-by-month breakdown of:
   - Collections
   - Available funds
   - Payout count
   - Recipient names (original only)
   - Residue
5. **Rules Section** (if provided)  
6. **Loan Summary** (if enabled)  
7. **Financial Summary**: Totals, residue, potential interest

> 🎨 All PDFs include a subtle “auto-generated” watermark and Team [zeru] branding.

---

## Configuration

### Customize Easily
- **Fruits**: Edit the `fruits_master` list in `app.py`
- **Branding**: Modify header/footer in `generate_pdf()`
- **Styling**: Adjust colors, fonts, and spacing in ReportLab styles
- **DB Path**: Change `db_name` in `DatabaseManager` init

---

## Contributing

We welcome contributions! Please:
1. Fork the repo
2. Create a feature branch
3. Write clear, PEP-8-compliant code
4. Test thoroughly
5. Submit a PR

> 🐞 Found a bug? Open an issue with steps to reproduce.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built with ❤️ using **Streamlit**, **ReportLab**, and **SQLite**
- Inspired by traditional African ROSCA systems
- Fruit list curated from global agricultural sources

---

**Developed by Team [zeru]**  
*“steady – calm – driven”*

🔗 **Live Demo**: [https://njangi.streamlit.app/](https://njangi.streamlit.app/)

--- 

This README accurately reflects all features in your code—including semi-automatic mode, duplicate name handling, loan interest, fruit constraints, PDF structure, and database design—while providing clear installation and usage guidance.
