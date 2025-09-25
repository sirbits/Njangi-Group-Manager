import random, sys, os, subprocess
import streamlit as st
import sqlite3
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

fruits_master = [
    'ackee', 'apple', 'apricot', 'avocado', 'banana', 'baobab', 'black sapote',
    'blackberry', 'blueberry', 'boysenberry', 'breadfruit', 'cantaloupe', 'carambola',
    'cherimoya', 'cherry', 'clementine', 'coconut', 'cranberry', 'custard apple',
    'date', 'dragonfruit', 'durian', 'elderberry', 'feijoa', 'fig', 'gooseberry',
    'grapefruit', 'grape', 'guava', 'jackfruit', 'jambul', 'jostaberry', 'jujube',
    'kiwi', 'kumquat', 'lemon', 'lime', 'lychee', 'longan', 'mandarin', 'mango',
    'marula', 'melon', 'miracle fruit', 'monkey orange', 'nectarine', 'orange',
    'papaya', 'passionfruit', 'peach', 'pear', 'persimmon', 'pineapple', 'plum',
    'pomegranate', 'rambutan', 'raspberry', 'redcurrant', 'soursop', 'strawberry',
    'starfruit', 'tamarind', 'tangerine', 'tomato', 'ugli fruit', 'watermelon',
    'African pear', 'African bush pear', 'African star apple', 'bush mango', 'jackalberry',
    'kei apple', 'waterberry', 'aput', 'bilberry', 'cloudberry', 'damson', 'honeyberry',
    'huckleberry', 'lingonberry', 'mulberry', 'physalis', 'pitaya', 'pomelo', 'salak',
    'sapodilla', 'santol', 'serviceberry', 'sloe', 'white currant', 'yuzu', 'jabuticaba',
    'horned melon', 'cupuacu', 'elderberry', 'genip', 'guavaberry', 'imbe', 'langsat',
    'loquat', 'mangosteen', 'mammee apple', 'nance', 'palm fruit', 'pequi', 'pitomba',
    'pulasan', 'rose apple', 'safou', 'santol', 'sapote', 'sea buckthorn', 'tamarillo',
    'tangelo', 'ugni', 'voavanga', 'yangmei', 'yumberry', 'ziziphus fruit'
]


months = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

