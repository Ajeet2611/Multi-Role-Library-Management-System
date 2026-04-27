"""
Chapters 1-5: Introduction, Literature Review, Problem Statement,
Requirements, Feasibility Study
"""

from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from doc_helpers import *


def chapter_1_introduction(doc):
    add_chapter_heading(doc, 1, "परिचय", "Introduction")

    add_section_heading(doc, "1.1", "Project का संक्षिप्त परिचय (Project Overview)")
    add_hindi_para(doc,
        "वर्तमान digital युग में, हर organization अपने operations को automate "
        "और digitize करने का प्रयास कर रही है। Library जैसी संस्थाएँ, जो हजारों books, "
        "members और daily transactions को handle करती हैं, अब manual register-based "
        "system पर निर्भर नहीं रह सकतीं। यह project — Multi-Role Library Management "
        "System — इसी समस्या का एक comprehensive technical solution है।",
        first_line_indent=Inches(0.3))

    add_hindi_para(doc,
        "यह एक Python-based desktop application है जो Tkinter GUI framework और MySQL "
        "relational database का उपयोग करते हुए एक complete library ecosystem provide "
        "करती है। इसमें multiple user roles (Super Admin, Admin, Student, Teacher), "
        "secure authentication (bcrypt hashing), granular permission system, real-time "
        "analytics dashboard, और inter-user messaging जैसे advanced features शामिल हैं।",
        first_line_indent=Inches(0.3))

    add_hindi_para(doc,
        "इस documentation का उद्देश्य project के हर technical pehlu को detail से explain "
        "करना है — architecture से लेकर implementation तक, security से लेकर future "
        "scalability तक। यह report एक production-grade software के design और development "
        "की पूरी journey को capture करती है।",
        first_line_indent=Inches(0.3))

    add_section_heading(doc, "1.2", "Background और Motivation")
    add_hindi_para(doc,
        "भारत में लाखों educational institutions हैं जिनमें छोटी-बड़ी libraries मौजूद "
        "हैं। एक recent NDLI (National Digital Library of India) report के अनुसार, "
        "देश की 60% से अधिक libraries अभी भी partial-manual या hybrid systems पर depend "
        "करती हैं। इसके पीछे कई कारण हैं — high-cost commercial software, complex "
        "deployment, training की कमी, और local-language support का अभाव।")

    add_hindi_para(doc,
        "एक अनुभव के तौर पर, जब मैंने अपने college library में देखा कि librarian एक "
        "thick register में हर book issue करती हैं और return पर manually fine calculate "
        "करती हैं — तब यह idea आया कि क्यों न एक ऐसा system बनाया जाए जो:")

    add_bullet(doc, "Free aur open-source हो — किसी भी small library afford कर सके")
    add_bullet(doc, "Offline भी काम करे — internet dependency न हो")
    add_bullet(doc, "Multi-role support दे — एक ही system Super Admin, Admin और Students के लिए काम करे")
    add_bullet(doc, "Secure हो — modern cryptography (bcrypt) का use हो")
    add_bullet(doc, "Scalable हो — एक से अधिक institution एक ही codebase use कर सकें")

    add_hindi_para(doc,
        "इन्हीं goals को ध्यान में रखकर इस project की foundation रखी गई।")

    add_section_heading(doc, "1.3", "Project का Scope")
    add_hindi_para(doc,
        "यह project एक complete Library Management System है जो निम्नलिखित functional "
        "areas को cover करता है:")

    add_data_table(doc,
        headers=["Functional Area", "Coverage"],
        rows=[
            ["Authentication", "Secure login (bcrypt), password reset, role-based routing"],
            ["User Management", "Add/Edit/Delete users, role assignment, status tracking"],
            ["Book Management", "CRUD operations, ISBN tracking, multi-copy handling"],
            ["Transactions", "Issue, return, due-date tracking, automatic fine calculation"],
            ["Analytics", "Real-time charts (Pie, Bar) — user/book/role distribution"],
            ["Messaging", "User → Admin queries, Admin replies, status tracking"],
            ["Reports", "Excel export, transaction history, member activity logs"],
            ["Multi-Tenancy", "InstitutionID-based isolation — multiple orgs supported"],
        ],
        table_num=1,
        caption="Project Scope — Functional Areas",
        col_widths=[Inches(2.0), Inches(4.5)])

    add_section_heading(doc, "1.4", "Documentation का Structure")
    add_hindi_para(doc,
        "यह documentation 16 chapters में organized है, जिसमें project के हर pehlu को "
        "systematic तरीके से cover किया गया है:")

    chapters = [
        ("Chapter 1", "Introduction", "Project का परिचय, motivation और scope"),
        ("Chapter 2", "Literature Review", "Existing systems का analysis और comparative study"),
        ("Chapter 3", "Problem Statement", "Specific problems जो solve किए गए, objectives"),
        ("Chapter 4", "System Requirements", "Hardware, software, functional और non-functional requirements"),
        ("Chapter 5", "Feasibility Study", "Technical, economic, operational feasibility"),
        ("Chapter 6", "System Architecture", "3-layer architecture, design patterns, data flow"),
        ("Chapter 7", "Tech Stack Deep Dive", "हर technology का selection rationale"),
        ("Chapter 8", "Database Design", "ER diagram, schemas, normalization, indexes"),
        ("Chapter 9", "Module-wise Implementation", "हर Python module का detailed walkthrough"),
        ("Chapter 10", "Security Implementation", "bcrypt, RBAC, SQL injection prevention"),
        ("Chapter 11", "UI/UX Design", "Interface screenshots और design decisions"),
        ("Chapter 12", "Testing & Validation", "Test cases, results, coverage"),
        ("Chapter 13", "Results & Output", "Application screenshots और real-world performance"),
        ("Chapter 14", "Challenges & Limitations", "Engineering challenges जो overcome किए गए"),
        ("Chapter 15", "Future Enhancements", "Roadmap और upcoming features"),
        ("Chapter 16", "Conclusion", "Final thoughts और key takeaways"),
    ]
    add_data_table(doc,
        headers=["Chapter", "Title", "Description"],
        rows=chapters,
        table_num=2,
        caption="Documentation Structure",
        col_widths=[Inches(0.9), Inches(1.6), Inches(4.0)])

    add_section_heading(doc, "1.5", "इस Document को कैसे पढ़ें")
    add_hindi_para(doc,
        "यह documentation linear तरीके से design की गई है — Chapter 1 से शुरू करके "
        "Chapter 16 तक हर section एक कहानी की तरह आगे बढ़ता है। पर अगर आप किसी specific "
        "topic में interested हैं, तो table of contents से directly वहाँ jump कर सकते हैं।")

    add_callout_box(doc, "Reading Tip",
        "Technical terms जैसे bcrypt, Tkinter, FigureCanvasTkAgg, RBAC आदि English में ही "
        "रखे गए हैं — यह industry-standard practice है ताकि actual code और documentation "
        "के बीच कोई gap न रहे। पर हर technical term का meaning Hindi में explain किया गया है।")

    add_page_break(doc)


