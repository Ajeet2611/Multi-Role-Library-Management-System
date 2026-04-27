"""
Chapters 6-9: Architecture, Tech Stack, Database, Module Implementation
"""

from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from doc_helpers import *


def chapter_6_architecture(doc):
    add_chapter_heading(doc, 6, "System Architecture", "System Architecture")

    add_section_heading(doc, "6.1", "Architectural Overview")
    add_hindi_para(doc,
        "Software architecture किसी भी system की foundation होती है। यह decide करती है "
        "कि code कितना maintainable, scalable और testable होगा। हमारे project में हमने "
        "एक classic 3-Layer Architecture (also known as Three-Tier Architecture) "
        "implement की है, जो industry में सबसे widely-adopted patterns में से एक है।",
        first_line_indent=Inches(0.3))

    add_hindi_para(doc,
        "इस architecture का मुख्य principle है — Separation of Concerns। यानि हर layer "
        "की एक specific responsibility है, और एक layer का change दूसरी layers को "
        "affect नहीं करता। यह design future modifications, testing और team-based "
        "development के लिए ideal है।",
        first_line_indent=Inches(0.3))

    arch_diagram = """
    ┌─────────────────────────────────────────────────────────────────┐
    │                    PRESENTATION LAYER (GUI)                     │
    │                                                                 │
    │   gui_login.py    gui_admin.py    gui_super_admin.py            │
    │   gui_user.py     gui_permission_manager.py                     │
    │                                                                 │
    │   Tech: Tkinter Widgets + Matplotlib (FigureCanvasTkAgg)        │
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ User Actions / Events
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                  BUSINESS LOGIC LAYER                           │
    │                                                                 │
    │   auth.py           — Login validation                          │
    │   security.py       — bcrypt hashing/verification               │
    │   permissions.py    — RBAC checks                               │
    │   messaging.py      — Message handling                          │
    │   admin_*.py        — Admin operations (8 modules)              │
    │   dashboard_charts  — Analytics                                 │
    │                                                                 │
    │   Tech: Pure Python (no framework dependency)                   │
    └────────────────────────────┬────────────────────────────────────┘
                                 │
                                 │ Database Operations (CRUD)
                                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    DATA ACCESS LAYER                            │
    │                                                                 │
    │   db.py             — Connection factory (Singleton-like)       │
    │                                                                 │
    │   Tables:                                                       │
    │     • Institutions       • Users         • Members              │
    │     • Books              • Transactions  • UserMessages         │
    │     • RolePermissions    • InstitutionRolePermissions           │
    │                                                                 │
    │   Tech: MySQL Connector/Python + Parameterized Queries          │
    └─────────────────────────────────────────────────────────────────┘
    """
    add_diagram_placeholder(doc, "6.1", "3-Layer Architecture Diagram",
                            arch_diagram, height_inches=5.5)

    add_section_heading(doc, "6.2", "Layer 1: Presentation Layer (GUI)")
    add_hindi_para(doc,
        "Presentation layer वो है जिसके through user system के साथ interact करता है। "
        "हमारे case में यह Tkinter widgets से बनी desktop GUI है। इस layer का सिर्फ "
        "एक responsibility है — user input capture करना और results display करना। "
        "इसमें कोई business logic नहीं रखी गई।")

    add_hindi_para(doc, "Files in this Layer:", bold=True)
    add_data_table(doc,
        headers=["File", "Responsibility"],
        rows=[
            ["gui_login.py", "Initial login screen — username/password input"],
            ["gui_super_admin.py", "Super admin's complete dashboard"],
            ["gui_admin.py", "Regular admin dashboard with all admin operations"],
            ["gui_user.py", "End-user (student/teacher) dashboard"],
            ["gui_permission_manager.py", "Permission configuration UI"],
            ["dashboard_charts.py", "Embedded matplotlib chart widgets"],
        ],
        table_num=12,
        caption="Presentation Layer Files",
        col_widths=[Inches(2.5), Inches(4.0)])

    add_section_heading(doc, "6.3", "Layer 2: Business Logic Layer")
    add_hindi_para(doc,
        "Business logic layer वो जगह है जहाँ system की 'intelligence' रहती है। यहाँ "
        "rules implemented हैं — कैसे fine calculate करना है, कौन से user को क्या permission "
        "है, password कैसे verify करना है, इत्यादि। यह layer GUI और Database के बीच "
        "की bridge है।")

    add_hindi_para(doc, "Key Modules:", bold=True)
    add_bullet(doc, "auth.py: Login flow को orchestrate करता है — Users और Members tables में search, password verify, role-based dict return")
    add_bullet(doc, "security.py: bcrypt-based password hashing और checking — सिर्फ 2 functions")
    add_bullet(doc, "permissions.py: RBAC enforcement — has_permission(user, code) check")
    add_bullet(doc, "messaging.py: User-to-Admin messages, schema bootstrapping")
    add_bullet(doc, "admin_add_book.py, admin_issue_book.py, etc: Each admin operation का दे dedicated module")

    add_section_heading(doc, "6.4", "Layer 3: Data Access Layer")
    add_hindi_para(doc,
        "Data access layer का सिर्फ एक काम है — database connection provide करना और "
        "raw queries execute करना। हमारे project में यह सिर्फ db.py एक file में encapsulated है, "
        "जो factory pattern follow करती है।")

    add_code_block(doc, """import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="<your_mysql_password>",
            database="library_db"
        )
        print("Database Connected Successfully")
        return conn
    except:
        print("Database Connection Failed")
        return None""", language="python")

    add_callout_box(doc, "Design Pattern Note",
        "यह Factory Pattern का एक simple implementation है। हर module जब connection "
        "चाहिए होती है तो get_connection() call करता है — connection creation logic एक "
        "ही जगह centralized है। Future में अगर PostgreSQL पे migrate करना हो तो "
        "सिर्फ इस file को change करना है, बाकी 15 modules untouched रहेंगे।")

    add_section_heading(doc, "6.5", "Data Flow Example: Login Process")
    add_hindi_para(doc,
        "एक concrete example से समझते हैं कि तीनों layers कैसे interact करती हैं — "
        "जब कोई user login करता है तब क्या होता है:")

    flow = """
    Step 1: User opens application
            └─> gui_login.py executes
                └─> Tkinter window पर username + password fields render होती हैं

    Step 2: User credentials enter करके "Login" button click करता है
            └─> do_login() function trigger होता है (Presentation Layer)
                └─> auth.login(username, password) call होता है (Business Layer)

    Step 3: auth.login() inside what happens:
            ├─> db.get_connection() called (Data Layer)
            ├─> SELECT query on Users table (Data Layer)
            │   └─> If found: bcrypt verify password
            │   └─> If not: SELECT query on Members table
            └─> Returns user dict {UserID, Username, Role, InstitutionID}

    Step 4: Login result handling (Presentation Layer)
            ├─> If None: Show error messagebox
            └─> If valid dict: Open appropriate dashboard
                ├─> Role == "SUPER_ADMIN" → gui_super_admin
                ├─> Role == "ADMIN" → gui_admin
                └─> Role == "USER/STUDENT/TEACHER" → gui_user
    """
    add_diagram_placeholder(doc, "6.2", "Login Process Data Flow",
                            flow, height_inches=4.5)

    add_section_heading(doc, "6.6", "Design Patterns Used")
    add_data_table(doc,
        headers=["Pattern", "Where Used", "Benefit"],
        rows=[
            ["Factory Method", "db.get_connection()", "Centralized DB instantiation"],
            ["MVC (Loose)", "GUI / Logic / Data layers", "Separation of concerns"],
            ["Repository Pattern", "Per-module DB queries", "Encapsulated data access"],
            ["Strategy Pattern", "Role-based routing in login", "Different behavior per role"],
            ["Singleton (Implicit)", "Single MySQL connection per op", "Resource management"],
        ],
        table_num=13,
        caption="Design Patterns Implemented",
        col_widths=[Inches(1.7), Inches(2.3), Inches(2.5)])

    add_section_heading(doc, "6.7", "Architecture Benefits")
    add_numbered(doc, "Maintainability: एक layer का bug दूसरी layers को affect नहीं करता")
    add_numbered(doc, "Testability: हर layer independently test की जा सकती है")
    add_numbered(doc, "Scalability: GUI layer को web में convert करना easy — सिर्फ Layer 1 बदलना है")
    add_numbered(doc, "Team Development: 3 अलग developers एक-एक layer पर parallel काम कर सकते हैं")
    add_numbered(doc, "Technology Migration: MySQL से PostgreSQL — सिर्फ db.py बदलना है")

    add_screenshot_placeholder(doc, "6.3",
        "Application Architecture Visualization (3-Tier Layered Diagram)",
        height_inches=3.5)

    add_page_break(doc)