class DatabaseManager:
    def __init__(self, db_name="njangi_groups.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS njangi_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                size INTEGER NOT NULL,
                loan INTEGER NOT NULL,
                time INTEGER NOT NULL,
                base INTEGER,
                start_month INTEGER,
                start_year INTEGER,
                participants TEXT,
                fruits TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS njangi_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES njangi_groups (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_group(self, name, size, loan, time, base, start_month, start_year, participants, fruits):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO njangi_groups 
                (name, size, loan, time, base, start_month, start_year, participants, fruits, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, size, loan, time, base, start_month, start_year, 
                  json.dumps(participants), json.dumps(fruits), datetime.now()))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def load_group(self, name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM njangi_groups WHERE name = ?', (name,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'size': result[2],
                'loan': result[3],
                'time': result[4],
                'base': result[5],
                'start_month': result[6],
                'start_year': result[7],
                'participants': json.loads(result[8]) if result[8] else [],
                'fruits': json.loads(result[9]) if result[9] else []
            }
        return None
    
    def get_all_groups(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, created_at, updated_at FROM njangi_groups ORDER BY updated_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def delete_group(self, name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM njangi_groups WHERE name = ?', (name,))
        conn.commit()
        conn.close()

class Njangi:
    def __init__(self, size, loan, time, base=None, participants=None, fruits=None, name=None):
        self.name = name
        self.size, self.loan, self.time = size, loan, time
        self.base = loan * time if base is None else base
        if size < time:
            sys.exit("Error: size >= time")
        
        self.fruits = fruits if fruits else random.sample(fruits_master, size)
        
        if participants:
            if len(participants) != size:
                sys.exit("Error: Number of participants provided must match size")
            
            # --- FIX 1: Internal Tracking for Participants ---
            # Create a list of tuples: (actual_name, unique_id)
            # The PDF will display actual_name, but the payout logic will use the unique list.
            # The structure for self.people is now a list of strings, where each string is the participant's name.
            # We must map fruits to this list.
            self.people = participants # This is the list of names from the UI
            
            # Create the internal mapping for payout logic and fruit assignment.
            # This is the list of *unique* identifiers used for random assignment.
            self.unique_participants = self._create_unique_participant_list(self.people)
            
        else:
            self.people = [f"Person {i}" for i in range(1, size + 1)]
            self.unique_participants = [f"Person {i}" for i in range(1, size + 1)]

        # Map the unique participants to their assigned fruit for quick lookup
        self.fruit_to_participant_map = dict(zip(self.fruits, self.people))
        # Map the actual participant names to their fruit for table 2
        self.participant_to_fruit_map = dict(zip(self.people, self.fruits))


    def _create_unique_participant_list(self, participants):
        """Creates an internally unique list of participant names to handle duplicates."""
        unique_participants = []
        name_counts = {}
        for name in participants:
            if name not in name_counts:
                name_counts[name] = 1
                unique_participants.append(name)
            else:
                name_counts[name] += 1
                # Append the name with a suffix like (2) for internal tracking
                unique_participants.append(f"{name} ({name_counts[name]})")
        return unique_participants


    def monthly_collection(self):
        return self.size * self.loan

    def pool(self):
        return self.monthly_collection() * self.time

    def generate_pdf(self, filename='njangi_pro_report.pdf', start_month=1, start_year=2025):
        schedule, residue = [], 0
        
        # We use the internally unique list for the unpaid list to ensure everyone gets paid once.
        unpaid_unique = self.unique_participants.copy()
        
        # Randomize the unique participants list to assign fruits/payouts in a random order
        random.shuffle(unpaid_unique) 
        
        fruit_to_name_for_payout = {
            fruit: name for fruit, name in zip(self.fruits, self.people)
        }

        # The core payout logic: map a unique participant to their fruit and then use the fruit's assigned name for display
        
        for i in range(self.time):
            month_idx = (start_month + i - 1) % 12 + 1
            year = start_year + ((start_month + i - 1) // 12)
            month_str = f"{months[month_idx][:3]}-{year}"

            collected = self.monthly_collection()
            available = collected + residue

            if i == self.time - 1:
                cnt, residue = len(unpaid_unique), 0
            else:
                cnt = min(available // self.base, len(unpaid_unique))
                residue = available - cnt * self.base

            # Get the unique participants who are paid this month
            paid_unique_participants = unpaid_unique[:cnt]
            
            # --- FIX 1 implementation in PDF generation ---
            # Find the fruit associated with this unique participant, then find the actual name associated with that fruit
            # The participants in self.people (actual names) are in the same order as self.fruits.
            
            # 1. Create a map from unique_participant -> actual_name
            unique_to_actual_name = {}
            for index, unique_name in enumerate(self.unique_participants):
                unique_to_actual_name[unique_name] = self.people[index]

            # 2. Get the actual names for display in the PDF's payout schedule (Table 3)
            # Find the index of the unique participant in self.unique_participants
            # Use that index to get the actual name from self.people, and the fruit from self.fruits
            assigned_fruits_and_names = []
            for paid_unique_name in paid_unique_participants:
                try:
                    # Find the index of the paid_unique_name in the unique list
                    idx = self.unique_participants.index(paid_unique_name)
                    actual_name = self.people[idx]
                    assigned_fruit = self.fruits[idx]
                    assigned_fruits_and_names.append((actual_name, assigned_fruit))
                except ValueError:
                    # Fallback for unexpected case
                    assigned_fruits_and_names.append(("--Error--", "--Error--"))

            # Sort by fruit for consistent display in the month
            assigned_fruits_and_names.sort(key=lambda x: x[1])

            # Prepare name display for Table 3
            # List all actual names and their fruits for the column
            # ----- FIXED: show only names (no fruits) in the Names (Fruit) column -----
            name_only_display = [f"{name}" for name, fruit in assigned_fruits_and_names]
            
            # Format display as requested: first 3, then "..."
            display_list = name_only_display[:3]
            name_display = ", ".join(display_list) + (", ..." if len(name_only_display) > 3 else "")
            
            schedule.append([
                str(i + 1), month_str,
                f"{collected:,}", f"{available:,}", f"{residue:,}",
                str(cnt), name_display
            ])
            unpaid_unique = unpaid_unique[cnt:] # Remove paid unique participants

        # --- PDF Generation (No changes to the template structure) ---
        doc = SimpleDocTemplate(
            filename, pagesize=letter,
            leftMargin=50, rightMargin=50, topMargin=130, bottomMargin=70
        )

        st_styles = getSampleStyleSheet()
        st_styles.add(ParagraphStyle('TitleBig', fontSize=22, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#2C3E50'), alignment=1, spaceAfter=12))
        st_styles.add(ParagraphStyle('Sub', fontSize=11, fontName='Helvetica',
                                     textColor=colors.HexColor('#7F8C8D'), alignment=1,
                                     spaceBefore=24, spaceAfter=24))
        st_styles.add(ParagraphStyle('SubSmall', fontSize=10, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#117A65'), alignment=1,
                                     spaceBefore=0, spaceAfter=18))
        st_styles.add(ParagraphStyle('SecTitle', fontSize=14, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#34495E'),
                                     spaceBefore=0, spaceAfter=12, leftIndent=-7, alignment=0))
        st_styles.add(ParagraphStyle('CellLeft', fontSize=9, fontName='Helvetica',
                                     textColor=colors.HexColor('#2C3E50'), alignment=0))

        elems = [
            Paragraph(self.name, st_styles['TitleBig']),
            Paragraph(
                f"Period: {months[start_month][:3]}-{start_year} to "
                f"{months[(start_month + self.time - 2) % 12 + 1][:3]}-"
                f"{start_year + ((start_month + self.time - 2) // 12)}",
                st_styles['Sub']
            ),
            Paragraph(f"Each member contributes: {self.loan:,} FCFA per month", st_styles['SubSmall']),
            Paragraph(f"Net payout per month per member: {self.base:,} FCFA", st_styles['SubSmall'])
        ]

        # Table 1: Assigned Fruits (Display is for fruits only, not names)
        # Note: This table is misleading now that names are assigned to fruits, 
        # but the template must be kept constant.
        elems.append(Paragraph("Assigned Fruits", st_styles['SecTitle']))
        # We display the fruits list as is, matching the old logic for template consistency.
        fruits_data = [["S/N", "Fruit"]] + [[str(i + 1), self.fruits[i]] for i in range(self.size)]
        t1 = Table(fruits_data, colWidths=[40, doc.width - 40])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#AED6F1')),
        ]))
        elems += [t1, PageBreak()]

        # Table 2: Participants & Fruits
        # The display names (self.people) and their assigned fruits (self.fruits) are 1:1.
        elems.append(Paragraph("Participants & Fruits", st_styles['SecTitle']))
        base_headers = ["S/N", "Name", "Fruit"]
        duration_headers = [
            f"{months[(start_month + i - 1) % 12 + 1][0]}{str(start_year + ((start_month + i - 1) // 12))[-2:]}"
            for i in range(self.time)
        ]
        headers = base_headers + duration_headers

        pf = [[str(i + 1), self.people[i], self.fruits[i]] + [" "]*self.time for i in range(self.size)]

        fixed_widths = [35, 120, 60]
        duration_width = max(15, (doc.width - sum(fixed_widths)) / self.time)
        col_widths = fixed_widths + [duration_width]*self.time

        t2 = Table([headers] + pf, colWidths=col_widths)
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('LEFTPADDING', (0, 1), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#ABEBC6')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        elems += [t2, PageBreak()]

        # Table 3: Payout Schedule (with names and fruits in the last column)
        elems.append(Paragraph("Payout Schedule", st_styles['SecTitle']))
        sched_headers = ["S/N", "Mon", "Col", "Avail", "Res", "Payouts", "Names (Fruit)"] # Updated header
        t3 = Table([sched_headers] + schedule,
                    colWidths=[35, 55, 60, 60, 60, 50, doc.width - 320],
                    repeatRows=1)
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),
            ('ALIGN', (6, 1), (6, -1), 'LEFT'),
            ('FONTNAME', (1, 1), (1, -1), 'Courier'),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#FAD7A0')),
            ('LEFTPADDING', (1, 1), (1, -1), 0),
            ('RIGHTPADDING', (1, 1), (1, -1), 0),
            ('LEFTPADDING', (0, 1), (-1, -1), 4),
        ]))
        elems += [t3, Spacer(1, 12)]

        # Summary Section
        elems.append(Paragraph("Summary", st_styles['SecTitle']))
        summary_lines = [
            f"Payout per person     : {self.base:,}",
            f"Loan per person/month : {self.loan:,}",
            f"Participants          : {self.size}",
            f"Months                : {self.time}",
            f"Total Pool Collected  : {self.pool():,}",
            f"Total Payout          : {(self.base * self.size):,}",
            f"Residue at End        : 0"
        ]
        sumt = Table([[Paragraph(line, st_styles['CellLeft'])] for line in summary_lines],
                      colWidths=[doc.width])
        sumt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#D6EAF8')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#5499C7')),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#AED6F1')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elems.append(sumt)

        def watermark(c, _doc):
            c.saveState()
            c.setFont("Helvetica-Bold", 70)
            c.setFillColor(colors.HexColor("#F7F9F9"))
            c.translate(letter[0] / 2, letter[1] / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, "auto-generated")
            c.restoreState()

        def header_footer(c, _doc):
            c.saveState()
            c.setStrokeColor(colors.HexColor('#3498DB'))
            c.setLineWidth(1.2)
            c.line(50, _doc.height + _doc.topMargin + 8,
                   letter[0] - 50, _doc.height + _doc.topMargin + 8)
            c.setFillColor(colors.HexColor('#FFFFFF'))
            c.circle(68, _doc.height + _doc.topMargin + 32, 18, fill=1, stroke=0)
            c.setFont("Helvetica-Bold", 16)
            c.setFillColor(colors.HexColor('#3498DB'))
            c.drawCentredString(68, _doc.height + _doc.topMargin + 29, "[ Tz ]")
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.HexColor('#2C3E50'))
            c.drawString(95, _doc.height + _doc.topMargin + 27, self.name)
            c.setStrokeColor(colors.HexColor('#B9770E'))
            c.line(50, 55, letter[0] - 50, 55)
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor('#ABB2B9'))
            c.drawCentredString(letter[0] / 2, 45, f"Page {c.getPageNumber()}")
            c.setFont("Helvetica", 8)
            c.drawString(50, 45, "Team [ zeru ]")
            sig = "steady - calm - driven"
            c.drawString(letter[0] - 50 - c.stringWidth(sig, "Helvetica", 8), 45, sig)
            c.restoreState()
            watermark(c, _doc)

        doc.build(elems, onFirstPage=header_footer, onLaterPages=header_footer)
        return filename