def chapter_2_literature_review(doc):
    add_chapter_heading(doc, 2, "साहित्य समीक्षा", "Literature Review")

    add_section_heading(doc, "2.1", "Existing Systems का Overview")
    add_hindi_para(doc,
        "कोई भी नया system design करने से पहले मौजूदा solutions को study करना ज़रूरी है। "
        "इस section में हम 5 major existing library management systems का analysis करेंगे "
        "— commercial और open-source दोनों।",
        first_line_indent=Inches(0.3))

    add_section_heading(doc, "2.2", "Commercial Solutions", level=2)

    add_section_heading(doc, "2.2.1", "Koha (Open-Source Web-Based)", level=2)
    add_hindi_para(doc,
        "Koha एक widely-used open-source library management system है जो Perl में लिखा "
        "गया है। यह web-based है और MySQL/MariaDB use करता है। इसमें cataloguing, "
        "circulation, acquisitions और serials management जैसे features हैं।")
    add_hindi_para(doc, "मुख्य Limitations:", bold=True)
    add_bullet(doc, "Setup बहुत complex — Apache, Perl, Zebra search engine — सब configure करना पड़ता है")
    add_bullet(doc, "Hardware requirements high — minimum 4GB RAM, dedicated server")
    add_bullet(doc, "Customization के लिए Perl की knowledge ज़रूरी — जो rare है आज के time में")
    add_bullet(doc, "Mobile-friendly interface नहीं")

    add_section_heading(doc, "2.2.2", "SLiMS (Senayan Library Management System)", level=2)
    add_hindi_para(doc,
        "Indonesia से originated, SLiMS एक PHP-based open-source LMS है। यह छोटी libraries "
        "के लिए popular है क्योंकि setup आसान है।")
    add_hindi_para(doc, "Limitations:", bold=True)
    add_bullet(doc, "PHP-only deployment — Python ecosystem की flexibility नहीं")
    add_bullet(doc, "Multi-tenancy support नहीं — हर institution के लिए separate installation")
    add_bullet(doc, "Modern UI/UX nहीं — design dated है")

    add_section_heading(doc, "2.2.3", "Libsys (Commercial Indian Solution)", level=2)
    add_hindi_para(doc,
        "Libsys एक commercial library automation software है जो भारत में universities और "
        "research institutes में popular है।")
    add_hindi_para(doc, "Limitations:", bold=True)
    add_bullet(doc, "License cost बहुत high — small libraries afford नहीं कर सकतीं")
    add_bullet(doc, "Customization के लिए vendor पर dependency")
    add_bullet(doc, "Source code closed — security audit possible नहीं")

    add_section_heading(doc, "2.2.4", "Manual Register Systems", level=2)
    add_hindi_para(doc,
        "अभी भी 60%+ Indian libraries (especially school/college libraries) पुराने "
        "register-based system पर चलती हैं। यह सबसे common 'baseline' है जिसके against "
        "हमारा system compete करता है।")
    add_hindi_para(doc, "Critical Issues:", bold=True)
    add_bullet(doc, "Data loss risk — paper destroy हो सकता है")
    add_bullet(doc, "Search inefficient — एक book ढूँढने में minutes लगते हैं")
    add_bullet(doc, "Reporting impossible — कोई analytics या trend visibility नहीं")
    add_bullet(doc, "Fine calculation error-prone")

    add_section_heading(doc, "2.3", "Comparative Analysis Table")
    add_data_table(doc,
        headers=["Feature", "Koha", "SLiMS", "Libsys", "Manual", "Our System"],
        rows=[
            ["Cost", "Free", "Free", "₹50K+/year", "Low", "Free"],
            ["Setup Complexity", "Very High", "Medium", "Medium", "Low", "Low"],
            ["Multi-Institution", "❌", "❌", "✓", "❌", "✓"],
            ["bcrypt Security", "✓", "Partial", "✓", "❌", "✓"],
            ["Real-time Charts", "Limited", "❌", "✓", "❌", "✓"],
            ["Built-in Messaging", "❌", "❌", "Limited", "❌", "✓"],
            ["Offline Capable", "❌", "❌", "❌", "✓", "✓"],
            ["Indian Lang Support", "Limited", "❌", "✓", "✓", "✓ (Hinglish)"],
            ["Code Customization", "Hard (Perl)", "Medium (PHP)", "Vendor-only", "N/A", "Easy (Python)"],
        ],
        table_num=3,
        caption="Comparative Analysis — हमारा System vs Existing Solutions",
        col_widths=[Inches(1.5), Inches(0.8), Inches(0.8), Inches(0.9), Inches(0.8), Inches(1.0)])

    add_section_heading(doc, "2.4", "Research Papers और Industry Reports")
    add_hindi_para(doc, "इस project को design करते समय निम्नलिखित studies को reference किया गया:")

    add_bullet(doc, "\"Library Automation in Indian Academic Institutions\" — IFLA Journal, 2023")
    add_bullet(doc, "\"Comparative Study of Open-Source LMS\" — Library Hi Tech, 2022")
    add_bullet(doc, "\"Role-Based Access Control Patterns\" — IEEE Software Engineering, 2021")
    add_bullet(doc, "\"Password Security Best Practices\" — OWASP Foundation, 2024")
    add_bullet(doc, "\"Multi-Tenant SaaS Database Design\" — Microsoft Azure Architecture Guide")

    add_section_heading(doc, "2.5", "Gap Analysis — हमारा System क्यों Different है")
    add_hindi_para(doc,
        "ऊपर के comparative analysis से clear है कि market में मौजूद solutions में "
        "निम्नलिखित gaps हैं जिन्हें हमारा system address करता है:")

    add_numbered(doc, "Cost Gap: Commercial solutions बहुत expensive हैं और open-source solutions complex हैं — हमारा system दोनों के बीच sweet spot है")
    add_numbered(doc, "Multi-Tenancy Gap: Most existing systems single-tenant हैं — हमारा architecture native multi-institution support देता है")
    add_numbered(doc, "Communication Gap: Built-in messaging system rare है — हमने यह first-class feature बनाया है")
    add_numbered(doc, "Modern Security Gap: कई existing systems अभी भी weak hashing (MD5, plain SHA) use करते हैं — हम bcrypt use करते हैं")
    add_numbered(doc, "Setup Gap: हमारा system minimal dependencies (Python + MySQL) के साथ run करता है — कोई web server, कोई complex configuration नहीं")

    add_callout_box(doc, "Pro-Tip",
        "Literature review का असली purpose सिर्फ existing systems list करना नहीं — "
        "बल्कि यह justify करना है कि आपका solution कुछ नया offer करता है। ऊपर का "
        "gap analysis exactly यही करता है।")

    add_page_break(doc)