def chapter_7_tech_stack(doc):
    add_chapter_heading(doc, 7, "Tech Stack विस्तार से", "Tech Stack Deep Dive")

    add_section_heading(doc, "7.1", "Technology Selection Philosophy")
    add_hindi_para(doc,
        "हर technology choice के पीछे एक specific reasoning है। हमने random तरीके से "
        "कोई भी tool नहीं उठाया — हर decision evaluation के बाद लिया गया। इस chapter में "
        "हर technology का detailed justification देखेंगे।",
        first_line_indent=Inches(0.3))

    add_section_heading(doc, "7.2", "Python 3.10+ — Programming Language")
    add_hindi_para(doc, "क्यों Python?", bold=True, color=NAVY, size=12)
    add_bullet(doc, "Readability: Python की syntax English-like है, beginners भी समझ सकते हैं")
    add_bullet(doc, "Massive Ecosystem: PyPI पर 4 lakh+ packages available — किसी भी need के लिए library मिल जाती है")
    add_bullet(doc, "Cross-Platform: एक ही code Windows, macOS, Linux पर run करता है")
    add_bullet(doc, "Built-in Tkinter: GUI के लिए कोई extra dependency नहीं")
    add_bullet(doc, "Modern Features: f-strings, type hints, walrus operator (3.10+)")
    add_bullet(doc, "Industry Adoption: Google, Netflix, Instagram — सब Python use करती हैं")

    add_hindi_para(doc, "क्यों Python 3.10+ (और 3.6 या 3.8 नहीं)?", bold=True, color=NAVY, size=12)
    add_bullet(doc, "Pattern matching (match-case statement) — cleaner role routing")
    add_bullet(doc, "Better error messages — debugging easier")
    add_bullet(doc, "Performance improvements — 3.11 में ~25% faster")
    add_bullet(doc, "Long-term support — 2026 तक official support")

    add_section_heading(doc, "7.3", "Tkinter — GUI Framework")
    add_hindi_para(doc, "क्यों Tkinter?", bold=True, color=NAVY, size=12)
    add_bullet(doc, "Built-in: Python के साथ default install — कोई extra package नहीं")
    add_bullet(doc, "Lightweight: Memory footprint कम — < 50MB total")
    add_bullet(doc, "Platform Native: हर OS पर native widgets render करता है")
    add_bullet(doc, "Mature: 30+ years पुराना — battle-tested")
    add_bullet(doc, "Documentation Rich: हजारों tutorials available")

    add_hindi_para(doc, "Alternatives जो हमने consider किए:", bold=True, color=NAVY, size=12)
    add_data_table(doc,
        headers=["Framework", "Pros", "Cons", "Decision"],
        rows=[
            ["Tkinter", "Built-in, lightweight, easy", "UI dated looks", "✓ SELECTED"],
            ["PyQt5/6", "Modern UI, professional", "Licensing complexity, heavy", "❌ Rejected"],
            ["Kivy", "Mobile + desktop", "Steep learning curve", "❌ Rejected"],
            ["wxPython", "Native look", "Less popular, fewer tutorials", "❌ Rejected"],
            ["Web (Flask)", "Modern", "Loses 'desktop' feel", "❌ Rejected"],
        ],
        table_num=14,
        caption="GUI Framework Comparison",
        col_widths=[Inches(1.0), Inches(1.8), Inches(1.8), Inches(1.5)])

    add_section_heading(doc, "7.4", "MySQL — Relational Database")
    add_hindi_para(doc, "क्यों MySQL?", bold=True, color=NAVY, size=12)
    add_bullet(doc, "ACID Compliance: Transactions safe — book issue/return atomic operations")
    add_bullet(doc, "Free & Open Source: Community Edition पूरी तरह free")
    add_bullet(doc, "Performance: Indexed queries millions of rows handle कर सकती हैं")
    add_bullet(doc, "Mature Ecosystem: GUI tools (MySQL Workbench), backup utilities")
    add_bullet(doc, "Cross-Platform: हर OS support करती है")
    add_bullet(doc, "Strong Community: 30M+ deployments worldwide")

    add_hindi_para(doc, "MySQL vs Alternatives:", bold=True, color=NAVY, size=12)
    add_data_table(doc,
        headers=["Database", "Type", "Pros", "Cons"],
        rows=[
            ["MySQL", "RDBMS", "Mature, free, fast", "Limited NoSQL features"],
            ["PostgreSQL", "RDBMS", "Most advanced features", "Slightly slower for simple queries"],
            ["SQLite", "Embedded RDBMS", "Zero setup", "Single-user, no concurrency"],
            ["MongoDB", "NoSQL", "Flexible schema", "No JOINs, ACID weak"],
            ["Oracle", "RDBMS", "Enterprise-grade", "Expensive licensing"],
        ],
        table_num=15,
        caption="Database Comparison",
        col_widths=[Inches(1.2), Inches(1.3), Inches(2.0), Inches(2.0)])

    add_section_heading(doc, "7.5", "bcrypt — Password Hashing Library")
    add_hindi_para(doc,
        "bcrypt एक purpose-built password hashing function है। यह deliberately slow "
        "है — एक hash operation में ~100ms लगते हैं। यह 'feature' है, 'bug' नहीं — slow "
        "होने की वजह से brute-force attacks practically impossible हो जाते हैं।")

    add_hindi_para(doc, "bcrypt vs Other Hashing Methods:", bold=True)
    add_data_table(doc,
        headers=["Method", "Speed (hashes/sec)", "Brute-Force Time", "Recommended?"],
        rows=[
            ["MD5", "~10 billion", "Seconds", "❌ Broken"],
            ["SHA-1", "~7 billion", "Seconds", "❌ Broken"],
            ["SHA-256", "~3 billion", "Minutes", "❌ Too fast for passwords"],
            ["bcrypt (cost 12)", "~10", "Years", "✓ STANDARD"],
            ["Argon2", "Configurable", "Years", "✓ Modern alternative"],
        ],
        table_num=16,
        caption="Password Hashing Methods Comparison",
        col_widths=[Inches(1.5), Inches(1.5), Inches(1.5), Inches(2.0)])

    add_callout_box(doc, "Critical Insight",
        "bcrypt की 'slowness' हमारी सबसे बड़ी security advantage है। MD5 जैसे fast "
        "algorithms में attacker GPU से 10 billion hashes/second try कर सकता है। bcrypt "
        "पर वही attack hundreds of years लगाएगा।")

    add_section_heading(doc, "7.6", "Matplotlib — Analytics & Visualization")
    add_hindi_para(doc, "Matplotlib हमारे dashboard में charts बनाने के लिए use हुआ है:")
    add_bullet(doc, "Pie chart: Active vs Inactive users")
    add_bullet(doc, "Bar chart: Role distribution")
    add_bullet(doc, "FigureCanvasTkAgg backend से Tkinter में embed किया")
    add_bullet(doc, "Real-time data — हर dashboard refresh पर fresh charts")

    add_section_heading(doc, "7.7", "Supporting Libraries")
    add_data_table(doc,
        headers=["Library", "Version", "Purpose"],
        rows=[
            ["mysql-connector-python", "8.0+", "Python ↔ MySQL communication"],
            ["bcrypt", "4.0+", "Password hashing"],
            ["Pillow (PIL)", "9.0+", "Image processing for icons"],
            ["openpyxl", "3.0+", "Excel file generation"],
            ["matplotlib", "3.5+", "Charts and plots"],
            ["datetime (built-in)", "—", "Date/time arithmetic for fines"],
        ],
        table_num=17,
        caption="Supporting Python Libraries",
        col_widths=[Inches(2.0), Inches(1.0), Inches(3.5)])

    add_screenshot_placeholder(doc, "7.1",
        "Tech Stack Visualization — हर technology का logo और role",
        height_inches=3.5)

    add_page_break(doc)