def initialize_session_state():
    """Initialize session state variables"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'current_group_data' not in st.session_state:
        st.session_state.current_group_data = None
    if 'participants' not in st.session_state:
        st.session_state.participants = []
    if 'fruits' not in st.session_state:
        st.session_state.fruits = []
    if 'fruit_keys' not in st.session_state: # New: To track which fruit belongs to which key
        st.session_state.fruit_keys = {}

def reset_form():
    """Reset form to default values"""
    st.session_state.current_group_data = None
    st.session_state.participants = []
    st.session_state.fruits = []
    st.session_state.fruit_keys = {}
    st.rerun()

def load_group_data(group_data):
    """Load group data into session state"""
    st.session_state.current_group_data = group_data
    st.session_state.participants = group_data['participants']
    st.session_state.fruits = group_data['fruits']
    st.session_state.fruit_keys = {f"fruit_{i}": fruit for i, fruit in enumerate(group_data['fruits'])}

# --- New helper function for auto-reassignment ---
def reassign_remaining_fruits(size, current_fruits_list, trigger_key):
    """
    Reassigns fruits based on the unique selection constraint.
    This function is called when a fruit is selected via a Streamlit widget.
    It updates the session state to reflect the unique assignment logic.
    """
    
    # 1. Get the fruit just selected for the triggering key
    selected_fruit = st.session_state.get(trigger_key)
    if not selected_fruit:
        return # Should not happen if a fruit was selected

    # 2. Get the index of the triggering selectbox
    try:
        trigger_index = int(trigger_key.split('_')[1])
    except:
        return # Not a fruit selectbox key

    # 3. Update the fruit at the trigger index
    current_fruits_list[trigger_index] = selected_fruit
    st.session_state.fruits = current_fruits_list
    
    # 4. Identify the remaining unassigned fruits from the master list
    used_fruits = set(current_fruits_list[:trigger_index + 1])
    remaining_fruits_master = [fruit for fruit in fruits_master if fruit not in used_fruits]
    
    # 5. Automatically reassign the remaining slots
    for i in range(trigger_index + 1, size):
        # The fruit at index i is now constrained to be one of the remaining
        # Try to keep the current fruit if it's still available in the remaining list
        current_fruit_at_i = current_fruits_list[i]
        
        if current_fruit_at_i in remaining_fruits_master:
            # Keep the current fruit for this slot, remove it from the remaining pool
            remaining_fruits_master.remove(current_fruit_at_i)
        elif remaining_fruits_master:
            # Reassign from the remaining pool (take the first available)
            new_fruit = remaining_fruits_master.pop(0)
            current_fruits_list[i] = new_fruit
        else:
            # This should not happen if size <= len(fruits_master), but as a safe fall-back
            current_fruits_list[i] = None 
            
    st.session_state.fruits = current_fruits_list


def main():
    st.set_page_config(
        page_title="Njangi Group Manager",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    
    st.title("💰 Njangi Group Report Generator")
    st.markdown("---")
    
    # Sidebar for saved groups management
    with st.sidebar:
        st.header("📁 Saved Groups")
        
        # Load existing groups
        saved_groups = st.session_state.db_manager.get_all_groups()
        
        if saved_groups:
            group_names = [group[0] for group in saved_groups]
            selected_group = st.selectbox("Load Existing Group:", [""] + group_names)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📂 Load", disabled=not selected_group, use_container_width=True):
                    group_data = st.session_state.db_manager.load_group(selected_group)
                    if group_data:
                        load_group_data(group_data)
                        st.success(f"Loaded: {selected_group}")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", disabled=not selected_group, use_container_width=True):
                    st.session_state.db_manager.delete_group(selected_group)
                    st.success(f"Deleted: {selected_group}")
                    st.rerun()
        else:
            st.info("No saved groups found.")
        
        st.divider()
        
        if st.button("🆕 New Group",use_container_width=True):
            reset_form()
    
    # Main form
    tab1, tab2, tab3 = st.tabs(["📋 Group Setup", "👥 Participants", "🎯 Generate"])
    
    with tab1:
        st.subheader("Basic Group Information")
        
        col1, col2 = st.columns(2)
        with col1:
            current_name = st.session_state.current_group_data['name'] if st.session_state.current_group_data else ""
            nname = st.text_input("Njangi Group Name", value=current_name, help="Enter a unique name for your Njangi group")
            
            current_size = st.session_state.current_group_data['size'] if st.session_state.current_group_data else 13
            size = st.number_input("Number of Participants", min_value=1, max_value=len(fruits_master), value=current_size, step=1)
            
            current_loan = st.session_state.current_group_data['loan'] if st.session_state.current_group_data else 5000
            loan = st.number_input("Monthly Contribution (FCFA)", min_value=1000, value=current_loan, step=1000)
        
        with col2:
            current_time = st.session_state.current_group_data['time'] if st.session_state.current_group_data else 12
            time = st.number_input("Duration (Months)", min_value=1, max_value=60, value=current_time, step=1)
            
            current_start_month = st.session_state.current_group_data['start_month'] if st.session_state.current_group_data else 7
            start_month = st.selectbox("Start Month", options=list(months.keys()), 
                                       format_func=lambda x: months[x], index=current_start_month-1)
            
            current_start_year = st.session_state.current_group_data['start_year'] if st.session_state.current_group_data else 2025
            start_year = st.number_input("Start Year", min_value=2025, max_value=2030, value=current_start_year, step=1)
        
        # Validation
        if size < time:
            st.error("⚠️ Number of participants must be greater than or equal to duration in months!")
        
        # Calculate base payout
        base = loan * time
        total_pool = size * loan * time
        
        st.info(f"💡 **Calculated Values:**\n"
               f"- Monthly Collection: {size * loan:,} FCFA\n"
               f"- Payout per Person: {base:,} FCFA\n"
               f"- Total Pool: {total_pool:,} FCFA")
    
    with tab2:
        st.subheader("Participants and Fruit Assignment")
        
        if size > 0:
            if size > len(fruits_master):
                st.error(f"❌ Cannot have more than {len(fruits_master)} participants as fruits must be unique.")
                return

            col1, col2 = st.columns(2)
            
            # --- Participant List Management (No major changes needed here based on request) ---
            with col1:
                st.markdown("**👥 Participants**")
                # Ensure participants list matches current size
                if len(st.session_state.participants) != size:
                    current_participants = st.session_state.participants[:size]
                    while len(current_participants) < size:
                        current_participants.append(f"Person {len(current_participants) + 1}")
                    st.session_state.participants = current_participants
                
                for i in range(size):
                    st.session_state.participants[i] = st.text_input(
                        f"Participant {i+1}", 
                        value=st.session_state.participants[i],
                        key=f"participant_{i}"
                    )
            
            # --- FIX 2 & 3: Interactive Unique Fruit Assignment Logic ---
            with col2:
                st.markdown("**🍎 Fruit Assignment**")
                
                # Ensure fruits list matches current size, re-initializing if size changes
                if len(st.session_state.fruits) != size or not st.session_state.fruits:
                    available_fruits = fruits_master.copy()
                    random.shuffle(available_fruits)
                    st.session_state.fruits = available_fruits[:size]
                
                # The core logic for unique, dependent fruit assignment
                current_used_fruits = set()
                
                for i in range(size):
                    # For the current participant, their assigned fruit is removed from the list of fruits
                    # available to all *subsequent* participants.
                    
                    # 1. Identify fruits already assigned to participants with a lower index
                    fruits_assigned_before = st.session_state.fruits[:i]
                    
                    # 2. Get the full list of options available for the current selectbox
                    # These are all fruits not used by participants 0 to i-1
                    available_options = [fruit for fruit in fruits_master if fruit not in fruits_assigned_before]
                    
                    # 3. Get the current fruit assigned to this participant
                    current_fruit = st.session_state.fruits[i]
                    
                    # 4. Determine the index of the current fruit in the available options list
                    try:
                        current_index = available_options.index(current_fruit)
                    except ValueError:
                        # This happens if the current fruit is an invalid option (e.g., if it was 
                        # an old selection now used by someone else after a change).
                        # We must auto-reassign to a valid fruit.
                        current_index = 0
                        st.session_state.fruits[i] = available_options[0] if available_options else None
                        current_fruit = st.session_state.fruits[i]
                        # Re-run after force-reassigning to update dependencies correctly
                        # st.rerun() 
                    
                    # 5. Display the selectbox
                    select_key = f"fruit_{i}"
                    
                    # Use on_change and args to pass context to the reassign function
                    st.session_state.fruits[i] = st.selectbox(
                        f"🍎 for {st.session_state.participants[i][:15]}...",
                        options=available_options,
                        index=current_index,
                        key=select_key,
                        on_change=reassign_remaining_fruits,
                        args=(size, st.session_state.fruits, select_key)
                    )
            
            # Quick actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎲 Random Fruits", use_container_width=True):
                    available_fruits = fruits_master.copy()
                    random.shuffle(available_fruits)
                    st.session_state.fruits = available_fruits[:size]
                    st.rerun()
            
            with col2:
                if st.button("📝 Auto-name Participants",use_container_width=True):
                    st.session_state.participants = [f"Member {i+1}" for i in range(size)]
                    st.rerun()
            
            with col3:
                if st.button("💾 Save Progress",use_container_width=True):
                    if nname and len(nname.strip()) > 0:
                        success = st.session_state.db_manager.save_group(
                            nname, size, loan, time, base, start_month, start_year,
                            st.session_state.participants, st.session_state.fruits
                        )
                        if success:
                            st.success("✅ Progress saved!")
                        else:
                            st.warning("⚠️ Group name already exists (updated progress)!")
                    else:
                        st.error("❌ Please enter a group name first!")
    
    with tab3:
        st.subheader("Generate Njangi Report")
        
        # Final validation and preview
        if nname and size > 0 and time > 0 and len(st.session_state.participants) == size:
            # Check for unique fruits (should be guaranteed by UI logic, but check for safety)
            unique_fruit_set = set(st.session_state.fruits)
            duplicate_fruits = len(st.session_state.fruits) != len(unique_fruit_set)
            
            # The check for duplicate *names* is no longer a blocking error, as requested.
            
            if duplicate_fruits:
                st.error("❌ Duplicate fruits found! Please ensure all fruits are unique.")
            else:
                # Display summary
                st.success("✅ All validations passed!")
                
                with st.expander("📊 Group Summary", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("👥 Participants", size)
                        st.metric("💰 Monthly Contribution", f"{loan:,} FCFA")
                    
                    with col2:
                        st.metric("📅 Duration", f"{time} months")
                        st.metric("🎯 Payout per Person", f"{base:,} FCFA")
                    
                    with col3:
                        st.metric("🏦 Total Pool", f"{size * loan * time:,} FCFA")
                        st.metric("📈 Monthly Collection", f"{size * loan:,} FCFA")
                    
                    # Generate PDF
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
                            with st.spinner("Generating PDF..."):
                                try:
                                    # Save before generating
                                    st.session_state.db_manager.save_group(
                                        nname, size, loan, time, base, start_month, start_year,
                                        st.session_state.participants, st.session_state.fruits
                                    )
                                    
                                    # Generate PDF
                                    njangi = Njangi(
                                        size=size, loan=loan, time=time, base=base,
                                        participants=st.session_state.participants,
                                        fruits=st.session_state.fruits,
                                        name=nname
                                    )
                                    
                                    filename = f"{nname.replace(' ', '_')}_report.pdf"
                                    njangi.generate_pdf(filename=filename, start_month=start_month, start_year=start_year)
                                    
                                    st.success(f"✅ PDF generated successfully: {filename}")
                                    
                                    # Download button
                                    with open(filename, "rb") as f:
                                        st.download_button(
                                            label="📥 Download PDF",
                                            data=f,
                                            file_name=filename,
                                            mime="application/pdf",
                                            use_container_width=True
                                        )
                                    
                                except Exception as e:
                                    st.error(f"❌ Error generating PDF: {str(e)}")
                    
                    with col2:
                        if st.button("💾 Save & Exit", use_container_width=True):
                            success = st.session_state.db_manager.save_group(
                                nname, size, loan, time, base, start_month, start_year,
                                st.session_state.participants, st.session_state.fruits
                            )
                            if success:
                                st.success("✅ Group saved successfully!")
                            else:
                                st.warning("⚠️ Group updated (name already exists)")
        else:
            st.warning("⚠️ Please complete all required fields in the previous tabs.")
            missing_items = []
            if not nname:
                missing_items.append("Group name")
            if size <= 0:
                missing_items.append("Valid number of participants")
            if time <= 0:
                missing_items.append("Valid duration")
            if len(st.session_state.participants) != size:
                missing_items.append("All participant names")
            
            st.info(f"Missing: {', '.join(missing_items)}")

if __name__ == "__main__":
    # Detect if running inside Streamlit server by checking env var
    if os.environ.get("STREAMLIT_RUN") == "true":
        # Running inside Streamlit — just run main app
        main()
    else:
        # Avoid infinite relaunch by checking a second env var
        if os.environ.get("STREAMLIT_LAUNCHED") == "true":
            # Already launched Streamlit once — exit to avoid recursion
            sys.exit()

        # Set env vars for subprocess
        env = os.environ.copy()
        env["STREAMLIT_RUN"] = "true"
        env["STREAMLIT_LAUNCHED"] = "true"

        # Launch Streamlit app in a separate process, non-blocking
        subprocess.Popen([sys.executable, "-m", "streamlit", "run", __file__], env=env)

        # Exit the parent script immediately after launching
        sys.exit()