def chapter_3_problem_statement(doc):
    add_chapter_heading(doc, 3, "समस्या कथन और उद्देश्य",
                        "Problem Statement & Objectives")

    add_section_heading(doc, "3.1", "मुख्य समस्या (Core Problem)")
    add_hindi_para(doc,
        "Indian educational institutions में libraries critical infrastructure हैं — "
        "हर student की learning journey का हिस्सा। पर इन libraries का management आज भी "
        "majority cases में outdated, manual या semi-digital systems से होता है, जिसके "
        "कारण निम्नलिखित समस्याएँ उत्पन्न होती हैं:",
        first_line_indent=Inches(0.3))

    problems = [
        ("Data Integrity Issues",
         "Manual registers में entries miss हो जाती हैं, ink fade हो जाती है, "
         "pages फट सकती हैं — leading to permanent data loss।"),
        ("Inefficient Operations",
         "एक book को locate करने में minutes लग सकते हैं। Issue/Return process slow "
         "है — लंबी queues student time waste करती हैं।"),
        ("Fine Calculation Errors",
         "Manual fine calculation में human errors common हैं। कई बार librarian late "
         "fees calculate करना भूल जाते हैं या gलत करते हैं।"),
        ("No Visibility",
         "Management के पास कोई real-time data नहीं — कितनी books popular हैं, कौन से "
         "students active हैं, कब peak hours हैं — कुछ नहीं पता।"),
        ("Security Risks",
         "Even existing digital systems plain-text passwords store करते हैं। एक data "
         "breach हजारों users के credentials expose कर सकता है।"),
        ("Communication Gap",
         "Students को कोई easy way नहीं library admin से contact करने का। "
         "Suggestion box भी आज के time में outdated है।"),
        ("Scalability Issues",
         "एक college अगर अपनी 5 branches में same system चलाना चाहे — तो हर branch "
         "के लिए separate installation, separate database — managing nightmare।"),
    ]
    for title, desc in problems:
        add_hindi_para(doc, title, bold=True, color=NAVY, size=12, space_after=Pt(2))
        add_hindi_para(doc, desc, space_after=Pt(8))

    add_section_heading(doc, "3.2", "Project Objectives")
    add_hindi_para(doc,
        "उपरोक्त समस्याओं को address करने के लिए, इस project के निम्नलिखित specific, "
        "measurable objectives define किए गए हैं:")

    add_section_heading(doc, "3.2.1", "Primary Objectives", level=2)
    add_numbered(doc, "एक secure, multi-role authentication system implement करना जो bcrypt-level password security provide करे")
    add_numbered(doc, "Complete CRUD-based book management system बनाना जिसमें ISBN tracking, multi-copy handling हो")
    add_numbered(doc, "Automated fine calculation system implement करना — late returns पर ₹5/day automatic")
    add_numbered(doc, "Real-time analytics dashboard बनाना जिसमें pie charts और bar charts हों")
    add_numbered(doc, "Built-in messaging system develop करना — Two-way communication (User ↔ Admin)")
    add_numbered(doc, "Multi-institution support architecture-level implement करना — InstitutionID-based isolation")

    add_section_heading(doc, "3.2.2", "Secondary Objectives", level=2)
    add_numbered(doc, "Excel export capability — librarians को reports generate करने में help")
    add_numbered(doc, "Granular permission system — हर role के लिए customizable permissions")
    add_numbered(doc, "Self-healing schema — application start पर missing tables auto-create")
    add_numbered(doc, "Clean modular code — हर logical unit अलग file में, future maintenance easy")
    add_numbered(doc, "Migration utilities — पुराने plain-text passwords को bcrypt पे migrate करने के लिए script")

    add_section_heading(doc, "3.3", "Success Criteria")
    add_hindi_para(doc,
        "एक project को 'successful' तब माना जाएगा जब निम्नलिखित criteria meet हों:")

    add_data_table(doc,
        headers=["#", "Criterion", "Measurable Goal"],
        rows=[
            ["1", "Login Performance", "< 2 seconds login time including bcrypt verify"],
            ["2", "Book Search", "< 1 second to filter and display matching books"],
            ["3", "Fine Calculation Accuracy", "100% accurate (no manual override needed)"],
            ["4", "Data Isolation", "0 cross-institution data leaks (verified by tests)"],
            ["5", "Code Modularity", "Each Python file < 600 lines, single responsibility"],
            ["6", "Security Standard", "OWASP Top 10 compliance (A02, A03, A07)"],
            ["7", "User Roles", "Minimum 4 roles supported with clear permissions"],
            ["8", "Database Tables", "Minimum 7 tables, all in 3NF"],
        ],
        table_num=4,
        caption="Project Success Criteria",
        col_widths=[Inches(0.4), Inches(2.0), Inches(4.0)])

    add_section_heading(doc, "3.4", "Project Constraints")
    add_hindi_para(doc, "हर project की कुछ constraints होती हैं — हमारी भी हैं:")
    add_bullet(doc, "Time Constraint: 4 months का development window")
    add_bullet(doc, "Budget Constraint: Open-source tools only, कोई paid service नहीं")
    add_bullet(doc, "Hardware Constraint: Minimum 4GB RAM machine पर run होना चाहिए")
    add_bullet(doc, "Internet Constraint: Offline capable होना चाहिए")
    add_bullet(doc, "Skill Constraint: Single developer (Python + MySQL stack)")

    add_screenshot_placeholder(doc, "3.1",
        "Problem-Solution Mapping Diagram — Manual System vs Our Solution",
        height_inches=3.0)

    add_page_break(doc)