def chapter_8_database(doc):
    add_chapter_heading(doc, 8, "Database Design", "Database Design")

    add_section_heading(doc, "8.1", "Database Design Philosophy")
    add_hindi_para(doc,
        "एक well-designed database किसी भी application की backbone होती है। हमारा "
        "schema 3rd Normal Form (3NF) में normalized है — कोई redundant data नहीं, "
        "कोई transitive dependencies नहीं। साथ ही हमने multi-tenancy को ground-up "
        "design किया है — हर business table में InstitutionID column है जो data "
        "isolation guarantee करता है।",
        first_line_indent=Inches(0.3))

    add_section_heading(doc, "8.2", "Entity-Relationship (ER) Diagram")

    er_diagram = """
    ┌──────────────────┐
    │   Institutions   │
    │ ──────────────── │
    │ InstitutionID PK │◄────────┐
    │ Name             │         │
    │ Address          │         │
    │ Contact          │         │
    └──────────────────┘         │
                                 │ (1:N)
              ┌──────────────────┼─────────────────────┐
              │                  │                     │
              ▼                  ▼                     ▼
      ┌──────────────┐    ┌──────────────┐     ┌──────────────┐
      │    Users     │    │   Members    │     │    Books     │
      │ ──────────── │    │ ──────────── │     │ ──────────── │
      │ UserID    PK │    │ MemberID  PK │     │ BookID    PK │
      │ Username     │    │ UserID UNIQ  │     │ Title        │
      │ Password     │    │ Name         │     │ Author       │
      │ Role         │    │ Password     │     │ ISBN         │
      │ InstitutionID│    │ Role         │     │ Status       │
      └──────┬───────┘    │ Status       │     │ TotalCopies  │
             │            │ InstitutionID│     │ AvailCopies  │
             │            └──────┬───────┘     │ InstitutionID│
             │                   │             └──────┬───────┘
             │                   │                    │
             │                   │ (1:N)              │ (1:N)
             │                   │                    │
             │                   ▼                    │
             │           ┌────────────────┐           │
             │           │  Transactions  │           │
             │           │ ────────────── │           │
             │           │ IssueID    PK  │◄──────────┘
             │           │ BookID    FK   │
             │           │ MemberID  FK   │
             │           │ IssueDate      │
             │           │ DueDate        │
             │           │ ReturnStatus   │
             │           └────────────────┘
             │
             │           ┌────────────────────────────┐
             │           │  UserMessages              │
             │           │ ────────────────────────── │
             │           │ MessageID         PK       │
             │           │ UserID            FK       │
             │           │ Username                   │
             │           │ UserMessage                │
             │           │ AdminReply                 │
             │           │ Status (OPEN/CLOSED)       │
             │           │ SentAt, RepliedAt          │
             │           │ InstitutionID              │
             │           └────────────────────────────┘
             │
             │  ┌──────────────────────────────────┐
             │  │ InstitutionRolePermissions       │
             │  │ ──────────────────────────────── │
             │  │ ID                          PK   │
             │  │ InstitutionID                FK  │
             │  │ Role                             │
             │  │ PermissionCode                   │
             │  └──────────────────────────────────┘
    """
    add_diagram_placeholder(doc, "8.1", "Complete Entity-Relationship Diagram",
                            er_diagram, height_inches=7.0)

    add_section_heading(doc, "8.3", "Table Specifications")

    # Institutions
    add_section_heading(doc, "8.3.1", "Institutions Table", level=2)
    add_hindi_para(doc,
        "यह table multi-tenancy की foundation है। हर organization (school, college, "
        "library) का यहाँ एक row होता है, और बाकी सब tables इस InstitutionID को "
        "reference करते हैं।")
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["InstitutionID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique institution identifier"],
            ["Name", "VARCHAR(150)", "NOT NULL", "Organization का नाम"],
            ["Address", "TEXT", "NULL", "Physical address"],
            ["Contact", "VARCHAR(50)", "NULL", "Phone/Email"],
            ["CreatedAt", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Record creation time"],
        ],
        table_num=18,
        caption="Institutions Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    # Users
    add_section_heading(doc, "8.3.2", "Users Table", level=2)
    add_hindi_para(doc,
        "Users table में admin-level accounts रहते हैं — Super Admin और Admin roles। "
        "यह deliberately Members table से अलग रखा गया है क्योंकि admins की permissions "
        "और lifecycle अलग होती है।")
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["UserID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique user ID"],
            ["Username", "VARCHAR(100)", "UNIQUE, NOT NULL", "Login username"],
            ["Password", "VARCHAR(255)", "NOT NULL", "bcrypt hashed password"],
            ["Role", "VARCHAR(50)", "NOT NULL", "SUPER_ADMIN / ADMIN"],
            ["InstitutionID", "INT", "FK → Institutions", "Tenant reference"],
            ["CreatedAt", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Account creation"],
        ],
        table_num=19,
        caption="Users Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    # Members
    add_section_heading(doc, "8.3.3", "Members Table", level=2)
    add_hindi_para(doc,
        "Members table end-users (students, teachers, others) के लिए है। यह library "
        "service consume करते हैं — books issue/return, messages send.")
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["MemberID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Internal member ID"],
            ["UserID", "VARCHAR(100)", "UNIQUE, NOT NULL", "Login ID (reg number etc)"],
            ["Name", "VARCHAR(150)", "NOT NULL", "पूरा नाम"],
            ["Password", "VARCHAR(255)", "NOT NULL", "bcrypt hashed"],
            ["Role", "VARCHAR(50)", "NOT NULL", "STUDENT / TEACHER / OTHER"],
            ["Status", "VARCHAR(20)", "DEFAULT 'ACTIVE'", "ACTIVE / INACTIVE"],
            ["Email", "VARCHAR(150)", "NULL", "Contact email"],
            ["Phone", "VARCHAR(20)", "NULL", "Contact phone"],
            ["InstitutionID", "INT", "FK → Institutions", "Tenant reference"],
        ],
        table_num=20,
        caption="Members Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    # Books
    add_section_heading(doc, "8.3.4", "Books Table", level=2)
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["BookID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Unique book ID"],
            ["Title", "VARCHAR(255)", "NOT NULL", "Book title"],
            ["Author", "VARCHAR(150)", "NOT NULL", "Author name"],
            ["ISBN", "VARCHAR(20)", "UNIQUE", "ISBN code"],
            ["Status", "VARCHAR(20)", "DEFAULT 'AVAILABLE'", "Overall status"],
            ["TotalCopies", "INT", "NOT NULL, DEFAULT 1", "Total copies owned"],
            ["AvailableCopies", "INT", "NOT NULL", "Currently available"],
            ["InstitutionID", "INT", "FK → Institutions", "Tenant reference"],
        ],
        table_num=21,
        caption="Books Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    # Transactions
    add_section_heading(doc, "8.3.5", "Transactions Table", level=2)
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["IssueID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Transaction ID"],
            ["BookID", "INT", "FK → Books", "Issued book"],
            ["MemberID", "VARCHAR(100)", "FK → Members.UserID", "Issuing member"],
            ["IssueDate", "DATE", "NOT NULL", "Issue date"],
            ["DueDate", "DATE", "NOT NULL", "Return deadline (Issue + 7 days)"],
            ["ReturnDate", "DATE", "NULL", "Actual return date"],
            ["ReturnStatus", "VARCHAR(20)", "DEFAULT 'ISSUED'", "ISSUED / RETURNED"],
            ["Fine", "DECIMAL(8,2)", "DEFAULT 0", "Calculated fine"],
        ],
        table_num=22,
        caption="Transactions Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    # Messages
    add_section_heading(doc, "8.3.6", "UserMessages Table", level=2)
    add_hindi_para(doc,
        "यह table runtime पे `messaging.ensure_user_messages_table()` से self-create "
        "होती है। Bootstrapping problem को इस तरह elegant handle किया गया है।")
    add_data_table(doc,
        headers=["Column", "Type", "Constraints", "Description"],
        rows=[
            ["MessageID", "INT", "PRIMARY KEY, AUTO_INCREMENT", "Message ID"],
            ["UserID", "VARCHAR(100)", "NOT NULL", "Sender's UserID"],
            ["Username", "VARCHAR(150)", "NOT NULL", "Sender's name"],
            ["UserMessage", "TEXT", "NOT NULL", "Message content"],
            ["AdminReply", "TEXT", "NULL", "Admin's response"],
            ["Status", "VARCHAR(20)", "DEFAULT 'OPEN'", "OPEN / CLOSED"],
            ["SentAt", "DATETIME", "DEFAULT CURRENT_TIMESTAMP", "Sent timestamp"],
            ["RepliedAt", "DATETIME", "NULL", "Reply timestamp"],
            ["InstitutionID", "INT", "NOT NULL", "Tenant reference"],
        ],
        table_num=23,
        caption="UserMessages Table Schema",
        col_widths=[Inches(1.4), Inches(1.2), Inches(2.0), Inches(1.9)])

    add_section_heading(doc, "8.4", "Normalization (3NF)")
    add_hindi_para(doc,
        "हमारा schema 3rd Normal Form में normalized है। इसका मतलब क्या है?")
    add_numbered(doc, "1NF: हर column atomic है (कोई multi-value column नहीं) ✓")
    add_numbered(doc, "2NF: सभी non-key attributes पूरी primary key पर depend करती हैं ✓")
    add_numbered(doc, "3NF: कोई transitive dependencies नहीं — हर non-key attribute सीधे primary key पर depend करता है ✓")

    add_callout_box(doc, "Why 3NF?",
        "Higher normalization (4NF, 5NF, BCNF) over-engineering होती है small-to-medium "
        "systems के लिए। 3NF perfect balance है data integrity और query performance के बीच।")

    add_section_heading(doc, "8.5", "Indexes")
    add_hindi_para(doc, "Performance के लिए हमने strategic indexes लगाए हैं:")
    add_bullet(doc, "Users.Username (UNIQUE INDEX) — fast login lookup")
    add_bullet(doc, "Members.UserID (UNIQUE INDEX) — fast login fallback")
    add_bullet(doc, "Books.InstitutionID (INDEX) — fast tenant filtering")
    add_bullet(doc, "Books.ISBN (UNIQUE INDEX) — duplicate prevention")
    add_bullet(doc, "Transactions.MemberID (INDEX) — user history lookup")
    add_bullet(doc, "UserMessages.InstitutionID (INDEX) — fast admin inbox load")

    add_section_heading(doc, "8.6", "Multi-Tenancy Isolation")
    add_hindi_para(doc,
        "हर business query में WHERE InstitutionID = %s clause है। यह application "
        "layer पर enforce किया जाता है। Architecture-level guarantee है कि एक "
        "institution का user दूसरे institution का data कभी access नहीं कर सकता।")

    add_code_block(doc, """# Example: Books fetch — हमेशा InstitutionID filter
cur.execute(\"\"\"
    SELECT BookID, Title, Author, AvailableCopies
    FROM Books
    WHERE InstitutionID = %s
\"\"\", (institution_id,))""", language="python")

    add_screenshot_placeholder(doc, "8.2",
        "MySQL Workbench में Database Schema Visualization",
        height_inches=4.0)

    add_page_break(doc)