def chapter_4_requirements(doc):
    add_chapter_heading(doc, 4, "System आवश्यकताएँ", "System Requirements")

    add_section_heading(doc, "4.1", "Hardware Requirements")
    add_hindi_para(doc,
        "इस system को run करने के लिए minimum और recommended hardware specifications "
        "नीचे table में दिए गए हैं। दोनों configurations के लिए application functional "
        "रहेगी, परंतु recommended specs पर performance बेहतर होगी।",
        first_line_indent=Inches(0.3))

    add_data_table(doc,
        headers=["Component", "Minimum", "Recommended"],
        rows=[
            ["Processor (CPU)", "Intel Core i3 / AMD Ryzen 3", "Intel Core i5 / AMD Ryzen 5 या उससे ऊपर"],
            ["RAM", "4 GB", "8 GB या उससे ऊपर"],
            ["Storage", "500 MB free space", "2 GB SSD recommended"],
            ["Display", "1024 × 768 resolution", "1920 × 1080 (Full HD)"],
            ["Operating System", "Windows 10 / Ubuntu 20.04 / macOS 11", "Latest version of OS"],
            ["Network", "Optional (offline mode supported)", "100 Mbps for multi-machine setup"],
            ["Database Server", "Same machine (localhost)", "Dedicated MySQL server"],
        ],
        table_num=5,
        caption="Hardware Requirements Specification",
        col_widths=[Inches(1.7), Inches(2.2), Inches(2.6)])

    add_section_heading(doc, "4.2", "Software Requirements")
    add_data_table(doc,
        headers=["Software", "Version", "Purpose"],
        rows=[
            ["Python", "3.10 या उससे नया", "Core programming language"],
            ["MySQL Server", "8.0+", "Relational database engine"],
            ["MySQL Connector/Python", "8.0+", "Python ↔ MySQL communication"],
            ["bcrypt", "4.0+", "Password hashing library"],
            ["Tkinter", "Built-in with Python", "GUI framework"],
            ["Matplotlib", "3.5+", "Charts और analytics"],
            ["Pillow (PIL)", "9.0+", "Image rendering for icons"],
            ["openpyxl", "3.0+", "Excel file generation"],
            ["pip", "22.0+", "Python package manager"],
            ["Git (optional)", "2.30+", "Version control"],
        ],
        table_num=6,
        caption="Software Requirements Specification",
        col_widths=[Inches(2.0), Inches(1.5), Inches(3.0)])

    add_section_heading(doc, "4.3", "Functional Requirements")
    add_hindi_para(doc,
        "Functional requirements वो specific behaviors हैं जो system को perform करने "
        "हैं। इन्हें हम modules के अनुसार categorize करेंगे:")

    add_section_heading(doc, "4.3.1", "Authentication Module", level=2)
    add_bullet(doc, "FR-AUTH-01: System को username/password के basis पर login allow करना चाहिए")
    add_bullet(doc, "FR-AUTH-02: Passwords bcrypt से hashed होने चाहिए — कभी plain-text में store नहीं")
    add_bullet(doc, "FR-AUTH-03: Successful login पर role-based redirection होनी चाहिए")
    add_bullet(doc, "FR-AUTH-04: Failed login attempts पर appropriate error message")
    add_bullet(doc, "FR-AUTH-05: Logout button सभी dashboards पर available")

    add_section_heading(doc, "4.3.2", "Book Management Module", level=2)
    add_bullet(doc, "FR-BOOK-01: Admin नई book add कर सके (Title, Author, ISBN, copies)")
    add_bullet(doc, "FR-BOOK-02: Admin existing book को edit और delete कर सके")
    add_bullet(doc, "FR-BOOK-03: सभी users available books की list देख सकें")
    add_bullet(doc, "FR-BOOK-04: Book search by title/author/ISBN")
    add_bullet(doc, "FR-BOOK-05: Available copies real-time update हों")

    add_section_heading(doc, "4.3.3", "Transaction Module", level=2)
    add_bullet(doc, "FR-TXN-01: Admin किसी member को book issue कर सके")
    add_bullet(doc, "FR-TXN-02: Default loan period 7 दिन — due date auto-calculated")
    add_bullet(doc, "FR-TXN-03: Return पर fine automatically calculate हो (₹5/day late)")
    add_bullet(doc, "FR-TXN-04: Available copies update हों issue/return पर")
    add_bullet(doc, "FR-TXN-05: Transaction history view available हो")

    add_section_heading(doc, "4.3.4", "User Management Module", level=2)
    add_bullet(doc, "FR-USER-01: Admin नए users add कर सके (with role assignment)")
    add_bullet(doc, "FR-USER-02: User status (Active/Inactive) toggle possible हो")
    add_bullet(doc, "FR-USER-03: User activity logs visible हों admin को")
    add_bullet(doc, "FR-USER-04: Bulk user import via Excel (future enhancement)")

    add_section_heading(doc, "4.3.5", "Messaging Module", level=2)
    add_bullet(doc, "FR-MSG-01: User admin को message भेज सके")
    add_bullet(doc, "FR-MSG-02: Admin user के messages देख सके और reply कर सके")
    add_bullet(doc, "FR-MSG-03: Message status track हो (OPEN/CLOSED)")
    add_bullet(doc, "FR-MSG-04: Timestamp हर message पर")

    add_section_heading(doc, "4.3.6", "Analytics Module", level=2)
    add_bullet(doc, "FR-ANALYTICS-01: Total users count display")
    add_bullet(doc, "FR-ANALYTICS-02: Pie chart — Active vs Inactive members")
    add_bullet(doc, "FR-ANALYTICS-03: Bar chart — Role distribution")
    add_bullet(doc, "FR-ANALYTICS-04: Real-time data — हर dashboard refresh पर fresh data")

    add_section_heading(doc, "4.4", "Non-Functional Requirements")
    add_hindi_para(doc,
        "Non-functional requirements (NFRs) system की quality attributes हैं — "
        "performance, security, usability आदि।")

    add_data_table(doc,
        headers=["Category", "Requirement", "Acceptance Criteria"],
        rows=[
            ["Performance", "Login response time", "< 2 seconds (including bcrypt)"],
            ["Performance", "Book search response", "< 1 second for 10,000+ books"],
            ["Performance", "Dashboard load time", "< 3 seconds with charts"],
            ["Security", "Password hashing", "bcrypt with cost factor 12+"],
            ["Security", "SQL injection prevention", "100% parameterized queries"],
            ["Security", "Session management", "Role-based access enforced everywhere"],
            ["Usability", "Learnability", "New user productive within 15 minutes"],
            ["Usability", "Error messages", "User-friendly Hindi/English messages"],
            ["Reliability", "Crash recovery", "Database state preserved on crash"],
            ["Maintainability", "Code modularity", "Each file < 600 lines"],
            ["Portability", "OS support", "Windows, macOS, Linux"],
            ["Scalability", "Multi-tenant", "100+ institutions on single DB"],
        ],
        table_num=7,
        caption="Non-Functional Requirements Specification",
        col_widths=[Inches(1.3), Inches(2.0), Inches(3.2)])

    add_section_heading(doc, "4.5", "User Roles और Permissions Matrix")
    add_data_table(doc,
        headers=["Permission", "Super Admin", "Admin", "User"],
        rows=[
            ["View Books", "✓", "✓", "✓"],
            ["Add Book", "✓", "✓", "❌"],
            ["Edit Book", "✓", "✓", "❌"],
            ["Delete Book", "✓", "✓", "❌"],
            ["Issue Book", "✓", "✓", "❌"],
            ["Return Book", "✓", "✓", "❌"],
            ["Add User", "✓", "Limited", "❌"],
            ["Manage Permissions", "✓", "❌", "❌"],
            ["View Analytics", "✓", "✓", "❌"],
            ["Export to Excel", "✓", "✓", "❌"],
            ["Send Message", "✓", "✓", "✓"],
            ["Reply to Message", "✓", "✓", "❌"],
            ["View Activity Logs", "✓", "✓", "Own only"],
            ["Multi-Institution View", "✓", "❌", "❌"],
        ],
        table_num=8,
        caption="User Roles and Permissions Matrix",
        col_widths=[Inches(2.3), Inches(1.4), Inches(1.4), Inches(1.4)])

    add_callout_box(doc, "Design Note",
        "Permissions architecture के level पर enforce होती हैं — हर sensitive operation "
        "से पहले `permissions.has_permission(user, code)` check चलता है। यह defense-in-depth "
        "approach है — UI में button hide करने के अलावा backend में भी validation है।")

    add_page_break(doc)


def chapter_5_feasibility(doc):
    add_chapter_heading(doc, 5, "व्यवहार्यता अध्ययन", "Feasibility Study")

    add_section_heading(doc, "5.1", "Feasibility Study क्या है?")
    add_hindi_para(doc,
        "Feasibility study किसी भी project को start करने से पहले की एक critical exercise है। "
        "इसमें यह evaluate किया जाता है कि project technically achievable है या नहीं, "
        "economically viable है या नहीं, और operationally implement हो सकता है या नहीं। "
        "अगर feasibility study negative आए तो project को redesign या abandon करना पड़ता है।",
        first_line_indent=Inches(0.3))

    add_section_heading(doc, "5.2", "Technical Feasibility")
    add_hindi_para(doc,
        "Technical feasibility evaluate करती है कि क्या available technology, tools "
        "और skills इस project को build करने के लिए sufficient हैं।")

    add_hindi_para(doc, "हमारी Technical Assessment:", bold=True)
    add_bullet(doc, "Python 3.10+ widely available और open-source है")
    add_bullet(doc, "MySQL एक mature, battle-tested RDBMS है — millions of installations")
    add_bullet(doc, "Tkinter Python के साथ built-in आता है — कोई extra licensing नहीं")
    add_bullet(doc, "bcrypt एक standard library है — pip से install हो जाती है")
    add_bullet(doc, "Matplotlib analytics के लिए perfect — Tkinter integration available")
    add_bullet(doc, "Documentation और community support all libraries के लिए excellent")

    add_callout_box(doc, "Conclusion",
        "Project technically 100% feasible है। सभी required tools open-source और freely "
        "available हैं। कोई rare expertise की ज़रूरत नहीं — Python + MySQL skills market "
        "में easily available हैं।")

    add_section_heading(doc, "5.3", "Economic Feasibility")
    add_hindi_para(doc,
        "Economic feasibility evaluate करती है कि project का cost vs benefit ratio "
        "favorable है या नहीं।")

    add_hindi_para(doc, "Cost Analysis:", bold=True)
    add_data_table(doc,
        headers=["Component", "Cost (INR)", "Notes"],
        rows=[
            ["Python", "₹0", "Open-source, free"],
            ["MySQL Community", "₹0", "GPL license — free for use"],
            ["bcrypt, Pillow, Matplotlib", "₹0", "Open-source PyPI packages"],
            ["Tkinter", "₹0", "Built into Python"],
            ["Development Hardware", "₹40,000–60,000", "Standard developer laptop"],
            ["Developer Time (4 months)", "₹2,00,000+", "If contracted out (avg)"],
            ["Hosting/Server (optional)", "₹500–1,000/month", "Shared MySQL hosting"],
            ["Total One-Time Cost", "≈ ₹2,40,000", "Most is human effort"],
            ["Recurring Cost", "₹0–12,000/year", "Optional hosting"],
        ],
        table_num=9,
        caption="Project Cost Breakdown",
        col_widths=[Inches(2.5), Inches(1.5), Inches(2.5)])

    add_hindi_para(doc, "Benefit Analysis:", bold=True)
    add_bullet(doc, "Replaces ₹50,000+/year commercial LMS subscriptions")
    add_bullet(doc, "Saves librarian time (~2 hours/day) → 600+ hours/year value")
    add_bullet(doc, "Reduces book loss/misplacement — सीधा monetary saving")
    add_bullet(doc, "Better analytics → smarter book purchases — budget optimization")
    add_bullet(doc, "Single codebase serves multiple branches — economy of scale")

    add_callout_box(doc, "ROI Analysis",
        "एक mid-size college (5000 students) के लिए: यह system 1 year में easily "
        "₹1,00,000+ का value generate करता है (subscription savings + librarian time "
        "+ reduced losses). Break-even ~6 months में achievable है।")

    add_section_heading(doc, "5.4", "Operational Feasibility")
    add_hindi_para(doc,
        "Operational feasibility यह देखती है कि क्या end-users (librarians, admins, "
        "students) इस system को adopt और use कर पाएँगे।")

    add_hindi_para(doc, "Key Considerations:", bold=True)
    add_bullet(doc, "UI Tkinter में बना है — clean, simple, intuitive")
    add_bullet(doc, "हर role के लिए dedicated dashboard — confusion नहीं")
    add_bullet(doc, "Training requirement minimal — < 30 minutes का onboarding काफी")
    add_bullet(doc, "Hindi में error messages possible — local language support")
    add_bullet(doc, "Offline capability — internet outages से कोई issue नहीं")

    add_section_heading(doc, "5.5", "Schedule Feasibility")
    add_hindi_para(doc,
        "Project को 4 months में deliver करने का target था। नीचे actual timeline है:")
    add_data_table(doc,
        headers=["Phase", "Duration", "Deliverables"],
        rows=[
            ["Planning & Requirements", "2 weeks", "SRS document, ER diagram"],
            ["Database Design", "1 week", "Schema, normalization, indexes"],
            ["Authentication Module", "2 weeks", "Login, bcrypt, role routing"],
            ["Book Management", "3 weeks", "CRUD operations, search"],
            ["Transaction Module", "2 weeks", "Issue/Return, fine logic"],
            ["User Management", "2 weeks", "Add/Edit users, roles"],
            ["Messaging System", "1 week", "User-Admin communication"],
            ["Analytics Dashboard", "2 weeks", "Matplotlib integration"],
            ["Testing & Bug Fixes", "2 weeks", "Test cases, fixes"],
            ["Documentation", "1 week", "User manual, technical docs"],
        ],
        table_num=10,
        caption="Project Schedule (16-week breakdown)",
        col_widths=[Inches(2.0), Inches(1.2), Inches(3.3)])

    add_section_heading(doc, "5.6", "Risk Assessment")
    add_data_table(doc,
        headers=["Risk", "Probability", "Impact", "Mitigation"],
        rows=[
            ["Database corruption", "Low", "High", "Regular backups, transaction logs"],
            ["Tkinter performance issue", "Medium", "Medium", "Lightweight queries, pagination"],
            ["MySQL version incompatibility", "Low", "Medium", "Test on multiple versions"],
            ["bcrypt slowness on weak HW", "Low", "Low", "Configurable cost factor"],
            ["UI complexity for non-tech users", "Medium", "High", "Iterative UX testing"],
            ["Multi-institution data leak bug", "Low", "Critical", "Architecture-level filter + tests"],
        ],
        table_num=11,
        caption="Risk Assessment Matrix",
        col_widths=[Inches(2.0), Inches(1.0), Inches(1.0), Inches(2.5)])

    add_callout_box(doc, "Final Feasibility Verdict",
        "सभी 4 dimensions पर project feasible है — Technical (✓), Economic (✓), "
        "Operational (✓), Schedule (✓). Risk assessment भी manageable है। "
        "Project को proceed करने की recommendation दी जाती है।")

    add_page_break(doc)