def chapter_9_modules(doc):
    add_chapter_heading(doc, 9, "Module-wise Implementation",
                        "Module-wise Design & Implementation")

    add_section_heading(doc, "9.1", "Project Structure Overview")
    add_hindi_para(doc,
        "यह project 20+ Python files में organized है, हर file का एक specific "
        "responsibility है। नीचे complete file structure दिया गया है:",
        first_line_indent=Inches(0.3))

    structure = """
    LibraryProject/
    │
    ├── main.py                       # CLI entry point
    │
    ├── 🔐 Core Modules (Foundation)
    │   ├── db.py                     # Database connection factory
    │   ├── auth.py                   # Login & authentication
    │   ├── security.py               # bcrypt hashing
    │   └── permissions.py            # RBAC checks
    │
    ├── 💬 Communication
    │   └── messaging.py              # User-Admin messages
    │
    ├── 📊 Analytics
    │   └── dashboard_charts.py       # Matplotlib charts
    │
    ├── 🖥️ GUI Modules (Tkinter)
    │   ├── gui_login.py              # Login window
    │   ├── gui_super_admin.py        # Super Admin dashboard
    │   ├── gui_admin.py              # Admin dashboard (~1500 lines)
    │   ├── gui_user.py               # End-user dashboard
    │   └── gui_permission_manager.py # Permission config UI
    │
    ├── 👨‍💼 Admin Operations
    │   ├── admin_add_book.py         # New book addition
    │   ├── admin_books_list.py       # Books inventory view
    │   ├── admin_add_user.py         # User registration
    │   ├── admin_users_view.py       # User listing
    │   ├── admin_issue_book.py       # Book issue logic
    │   ├── admin_return_book.py      # Book return + fine
    │   ├── admin_messages.py         # Message inbox
    │   └── admin_user_activity.py    # Activity logs
    │
    ├── 🛠️ Utilities
    │   └── fix_passwords.py          # Plain → bcrypt migration
    │
    ├── 📁 Assets
    │   └── assets/                   # Icons, images
    │
    └── 📄 Docs
        ├── README.md
        └── PROJECT_PROPOSAL_HINDI.md
    """
    add_diagram_placeholder(doc, "9.1", "Complete Project Structure",
                            structure, height_inches=6.5)

    add_section_heading(doc, "9.2", "db.py — Database Connection Factory")
    add_hindi_para(doc,
        "सिर्फ 15 lines का यह file पूरे project के foundation है। एक factory function "
        "जो MySQL connection return करती है।")
    add_code_block(doc, """import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="<your_password>",
            database="library_db"
        )
        print("Database Connected Successfully")
        return conn
    except:
        print("Database Connection Failed")
        return None""", language="python")

    add_hindi_para(doc, "Key Design Decisions:", bold=True)
    add_bullet(doc, "Try-except wrapper — connection failure पर graceful degradation")
    add_bullet(doc, "Returns None on failure — caller responsibility check करना")
    add_bullet(doc, "Centralized — कोई भी other module सीधे mysql.connector import नहीं करता")
    add_bullet(doc, "Future-friendly — connection pooling या ORM migration यहीं से possible")

    add_section_heading(doc, "9.3", "security.py — Password Hashing")
    add_code_block(doc, """import bcrypt

def hash_password(password: str) -> str:
    \"\"\"Plain password ko secure hash me convert karta hai\"\"\"
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def check_password(password: str, hashed_password: str) -> bool:
    \"\"\"Login ke time password verify karta hai\"\"\"
    return bcrypt.checkpw(password.encode(), hashed_password.encode())""",
                   language="python")

    add_hindi_para(doc, "Function Walkthrough:", bold=True)
    add_bullet(doc, "hash_password(): bcrypt.gensalt() हर बार unique salt generate करता है — same password का hash हर बार different होगा")
    add_bullet(doc, "check_password(): bcrypt.checkpw() automatically salt extract करता है और verify करता है")
    add_bullet(doc, "Encoding: bcrypt bytes में काम करता है, इसलिए .encode() और .decode() ज़रूरी हैं")

    add_section_heading(doc, "9.4", "auth.py — Authentication Logic")
    add_hindi_para(doc,
        "auth.py में login का complete flow है। Dual-table fallback (Users + Members) "
        "इसकी सबसे interesting feature है।")

    add_code_block(doc, """from db import get_connection
from security import check_password

def login(username=None, password=None):
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)

    # Step 1: Check Users table (Admins)
    cursor.execute(\"\"\"
        SELECT UserID, Username, Password, Role, InstitutionID
        FROM Users
        WHERE Username = %s
    \"\"\", (username,))
    user = cursor.fetchone()

    # Step 2: Fallback to Members (Students/Teachers)
    if not user:
        cursor.execute(\"\"\"
            SELECT MemberID, UserID, Name, Password, Role, InstitutionID
            FROM Members
            WHERE UserID = %s AND Status = 'ACTIVE'
        \"\"\", (username,))
        member = cursor.fetchone()
    else:
        member = None

    cursor.close()
    conn.close()

    # Verify password
    if user and check_password(password, user["Password"]):
        return {"UserID": user["UserID"], ...}
    if member and check_password(password, member["Password"]):
        return {"UserID": member["UserID"], ...}
    return None""", language="python")

    add_callout_box(doc, "Design Insight",
        "Dual-table fallback एक deliberate architectural decision है। Admins और end-users "
        "के lifecycle, permissions और attributes अलग हैं — उन्हें same table में रखने से "
        "schema bloated होता। पर login experience users के लिए unified रहना चाहिए, इसलिए "
        "यह fallback pattern।")

    add_section_heading(doc, "9.5", "permissions.py — Role-Based Access Control")
    add_code_block(doc, """from db import get_connection

def has_permission(user, permission_code):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(\"\"\"
        SELECT 1
        FROM InstitutionRolePermissions
        WHERE InstitutionID = %s
          AND Role = %s
          AND PermissionCode = %s
    \"\"\", (
        user["InstitutionID"],
        user["Role"],
        permission_code
    ))
    result = cur.fetchone()
    conn.close()
    return result is not None""", language="python")

    add_hindi_para(doc, "Why per-Institution Permissions?", bold=True)
    add_bullet(doc, "Different colleges के लिए different rules हो सकते हैं")
    add_bullet(doc, "Example: एक college में Admin user delete कर सकता है, दूसरे में नहीं")
    add_bullet(doc, "Granular control — flexibility बिना complexity के")

    add_section_heading(doc, "9.6", "messaging.py — Self-Healing Schema")
    add_code_block(doc, """from db import get_connection

def ensure_user_messages_table():
    conn = get_connection()
    if conn is None:
        return False

    cur = conn.cursor()
    cur.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS UserMessages (
            MessageID INT AUTO_INCREMENT PRIMARY KEY,
            UserID VARCHAR(100) NOT NULL,
            Username VARCHAR(150) NOT NULL,
            UserMessage TEXT NOT NULL,
            AdminReply TEXT NULL,
            Status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
            SentAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            RepliedAt DATETIME NULL,
            InstitutionID INT NOT NULL
        )
    \"\"\")
    conn.commit()
    cur.close()
    conn.close()
    return True""", language="python")

    add_callout_box(doc, "Self-Healing Schema Pattern",
        "यह pattern बहुत powerful है — जब भी messaging module use होता है, table "
        "automatically create होती है अगर already नहीं है। इसका मतलब new deployments "
        "के लिए कोई manual schema setup नहीं चाहिए। 'CREATE TABLE IF NOT EXISTS' "
        "एक idempotent operation है — कितनी भी बार run करो, side-effects नहीं।")

    add_section_heading(doc, "9.7", "dashboard_charts.py — Matplotlib Integration")
    add_code_block(doc, """from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from db import get_connection

def open_dashboard_charts(parent, user):
    frame = tk.Frame(parent, bg="#f2f4f7")
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Fetch data with InstitutionID filter
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(\"\"\"
        SELECT Status, COUNT(*) FROM Members
        WHERE InstitutionID = %s GROUP BY Status
    \"\"\", (user["InstitutionID"],))
    status_data = dict(cur.fetchall())

    # Create Pie chart
    fig1 = Figure(figsize=(4, 3), dpi=100)
    ax1 = fig1.add_subplot(111)
    ax1.pie(status_data.values(), labels=status_data.keys(), autopct="%1.1f%%")
    ax1.set_title("Active vs Inactive Users")

    # Embed in Tkinter
    canvas1 = FigureCanvasTkAgg(fig1, frame)
    canvas1.get_tk_widget().pack(side="left", padx=10, pady=10)""", language="python")

    add_section_heading(doc, "9.8", "admin_issue_book.py — Issue Logic")
    add_hindi_para(doc, "Book issue करने का complete logic:")
    add_bullet(doc, "Available copies check")
    add_bullet(doc, "Insert transaction record with default 7-day due date")
    add_bullet(doc, "Decrement AvailableCopies in Books table")
    add_bullet(doc, "Sub-transaction safety — single connection, atomic")

    add_section_heading(doc, "9.9", "admin_return_book.py — Auto Fine Calculation")
    add_code_block(doc, """from datetime import date

def return_book(book_id, institution_id):
    cur.execute(\"\"\"
        SELECT IssueID, DueDate FROM Transactions T
        JOIN Books B ON T.BookID = B.BookID
        WHERE T.BookID = %s AND T.ReturnStatus = 'ISSUED'
          AND B.InstitutionID = %s
        ORDER BY IssueID DESC LIMIT 1
    \"\"\", (book_id, institution_id))
    
    issue_id, due_date = cur.fetchone()
    late = (date.today() - due_date).days
    
    if late > 0:
        fine = late * 5  # ₹5 per day
        print(f"Late by {late} days | Fine ₹{fine}")
    else:
        print("Returned on time")
    
    cur.execute("UPDATE Transactions SET ReturnStatus='RETURNED' WHERE IssueID=%s",
                (issue_id,))
    cur.execute("UPDATE Books SET AvailableCopies = AvailableCopies + 1 WHERE BookID=%s",
                (book_id,))""", language="python")

    add_section_heading(doc, "9.10", "fix_passwords.py — Migration Utility")
    add_hindi_para(doc,
        "Real-world में अक्सर ऐसे cases आते हैं जब purane plain-text passwords को secure "
        "hashes में migrate करना पड़ता है। हमने इसके लिए एक one-time migration script "
        "बनाया है जो सभी existing users के passwords को bcrypt में convert करता है।")

    add_screenshot_placeholder(doc, "9.2",
        "VS Code में Project File Tree — Complete Module Structure",
        height_inches=4.5)

    add_page_break(doc)
