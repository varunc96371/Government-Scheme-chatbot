import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'schemeai.db')

def get_db_connection():
    """
    Establishes and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    return conn

def init_db():
    """
    Initializes the SQLite database tables and seeds sample government schemes.
    Handles migration automatically if schemes table is missing or lacks the 90 seeded schemes.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if schemes table exists and check if it needs migration (missing columns or needs reseeding for 90 schemes)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schemes'")
    if cursor.fetchone():
        cursor.execute("PRAGMA table_info(schemes)")
        columns = [row[1] for row in cursor.fetchall()]
        
        cursor.execute("SELECT COUNT(*) FROM schemes")
        count = cursor.fetchone()[0]
        
        # If required_documents column is missing, or schemes count is less than 90 (15 per category * 6 categories)
        if 'required_documents' not in columns or count < 90:
            print(f"Database update required: schemes table has only {count} schemes. Dropping and reseeding schemes table...")
            cursor.execute("DROP TABLE schemes")
            conn.commit()
    
    # 1. Create Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

    # Add email column to existing users table if it is missing
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]

    if 'email' not in user_columns:
        print("Database update required: adding email column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")

        conn.commit()
    
    # 2. Create Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT NOT NULL, -- 'user' or 'bot'
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Create Schemes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schemes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL, -- 'student', 'farmer', 'women', 'senior_citizen', 'unemployed', 'differently_abled'
            description TEXT NOT NULL,
            eligibility TEXT NOT NULL,
            benefits TEXT NOT NULL,
            required_documents TEXT NOT NULL,
            portal_link TEXT NOT NULL
        )
    ''')

    # 4. Create Feedback Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    
    # 5. Seed sample schemes (15 per category * 6 categories = 90 schemes total)
    cursor.execute('SELECT COUNT(*) FROM schemes')
    if cursor.fetchone()[0] == 0:
        seed_schemes = [
            # ==================== CATEGORY: STUDENT (15 Schemes) ====================
    (
        "PM Vidyalaxmi Scheme",
        "student",
        "Financial aid and interest subvention for students pursuing higher education.",
        "Indian national students securing admission in higher education institutions in India or abroad.",
        "Provides collateral-free and third-party-guarantee-free education loans up to ₹7.5 Lakhs with 3% interest subvention.",
        "Aadhaar Card, Admission Letter from Institution, Fee Structure Document, Income Certificate of parents, Academic Marksheets (Class 10/12/Graduation).",
        "https://pmvidyalaxmi.co.in/"
    ),
    (
        "Post Matric Scholarship Scheme",
        "student",
        "Financial assistance for post-matriculation or post-secondary courses.",
        "Students belonging to SC, ST, OBC, or EWS categories with family annual income less than ₹2.5 Lakhs.",
        "100% reimbursement of compulsory non-refundable fees and monthly maintenance allowance.",
        "Aadhaar Card, Caste Certificate (SC/ST/OBC), Income Certificate, Fee Receipt, Academic Marksheets, Bank Account Passbook.",
        "https://scholarships.gov.in/"
    ),
    (
        "National Means-cum-Merit Scholarship (NMMSS)",
        "student",
        "Scholarship for gifted EWS class IX-XII students to reduce dropouts.",
        "Students of class IX with family income less than ₹3.5 Lakhs and scoring minimum 55% marks in class VIII.",
        "An annual scholarship of ₹12,000 (₹1,000 per month) for classes IX to XII in government/government-aided schools.",
        "Aadhaar Card, Class VIII Marksheet, Parental Income Certificate, Caste/Category Certificate.",
        "https://scholarships.gov.in/"
    ),
    (
        "Pragati Scholarship Scheme for Girl Students",
        "student",
        "Financial assistance for girl students pursuing technical diploma or degree education.",
        "Maximum 2 girl children per family, admitted in 1st year degree/diploma technical courses with family income below ₹8 Lakhs.",
        "₹50,000 per annum for tuition fees, study materials, computer/equipment purchase.",
        "Aadhaar Card, Class 10 & 12 Marksheets, Income Certificate, Fee Receipt, AICTE Course Registration Receipt.",
        "https://scholarships.gov.in/"
    ),
    (
        "Saksham Scholarship Scheme for Specially Abled Students",
        "student",
        "Special scholarship encouraging differently-abled youth to pursue technical education.",
        "Students with disability of not less than 40% admitted in AICTE approved technical colleges with family income below ₹8 Lakhs.",
        "₹50,000 per annum for tuition fee reimbursement, purchase of books, equipment, and assistive software.",
        "Aadhaar Card, Disability Certificate (40%+), Admission Letter, Fee Receipt, Family Income Certificate.",
        "https://scholarships.gov.in/"
    ),
    (
        "AICTE Swanath Scholarship Scheme",
        "student",
        "Financial aid for orphans, children of parents deceased due to COVID-19, and wards of Armed Forces martyrs.",
        "Orphans or wards of martyrs studying in AICTE approved diploma/degree institutions with family income under ₹8 Lakhs.",
        "₹50,000 per annum towards educational expenses, boarding, and textbook purchases.",
        "Death certificate of parents / Martyr proof, Bonafide Student Certificate, Aadhaar Card, Income Certificate.",
        "https://scholarships.gov.in/"
    ),
    (
        "Prime Minister's Research Fellowship (PMRF)",
        "student",
        "Attracting top talent to doctoral (Ph.D.) programs in premier institutions like IITs and IISc.",
        "B.Tech/M.Tech/M.Sc graduates with minimum 8.0 CGPA or qualifying GATE score securing admission in Ph.D.",
        "Monthly fellowship of ₹70,000 to ₹80,000 plus an annual research contingency grant of ₹2 Lakhs for 5 years.",
        "GATE scorecard, Academic Transcripts, Ph.D. Admission Letter, Research Proposal, Recommendation Letters.",
        "https://www.pmrf.in/"
    ),
    (
        "Ishan Uday Special Scholarship Scheme",
        "student",
        "Promoting higher education among youth from the North Eastern Region (NER).",
        "Students with domicile of North Eastern states who passed Class XII and secured admission in general/technical degree courses.",
        "Monthly financial stipend of ₹5,400 for general degree and ₹7,800 for professional/medical/engineering degrees.",
        "North-East Domicile Certificate, Class 12 Marksheet, College Admission Slip, Parental Annual Income Certificate.",
        "https://scholarships.gov.in/"
    ),
    (
        "Central Sector Scheme of Scholarship for College and University Students",
        "student",
        "Financial support to meritorious students from low-income families to meet day-to-day college expenses.",
        "Students scoring above 80th percentile in Class 12 board exams pursuing regular degree courses with family income below ₹4.5 Lakhs.",
        "₹12,000 per annum for the first 3 years of undergraduate study and ₹20,000 per annum at postgraduate level.",
        "Class 12 Passing Certificate & Marksheet, Family Income Certificate, College Joining Report, Bank Passbook.",
        "https://scholarships.gov.in/"
    ),
    (
        "Prime Minister's Scholarship Scheme (PMSS)",
        "student",
        "Encouraging higher technical and professional education for wards of ex-servicemen and police personnel.",
        "Dependent wards and widows of deceased/ex-service personnel of Armed Forces and Central Armed Police Forces (CAPF).",
        "Monthly scholarship of ₹2,500 for boys and ₹3,000 for girls pursuing recognized professional degree courses.",
        "Ex-serviceman PPO / Discharge Book, College Admission Letter, Marksheets of Class 12/Diploma, Relationship Certificate.",
        "https://www.desw.gov.in/"
    ),
    (
        "PM YASASVI Scholarship Scheme",
        "student",
        "Top-class school education scholarship for meritorious Other Backward Classes (OBC), EWS, and DNT students.",
        "Students of Class 9 and Class 11 belonging to OBC, EBC, or DNT categories with parental income less than ₹2.5 Lakhs.",
        "Scholarship up to ₹75,000 per year for Class 9–10 and up to ₹1,25,000 per year for Class 11–12 covering tuition and hostel fees.",
        "Aadhaar Card, Category Certificate (OBC/EBC/DNT), Income Certificate, School Bonafide Certificate, Previous Year Marksheet.",
        "https://scholarships.gov.in/"
    ),
    (
        "National Overseas Scholarship (NOS)",
        "student",
        "Financial aid for students from disadvantaged communities to pursue Master's or Ph.D. degrees in top foreign universities.",
        "Low-income students belonging to SC, de-notified nomadic tribes, and landless agricultural laborers with income below ₹8 Lakhs.",
        "Full tuition fee reimbursement, annual living maintenance allowance of up to $15,400 / £9,900, contingency fees, and international airfare.",
        "Offer Letter from Top 500 QS Ranked Foreign University, Caste Certificate, Income Certificate, Passport, Academic Transcripts.",
        "https://www.myscheme.gov.in/schemes/nos-sc"
    ),
    (
        "Central Sector Interest Subsidy Scheme (CSIS)",
        "student",
        "Full interest subvention on education loans during moratorium period for students from economically weaker sections.",
        "Students with family annual gross income up to ₹4.5 Lakhs taking education loans for approved professional/technical courses in India.",
        "Government pays 100% interest during the study period plus one year after course completion, reducing loan burden.",
        "Income Certificate from authorized revenue officer, Loan Sanction Letter, Bonafide Student Certificate, Aadhaar Card.",
        "https://www.education.gov.in/"
    ),
    (
        "Pre-Matric Scholarship Scheme for Minorities",
        "student",
        "Encouraging parents from minority communities to send their school-age children to school.",
        "Students from Muslim, Christian, Sikh, Buddhist, Jain, or Parsi communities studying in classes 1 to 10 with family income below ₹1 Lakh.",
        "Admission fee, tuition fee reimbursement, and maintenance allowance directly credited to student bank accounts.",
        "Minority Community Self-Declaration, Previous Year School Marksheet (50%+), Parent Income Certificate, Bank Passbook.",
        "https://scholarships.gov.in/"
    ),
    (
        "SHREYAS Scholarship Scheme",
        "student",
        "Higher education fellowships and overseas study assistance for SC and OBC scholars.",
        "Meritorious SC and OBC graduate students pursuing M.Phil, Ph.D., and post-doctoral research in Indian universities.",
        "Monthly fellowship equivalent to JRF/SRF rates (₹37,000 to ₹42,000 per month) plus annual contingency grants.",
        "Caste Certificate, University Admission / Registration Order, Research Synopsis, Post-graduation Marksheet, Bank Account Details.",
        "https://socialjustice.gov.in/"
    ),

    # ==================== CATEGORY: FARMER (15 Schemes) ====================
    (
        "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "farmer",
        "Direct income support of ₹6,000 annually to all landholding farmer families across the country.",
        "All landholding farmer families having cultivable land in their names (subject to exclusion criteria for high income earners).",
        "₹6,000 per year transferred directly into Aadhaar-seeded bank accounts in three equal installments of ₹2,000 every 4 months.",
        "Aadhaar Card, Land Ownership Papers (Khatauni/Patta), Aadhaar-linked Bank Account Passbook, Active Mobile Number.",
        "https://pmkisan.gov.in/"
    ),
    (
        "PM Fasal Bima Yojana (PMFBY)",
        "farmer",
        "Comprehensive crop loss insurance coverage against natural calamities, droughts, floods, pests, and unseasonal rainfall.",
        "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas.",
        "Comprehensive financial compensation for crop failure with farmers paying only 1.5% premium for Rabi, 2% for Kharif, and 5% for commercial crops.",
        "Land Record Document (RoR/Khasra), Sowing Certificate / Crop Sowing Declaration, Bank Account Passbook, Aadhaar Card.",
        "https://pmfby.gov.in/"
    ),
    (
        "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
        "farmer",
        "Per Drop More Crop water efficiency and micro-irrigation drip/sprinkler subsidy for farmers.",
        "All categories of farmers owning cultivable land, with special subsidy focus on small and marginal farmers.",
        "Up to 55% financial subsidy for small & marginal farmers (45% for other farmers) on installing drip and sprinkler irrigation systems.",
        "Land Ownership Records (7/12 extract / Patta), Electricity Connection Receipt (if pump operated), Aadhaar Card, Bank Details, Quotation of system.",
        "https://pmksy.gov.in/"
    ),
    (
        "Soil Health Card Scheme",
        "farmer",
        "Scientific soil nutrient testing and customized fertilizer advisory issued to farmers once every 3 years.",
        "All farmers owning or cultivating farm plots in India.",
        "Free soil sample analysis report showing levels of 12 nutrients, with precise chemical and bio-fertilizer dosage recommendations.",
        "Land Identification Number, Aadhaar Card, Farmer Contact Details.",
        "https://soilhealth.dac.gov.in/"
    ),
    (
        "Paramparagat Krishi Vikas Yojana (PKVY)",
        "farmer",
        "Promoting organic farming, cluster cultivation, zero chemical inputs, and organic PGS certification.",
        "Farmers willing to form clusters of 20 or more hectares and transition to traditional/organic agricultural practices.",
        "Financial assistance of ₹50,000 per hectare for 3 years, of which ₹31,000 is directly paid for organic seeds, bio-fertilizers, and botanical extracts.",
        "Aadhaar Card, Land Revenue Records, Farmer Group/Cluster Resolution, Bank Account Passbook.",
        "https://jaivikkheti.in/"
    ),
    (
        "PM Kisan Maandhan Yojana (PM-KMY)",
        "farmer",
        "Old age social security pension scheme for small and marginal landholding farmers.",
        "Small and marginal farmers aged between 18 and 40 years possessing cultivable land up to 2 hectares.",
        "Guaranteed minimum pension of ₹3,000 per month upon reaching 60 years of age, with 50% spousal family pension on subscriber demise.",
        "Aadhaar Card, Land Possession Records / Khasra-Khatauni, Savings Bank Account Details, Nominee Aadhaar Card.",
        "https://maandhan.in/"
    ),
    (
        "Kisan Credit Card (KCC) Scheme",
        "farmer",
        "Adequate and timely institutional credit for farmers to meet cultivation and farm investment expenses.",
        "All individual farmers, joint borrowers, tenant farmers, oral lessees, sharecroppers, and SHGs of farmers.",
        "Revolving cash credit limit up to ₹3 Lakhs at an effective concessional interest rate of only 4% per annum upon prompt repayment.",
        "Land Record Proof, Identity and Address Proof (Aadhaar/Voter ID), Passport size photograph, No-Dues Certificate from local banks.",
        "https://www.myscheme.gov.in/schemes/kcc"
    ),
    (
        "Sub-Mission on Agricultural Mechanization (SMAM)",
        "farmer",
        "Promoting farm mechanization and modern implements to improve productivity and reduce human drudgery.",
        "Individual farmers, agricultural graduates, cooperative societies, Farmer Producer Organizations (FPOs), and Panchayats.",
        "Subsidies from 40% to 50% for purchasing tractors, power tillers, rotavators, and setting up Custom Hiring Centers (up to ₹10 Lakhs subsidy).",
        "Aadhaar Card, Land Ownership Copy, Caste Certificate (if SC/ST), Bank Passbook, Equipment Quotation from authorized dealer.",
        "https://agrimachinery.nic.in/"
    ),
    (
        "National Mission for Sustainable Agriculture (NMSA)",
        "farmer",
        "Promoting climate-resilient farming, rainfed area development, integrated farming systems, and resource conservation.",
        "Farmers located in rainfed and drought-vulnerable agro-climatic zones.",
        "Financial support up to 50% for constructing on-farm water harvesting ponds, vermicompost units, and adopting agroforestry.",
        "Land Records (Khatoni/Khasra), Aadhaar Card, Bank Account Details, Farm Project Plan verified by agriculture officer.",
        "https://nmsa.dac.gov.in/"
    ),
    (
        "Interest Subvention Scheme for Short Term Crop Loans",
        "farmer",
        "Concessional interest rate for short-term farm crop credit through cooperative and commercial banks.",
        "Farmers taking short-term agricultural production credit up to ₹3 Lakhs through KCC.",
        "Normal interest rate of 7% subsidized to 4% effective interest rate through 3% Prompt Repayment Incentive (PRI).",
        "Kisan Credit Card, Crop Loan Account Details, Land Sowing Records, Aadhaar Card.",
        "https://www.nabard.org/"
    ),
    (
        "Rashtriya Krishi Vikas Yojana (RKVY-RAFTAAR)",
        "farmer",
        "Grants and financial assistance for infrastructure creation, post-harvest management, and agricultural entrepreneurship.",
        "Farmers, youth agri-entrepreneurs, self-help groups, and farmer cooperatives.",
        "Seed-stage funding up to ₹25 Lakhs for agri-startups, alongside community grants for post-harvest cold storage and grain drying centers.",
        "Detailed Business Project Report, Land Record or Lease Agreement, Aadhaar Card, Pan Card, Bank Account Details.",
        "https://www.myscheme.gov.in/schemes/rkvy-raftaar"
    ),
    (
        "National Livestock Mission (NLM)",
        "farmer",
        "Financial subsidy for setting up poultry, sheep, goat, piggery breeding farms and fodder production units.",
        "Individual farmers, rural entrepreneurs, Farmer Producer Organizations (FPOs), self-help groups, and joint liability groups.",
        "50% back-ended capital subsidy up to ₹50 Lakhs for sheep/goat breeding farms, and up to ₹25 Lakhs for poultry parent farm units.",
        "Land Documents / Lease Agreement (minimum 10 years), Detailed Project Report (DPR), Bank Loan Sanction Letter, KYC Documents.",
        "https://nlm.udyamimitra.in/"
    ),
    (
        "PM Matsya Sampada Yojana (PMMSY)",
        "farmer",
        "Harnessing fisheries potential through modern aquaculture, biofloc units, fish feed plants, and deep-sea vessels.",
        "Fishers, fish farmers, fish workers, fisheries cooperatives, self-help groups, and private entrepreneurs.",
        "Financial subsidy of 40% for general category and 60% for women/SC/ST for ponds, cage culture, biofloc, re-circulatory systems (RAS), and ice trucks.",
        "Aadhaar Card, Land / Water Body Ownership or Lease Deed, Project Proposal, Bank Passbook, Caste Certificate (if SC/ST).",
        "https://pmmsy.dof.gov.in/"
    ),
    (
        "Pradhan Mantri Kisan Sampada Yojana",
        "farmer",
        "Creating modern infrastructure for mega food parks, agro-processing clusters, and cold chain logistics.",
        "Food processing entrepreneurs, farmer producer organizations, and agricultural cooperatives.",
        "Capital grant-in-aid up to 50% of eligible project cost (up to ₹5 Crore) for food processing and value-addition units.",
        "Detailed Project Report (DPR), Land Purchase/Lease Proof, Bank Loan In-principle Approval, Audited Financial Statements.",
        "https://www.mofpi.gov.in/"
    ),
    (
        "Mission for Integrated Development of Horticulture (MIDH)",
        "farmer",
        "Holistic growth of the horticulture sector including fruits, vegetables, root crops, spices, and flowers.",
        "Horticulture farmers, nursery owners, and farmer producer groups.",
        "Subsidies up to 50% for hi-tech polyhouses, shade net structures, quality planting materials, mushroom units, and pack houses.",
        "Land Record Document (Khasra/Khatauni), Soil & Water Test Report, Quotation of Polyhouse/Equipment, Aadhaar Card, Bank Details.",
        "https://midh.gov.in/"
    ),

    # ==================== CATEGORY: WOMEN (15 Schemes) ====================
    (
        "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
        "women",
        "Maternity cash incentive scheme compensating wage loss and improving maternal and child nutrition.",
        "Pregnant women and lactating mothers for the first child and second girl child (subject to eligibility conditions).",
        "Direct cash benefit of ₹5,000 in two installments for the first child, and ₹6,000 in single installment for a second girl child.",
        "Aadhaar Card of Mother and Husband, MCP Card (Mother & Child Protection Card), Mother's Bank Passbook, Birth Certificate of child.",
        "https://pmmvy.wcd.gov.in/"
    ),
    (
        "Sukanya Samriddhi Yojana (SSY)",
        "women",
        "Small deposit savings scheme for girl children offering highest government interest rate and tax exemption.",
        "Parents or legal guardians of a girl child aged from birth up to 10 years (maximum 2 accounts per family).",
        "High interest rate of 8.2% per annum compounded annually, with complete tax exemption on investment, interest, and maturity under Section 80C.",
        "Birth Certificate of girl child, Identity and Address Proof of parent/guardian (Aadhaar/PAN), Passport photos.",
        "https://www.indiapost.gov.in/"
    ),
    (
        "Pradhan Mantri Ujjwala Yojana (PMUY)",
        "women",
        "Providing clean cooking fuel LPG connections to poor women to eliminate indoor pollution and health risks.",
        "Adult women belonging to BPL households, SC/ST, SECC list, or most backward categories without existing LPG connection.",
        "Free LPG domestic gas connection with deposit-free cylinder, pressure regulator, safety hose pipe, first cylinder refill, and gas stove.",
        "BPL Ration Card / SECC Household proof, Aadhaar Card of all adult family members, Bank Account Passbook of the woman applicant.",
        "https://www.pmuy.gov.in/"
    ),
    (
        "Lakhpati Didi Scheme",
        "women",
        "Empowering rural women through Self Help Groups to achieve a sustainable annual income of over ₹1 Lakh.",
        "Women members of Deendayal Antyodaya Yojana - National Rural Livelihoods Mission (DAY-NRLM) Self Help Groups.",
        "Skill training in drone piloting, LED bulb making, organic fertilizers, livestock rearing, with micro-credit assistance up to ₹5 Lakhs.",
        "Aadhaar Card, SHG Membership Verification Letter, Bank Account Passbook, Proof of Livelihood Activity.",
        "https://nrlm.gov.in/"
    ),
    (
        "Mahila Samman Savings Certificate (MSSC)",
        "women",
        "Government-backed small savings scheme designed specifically for women and girl investors.",
        "Any woman for herself, or a guardian on behalf of a minor girl child.",
        "Guaranteed 7.5% per annum fixed interest rate for a 2-year tenure, with flexible partial withdrawal facility up to 40% after one year.",
        "Account Opening Form (from Post Office / Bank), Aadhaar Card, PAN Card, Passport size photograph.",
        "https://www.indiapost.gov.in/"
    ),
    (
        "Stand-Up India Scheme for Women",
        "women",
        "Facilitating bank loans between ₹10 Lakhs and ₹1 Crore for women establishing greenfield commercial enterprises.",
        "Women entrepreneurs aged 18 years and above starting new business ventures in manufacturing, services, or trading.",
        "Composite bank loans covering up to 85% of project cost with concessional interest rates and credit guarantee cover.",
        "Business Project Report, Proof of Identity and Business Address, Lease Deed or Land Ownership Proof, Bank Account Statements.",
        "https://www.myscheme.gov.in/schemes/suisw"
    ),
    (
        "Beti Bachao Beti Padhao (BBBP)",
        "women",
        "National campaign to prevent gender-biased sex selection and ensure education and safety for every girl child.",
        "All families and girl children across districts with adverse Child Sex Ratio (CSR).",
        "Free school admission drives, institutional delivery incentives, provision of school toilets, and protection against early child marriage.",
        "Birth Certificate of girl child, Aadhaar Card, Residence Proof.",
        "https://www.myscheme.gov.in/schemes/bbbp"
    ),
    (
        "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)",
        "women",
        "Free, comprehensive, high-quality antenatal healthcare services provided on the 9th day of every month.",
        "All pregnant women in their 2nd or 3rd trimester visiting government health centers and hospitals.",
        "Free blood tests, urine investigations, ultrasound diagnostics, iron-folic supplements, and specialist OB-GYN consultations.",
        "PMSMA Mother Card, Aadhaar Card, MCP Card (Mother & Child Protection Card).",
        "https://pmsma.mohfw.gov.in/"
    ),
    (
        "One Stop Centre Scheme (Sakhi)",
        "women",
        "Integrated single-window support for women affected by violence, harassment, or societal abuse.",
        "Any woman facing physical, sexual, emotional, psychological, or economic abuse, irrespective of age, marital status, or caste.",
        "Immediate emergency shelter up to 5 days, police assistance, medical treatment, legal aid, and professional psycho-social counseling under one roof.",
        "No documentation required for receiving emergency aid and rescue support.",
        "https://wcd.gov.in/"
    ),
    (
        "Sakhi Niwas (Working Women Hostel Scheme)",
        "women",
        "Safe, affordable, and clean rental housing for working women located away from their families.",
        "Employed, single, widowed, divorced, or separated women with monthly gross income up to ₹50,000 in cities.",
        "Subsidized lodging with secure premises, nutritious meals, and day care facilities (creche) for children up to 5 years.",
        "Employment Letter / Salary Slip, Aadhaar Card, Address Proof of permanent hometown, Passport size photograph.",
        "https://wcd.gov.in/"
    ),
    (
        "Deendayal Antyodaya Yojana - DAY-NRLM (Self Help Groups)",
        "women",
        "Organizing rural poor women into self-help groups and providing subsidized financial credit for micro-enterprises.",
        "Rural women from poor and marginalized families forming groups of 10 to 20 members.",
        "Revolving Fund of ₹20,000–₹30,000, Community Investment Fund up to ₹1.5 Lakhs, and collateral-free bank loans up to ₹20 Lakhs at 7% interest.",
        "SHG Resolution Book, Member Aadhaar Cards, Group Bank Account Passbook, KYC documents.",
        "https://nrlm.gov.in/"
    ),
    (
        "Kasturba Gandhi Balika Vidyalaya (KGBV)",
        "women",
        "Residential schools providing quality upper primary and secondary education for underprivileged girls.",
        "Girls aged 10–18 from SC, ST, OBC, minority, and BPL families who are dropouts or never enrolled in school.",
        "100% free education, textbooks, uniforms, boarding, lodging, health check-ups, and vocational skill training.",
        "Birth Certificate or Age Affidavit, Caste Certificate (if applicable), BPL Card / Income Proof, Previous School Leaving Certificate.",
        "https://www.education.gov.in/"
    ),
    (
        "Mahila Coir Yojana",
        "women",
        "Skill training and subsidized machinery distribution for women in coconut-producing coastal and rural areas.",
        "Rural female workers and artisans interested in coir yarn spinning and value-added coir craft manufacturing.",
        "75% government subsidy on motorized coir spinning ratts, 2-month training with monthly stipend of ₹3,000, and marketing linkage.",
        "Aadhaar Card, Residence Proof, Age Proof (18+ years), Bank Account Details, Caste Certificate (if SC/ST).",
        "https://msme.gov.in/"
    ),
    (
        "Pradhan Mantri Awas Yojana - Urban (Women Co-Ownership Priority)",
        "women",
        "Housing subsidy scheme mandating female household headship or joint ownership to empower women.",
        "Families belonging to EWS or LIG categories where the pucca house must be registered in the name of the female head or jointly.",
        "Interest subsidy up to ₹2.67 Lakhs on housing loans, or direct central assistance of ₹1.5 Lakhs for individual house construction.",
        "Aadhaar Card of female head and spouse, Income Certificate, Land ownership title, Non-ownership affidavit (no pucca house elsewhere).",
        "https://pmaymis.gov.in/"
    ),
    (
        "PM Vishwakarma for Women Tailors (Darzi) & Artisans",
        "women",
        "Special recognition, toolkit vouchers, and credit for traditional women tailors, basket weavers, and garland makers.",
        "Traditional female artisans and craftspersons practicing hand-skill trades aged 18 years and above.",
        "PM Vishwakarma Certificate & ID, ₹15,000 e-voucher for modern sewing/craft tools, 5-day training with ₹500/day stipend, and 5% interest loans up to ₹3 Lakhs.",
        "Aadhaar Card, Active Mobile Number, Bank Account Passbook, Trade Self-declaration.",
        "https://pmvishwakarma.gov.in/"
    ),

    # ==================== CATEGORY: SENIOR CITIZEN (15 Schemes) ====================
    (
        "Ayushman Bharat (PM-JAY) for Senior Citizens 70+",
        "senior_citizen",
        "Universal free health insurance coverage for all senior citizens aged 70 years and above regardless of income.",
        "Every Indian citizen aged 70 years and above, irrespective of economic standing or family income.",
        "₹5 Lakh free health cover per year for secondary and tertiary hospitalization across all empaneled public and private hospitals.",
        "Aadhaar Card with correct date of birth, Active Mobile Number for OTP verification, Ration Card (optional).",
        "https://beneficiary.nha.gov.in/"
    ),
    (
        "Pradhan Mantri Vaya Vandana Yojana (PMVVY)",
        "senior_citizen",
        "Government-backed pension scheme operated by LIC providing assured monthly returns on retirement lump-sum investments.",
        "Senior citizens aged 60 years and above.",
        "Assured return of 7.4% per annum payable monthly for 10 years on purchase price deposits up to ₹15 Lakhs.",
        "Aadhaar Card, Age Proof (PAN Card / Passport), Bank Account Passbook, Retirement / Superannuation proof.",
        "https://www.licindia.in/"
    ),
    (
        "Indira Gandhi National Old Age Pension Scheme (IGNOAPS)",
        "senior_citizen",
        "Non-contributory monthly cash pension for destitute elderly citizens living below the poverty line.",
        "Citizens aged 60 years and above belonging to a household listed in Below Poverty Line (BPL) records.",
        "Monthly direct cash pension of ₹200–₹500 (plus additional state supplements up to ₹2,000/month depending on state).",
        "BPL Card / SECC Household Data, Aadhaar Card, Age Proof, Bank Account Passbook seeded with Aadhaar.",
        "https://www.myscheme.gov.in/schemes/ignoaps"
    ),
    (
        "Atal Pension Yojana (APY)",
        "senior_citizen",
        "Guaranteed lifelong social security monthly pension scheme for citizens in the unorganized sector.",
        "Indian citizens aged between 18 and 40 years holding a savings bank or post office account.",
        "Guaranteed monthly pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000 from age 60 until death, followed by spouse pension and return of corpus to nominee.",
        "Savings Bank Account Number, Aadhaar Card, Active Mobile Number, Nominee details.",
        "https://www.myscheme.gov.in/schemes/apy"
    ),
    (
        "Senior Citizens Savings Scheme (SCSS)",
        "senior_citizen",
        "Government savings deposit offering safe, quarterly regular interest income with tax benefits.",
        "Individuals aged 60 years and above (or 55 years for early retirees / superannuated personnel).",
        "High guaranteed interest rate of 8.2% per annum paid quarterly on deposits up to ₹30 Lakhs with Section 80C tax deduction.",
        "Age Proof (PAN Card / Passport), Aadhaar Card, Retirement Gratuity proof (if under 60), Bank/Post Office Account Details.",
        "https://www.indiapost.gov.in/"
    ),
    (
        "Rashtriya Vayoshri Yojana (RVY)",
        "senior_citizen",
        "Free distribution of physical assistive living devices for senior citizens suffering from age-related disabilities.",
        "Senior citizens aged 60+ belonging to BPL category or earning monthly income less than ₹15,000.",
        "Free supply of walking sticks, elbow crutches, walkers, hearing aids, wheelchairs, artificial dentures, and spectacles.",
        "Aadhaar Card, Proof of Age (60+), BPL Card / Income Certificate from Tehsildar, Medical disability/impairment certificate.",
        "https://alimco.in/"
    ),
    (
        "Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
        "senior_citizen",
        "Providing quality generic medicines and healthcare items to elderly citizens at 50% to 90% cheaper prices.",
        "All citizens, with special cost-saving benefits for senior citizens managing diabetes, hypertension, and arthritis.",
        "Access to over 1,800 essential generic medicines and 300 surgical products manufactured under strict WHO-GMP standards at affordable rates.",
        "Doctor's Prescription (for prescription drugs), Patient Name, Contact Number.",
        "https://janaushadhi.gov.in/"
    ),
    (
        "National Programme for Health Care of the Elderly (NPHCE)",
        "senior_citizen",
        "Dedicated geriatric healthcare services through specialized senior wings and clinics in government hospitals.",
        "All senior citizens aged 60 years and above across India.",
        "Free dedicated geriatric OPD consultations, specialized senior inpatient wards, physiotherapy, and medicines at district hospitals.",
        "Aadhaar Card / Age Proof, Previous Medical Records.",
        "https://mohfw.gov.in/"
    ),
    (
        "Reverse Mortgage Loan Scheme",
        "senior_citizen",
        "Allows elderly house owners to convert home equity into a regular tax-free monthly stream of income without selling.",
        "Senior citizens aged 60 years and above owning a self-acquired, unencumbered residential property.",
        "Periodic monthly cash payouts from the bank for up to 20 years while the senior citizen retains full ownership and residence rights for life.",
        "Title Deed of Residential Property, Age Proof (PAN/Aadhaar), House Valuation and Municipal Tax Receipts, Permanent Residence Proof.",
        "https://www.nhb.org.in/"
    ),
    (
        "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "senior_citizen",
        "Subsidized accident death and permanent disability insurance cover for senior citizens up to 70 years.",
        "All individuals aged 18 to 70 years having a bank account with auto-debit consent.",
        "₹2 Lakh accidental death / full disability cover (₹1 Lakh for partial disability) for a nominal premium of just ₹20 per year.",
        "Aadhaar Card, Bank Account Passbook, Auto-debit Mandate Form.",
        "https://financialservices.gov.in/"
    ),
    (
        "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "senior_citizen",
        "Subsidized renewable term life insurance protection for citizens up to age 55 (valid policy protection for family).",
        "Bank account holders aged 18 to 50 years (coverage valid up to age 55).",
        "₹2 Lakh life insurance sum assured payable to nominee upon death of subscriber due to any cause for ₹436/year.",
        "Aadhaar Card, Bank Account Details, Nominee Aadhaar Card.",
        "https://financialservices.gov.in/"
    ),
    (
        "Integrated Programme for Senior Citizens (IPSrC)",
        "senior_citizen",
        "Financial grant-in-aid for running old age homes, day care centers, and continuous medical care for destitute elderly.",
        "Senior citizens (60+) who are homeless, indigent, or lacking family support.",
        "Free nutritious food, clean shelter, clothing, medical healthcare, and recreational facilities provided at registered Senior Homes.",
        "Age proof (Aadhaar/Voter ID), Indigence / BPL Certificate (where required).",
        "https://socialjustice.gov.in/"
    ),
    (
        "Annapurna Scheme for Senior Citizens",
        "senior_citizen",
        "Meeting food security needs of indigent senior citizens who are not receiving pension under NOAPS.",
        "Destitute senior citizens aged 65 years and above who are not receiving old age pension benefits.",
        "10 kg of food grains (wheat/rice) provided completely free of charge every month through Fair Price Shops.",
        "Aadhaar Card, Age Certificate, Certificate from revenue officer confirming non-receipt of pension, Ration Card.",
        "https://www.myscheme.gov.in/schemes/ignoaps"
    ),
    (
        "National Pension System (NPS for Senior Investors)",
        "senior_citizen",
        "Voluntary defined-contribution pension system allowing investments up to age 70 with market-linked returns.",
        "Any citizen aged 18 to 70 years seeking systematic post-retirement pension accumulation.",
        "Low fund management fees, tax deductions under 80CCD, flexibility to select asset allocation, and regular annuity payouts.",
        "Aadhaar Card, PAN Card, CKYC Compliance, Bank Account Details.",
        "https://www.myscheme.gov.in/schemes/nps"
    ),
    (
        "Varishtha Nagrik Swasthya Seva & Wellness Centers",
        "senior_citizen",
        "Free primary medical consultations, geriatric screenings, and free diagnostic tests for elderly citizens.",
        "All senior citizens aged 60 and above visiting Ayushman Bharat Health and Wellness Centers (Arogya Mandir).",
        "Free screening for hypertension, diabetes, oral and breast cancers, cataract detection, and free supply of maintenance medicines.",
        "Aadhaar Card or Senior Citizen ID Card.",
        "https://mohfw.gov.in/"
    ),

    # ==================== CATEGORY: UNEMPLOYED / SKILLS / SELF-EMPLOYMENT (15 Schemes) ====================
    (
        "PM Vishwakarma Scheme",
        "unemployed",
        "Flagship scheme supporting traditional artisans and craftspersons with toolkits, stipend, and concessional loans.",
        "Artisans and craftspersons working in 18 notified family-based traditional trades (carpenters, blacksmiths, potters, masons, tailors, etc.) aged 18+.",
        "PM Vishwakarma Certificate & ID Card, ₹15,000 modern toolkit e-voucher, skill training with ₹500/day stipend, and collateral-free enterprise loans up to ₹3 Lakhs at 5% interest.",
        "Aadhaar Card, Mobile Number, Bank Account Passbook, Trade Self-Declaration.",
        "https://pmvishwakarma.gov.in/"
    ),
    (
        "Pradhan Mantri Kaushal Vikas Yojana (PMKVY 4.0)",
        "unemployed",
        "Short-term industry-aligned skill training and certification to enable youth to secure productive employment.",
        "Any Indian youth aged 15–45 years who is unemployed, school/college dropout, or seeking marketable vocational skills.",
        "Free industry-standard skill training across emerging tech, manufacturing, and services, recognized NSQF Certificate, and placement assistance.",
        "Aadhaar Card, Bank Account Details, Educational Marksheet (if any), Passport size photographs.",
        "https://www.skillindiadigital.gov.in/"
    ),
    (
        "PM SVANidhi (PM Street Vendor's AtmaNirbhar Nidhi)",
        "unemployed",
        "Special microcredit facility for street vendors and small hawkers to restart and scale their livelihood businesses.",
        "Urban and peri-urban street vendors vending before March 2020 (or holding Vending Certificate / Letter of Recommendation).",
        "Collateral-free working capital loan of ₹10,000 in 1st tranche, ₹20,000 in 2nd tranche, and ₹50,000 in 3rd tranche, with 7% interest subsidy and digital cashback up to ₹1,200/year.",
        "Certificate of Vending / Vendor Identity Card issued by Urban Local Body (ULB), Aadhaar Card, Bank Passbook.",
        "https://pmsvanidhi.mohua.gov.in/"
    ),
    (
        "Pradhan Mantri Mudra Yojana (PMMY)",
        "unemployed",
        "Providing institutional micro-loans up to ₹10 Lakhs to non-corporate, non-farm small and micro enterprises.",
        "Any Indian citizen having a viable business plan for manufacturing, processing, trading, or service sector activities.",
        "Collateral-free credit under 3 categories: Shishu (loans up to ₹50,000), Kishore (loans ₹50,000 to ₹5 Lakhs), and Tarun (loans ₹5 Lakhs to ₹10 Lakhs).",
        "Business Proposal / Project Details, Identity & Address Proof (Aadhaar/PAN), Proof of Business Address, 6 months bank statement.",
        "https://www.mudra.org.in/"
    ),
    (
        "Prime Minister's Employment Generation Programme (PMEGP)",
        "unemployed",
        "Credit-linked subsidy program to generate continuous self-employment opportunities in rural and urban areas.",
        "Any individual aged 18+ years (minimum 8th class pass for projects above ₹10 Lakhs in manufacturing and ₹5 Lakhs in service).",
        "Government margin money subsidy of 15% to 35% on project costs up to ₹50 Lakhs for manufacturing units and ₹20 Lakhs for service units.",
        "Detailed Project Report (DPR), Aadhaar Card, Caste / Special Category Certificate (if SC/ST/OBC/Women), Educational Qualification Certificate, EDP Training Certificate.",
        "https://www.myscheme.gov.in/schemes/pmegp"
    ),
    (
        "Startup India Initiative",
        "unemployed",
        "Tax benefits, patent fee reductions, seed fund access, and regulatory simplifications for innovative new ventures.",
        "Entities incorporated as private limited company, LLP, or registered partnership within 10 years with turnover below ₹100 Crores.",
        "3-year consecutive income tax holiday under Section 80IAC, 80% rebate on patent filings, fast-track exit, and access to ₹10,000 Crore Fund of Funds.",
        "Certificate of Incorporation / Registration, Pitch Deck / Business Description, PAN Card of Entity, Founder Aadhaar Cards.",
        "https://www.startupindia.gov.in/"
    ),
    (
        "National Apprenticeship Promotion Scheme (NAPS)",
        "unemployed",
        "Promoting formal apprenticeship training in industries to bridge the academia-industry skill gap.",
        "Youth aged 14 years and above possessing minimum educational qualification (5th/8th/10th/12th/ITI/Diploma/Degree).",
        "Government shares 25% of prescribed monthly stipend paid to apprentices up to ₹1,500 per month, directly boosting employability.",
        "Aadhaar Card, Highest Educational / Technical Certificate, Bank Account Details, Apprenticeship Portal Registration Number.",
        "https://www.apprenticeshipindia.gov.in/"
    ),
    (
        "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
        "unemployed",
        "Demand-led placement-linked skill training for rural youth from poor households.",
        "Rural youth aged 15 to 35 years (up to 45 years for women, SC/ST, and persons with disabilities) belonging to poor families.",
        "100% free residential training, uniforms, books, lodging, and boarding, with mandatory minimum 70% job placement assurance at statutory wages.",
        "BPL Ration Card / SECC Data, Aadhaar Card, Age Proof, Educational Marksheets, Bank Passbook.",
        "https://kaushalpanjee.nic.in/"
    ),
    (
        "National Career Service (NCS)",
        "unemployed",
        "Digital portal connecting job seekers with national employers, government recruitments, and career counselors.",
        "Any unemployed youth, graduate, or professional looking for employment or career counseling.",
        "Free online registration, verified job listings across IT, manufacturing, banking, and government sectors, job fairs, and resume building tools.",
        "Aadhaar Card or Government Identity Card, Educational Certificates, Resume / Work Experience Details.",
        "https://www.ncs.gov.in/"
    ),
    (
        "e-Shram Portal (National Database of Unorganized Workers)",
        "unemployed",
        "National database issuing universal identity cards and social security scheme access to informal workers.",
        "Unorganized workers, construction laborers, domestic workers, gig workers, and agricultural workers aged 16 to 59 years.",
        "Universal 12-digit UAN card, direct access to social security welfare schemes, and ₹2 Lakh accidental death / permanent disability insurance cover.",
        "Aadhaar Card, Active Mobile Number linked to Aadhaar, Savings Bank Account Passbook.",
        "https://eshram.gov.in/"
    ),
    (
        "MGNREGA (Mahatma Gandhi NREGA)",
        "unemployed",
        "Legal statutory guarantee of 100 days of wage employment in a financial year for rural adult workers.",
        "Any adult member (18+) of a rural household willing to perform unskilled manual public work.",
        "Statutory guaranteed minimum wage employment within 15 days of applying, with unemployment allowance if work is not provided.",
        "Job Card Application, Aadhaar Card, Proof of Rural Residence, Bank / Post Office Account Details.",
        "https://nrega.nic.in/"
    ),
    (
        "PM Surya Ghar: Muft Bijli Yojana (Green Jobs & Entrepreneurship)",
        "unemployed",
        "Rooftop solar subsidy scheme creating green jobs for local technicians, installers, and small vendors.",
        "Indian households wishing to install rooftop solar, alongside youth seeking training as Surya Mitras and solar vendors.",
        "Up to ₹78,000 direct capital subsidy for 3kW rooftop solar setup, 300 units free monthly electricity, and certified installation employment.",
        "Electricity Consumer Number & Bill, Aadhaar Card, Bank Account Details, Roof Ownership Proof.",
        "https://pmsuryaghar.gov.in/"
    ),
    (
        "Rural Self Employment Training Institutes (RSETI)",
        "unemployed",
        "Free short-term intensive vocational training and enterprise mentorship for rural youth.",
        "Rural youth aged 18 to 45 years hailing from BPL families or under-privileged backgrounds.",
        "Free residential training in 60+ trades (plumbing, motor mechanics, tailoring, food processing, photography) with guaranteed bank loan linkage for enterprise setup.",
        "Aadhaar Card, BPL Certificate / Family Income Proof, School Leaving Marksheet, Passport Photographs.",
        "https://www.myscheme.gov.in/schemes/rseti"
    ),
    (
        "SANKALP Skill Development Programme",
        "unemployed",
        "Strengthening district skill committees and modernizing skill training infrastructure across states.",
        "Youth enrolled in district-level vocational skill programs.",
        "Standardized NSQF certifications, industry internships, micro-enterprise incubation, and career counseling centers.",
        "Aadhaar Card, Enrollment Slip from local ITI / Government Skill Training Center.",
        "https://msde.gov.in/"
    ),
    (
        "PM-YUVA (Yuva Udyamita Vikas Abhiyan)",
        "unemployed",
        "Fostering entrepreneurship education, incubation, and mentorship for youth in colleges and polytechnics.",
        "Students and young adults in higher educational institutes, ITIs, and polytechnics.",
        "Access to business incubation centers, seed funding network connections, startup mentor bootcamps, and legal business advisory.",
        "Student ID Card, Aadhaar Card, Business Concept Pitch Note.",
        "https://msde.gov.in/"
    ),

    # ==================== CATEGORY: DIFFERENTLY ABLED / DIVYANGJAN (15 Schemes) ====================
    (
        "Unique Disability ID (UDID) Card (Swavlamban)",
        "differently_abled",
        "Single universal digital identity card for Divyangjan that eliminates the need to carry physical disability certificates.",
        "Persons with disabilities (PwD) as recognized under the Rights of Persons with Disabilities Act (21 benchmark disabilities).",
        "Pan-India universal recognition for railway/bus travel concessions, pension approvals, medical benefits, and scholarship disbursement.",
        "Aadhaar Card, Medical Disability Certificate from authorized hospital, Passport size photograph, Address Proof.",
        "https://www.swavlambancard.gov.in/"
    ),
    (
        "ADIP Scheme (Purchase / Fitting of Assistive Devices)",
        "differently_abled",
        "Free distribution of modern, sophisticated, durable aids and assistive appliances for persons with disabilities.",
        "Indian citizens with 40% or more disability and monthly family income up to ₹22,500.",
        "Free motorized tricycles, smart canes, wheelchairs, digital hearing aids, braille kits, prosthetics, and cochlear implant surgeries (up to ₹6 Lakhs for children under 5).",
        "Disability Certificate (40%+), Income Certificate / BPL Card, Aadhaar Card, Doctor's Prescription for device.",
        "https://adip.depwd.gov.in/"
    ),
    (
        "Deendayal Disabled Rehabilitation Scheme (DDRS)",
        "differently_abled",
        "Grant-in-aid to voluntary non-governmental organizations providing education and vocational rehabilitation for disabled children.",
        "Persons with intellectual, hearing, visual, locomotor, and multiple disabilities.",
        "Free special schooling, vocational rehabilitation, early intervention therapies, speech therapy, and free hostel accommodation.",
        "Disability Certificate / UDID Card, Medical history, Recommendation from local district social welfare officer.",
        "https://disabilityaffairs.gov.in/"
    ),
    (
        "Accessible India Campaign (Sugamya Bharat Abhiyan)",
        "differently_abled",
        "Nation-wide campaign creating universal barrier-free physical and digital accessibility for persons with disabilities.",
        "All persons with disabilities, elderly citizens, and individuals with temporary reduced mobility.",
        "Ramps, tactile flooring, accessible toilets, audio signage, and lifts in public buildings, airports, railway stations, and government websites.",
        "Citizen feedback / accessibility complaints can be registered directly on the Sugamya Bharat mobile app.",
        "https://disabilityaffairs.gov.in/"
    ),
    (
        "National Scholarship for Students with Disabilities",
        "differently_abled",
        "Pre-matric, post-matric, and top-class higher education scholarships for students with disabilities.",
        "Students with 40% or more disability studying from Class 9 up to Post-Graduation / Ph.D. with family income below ₹2.5 Lakhs.",
        "Full tuition fee reimbursement, maintenance allowance up to ₹4,000/month, book grants, and disability allowances for escorts/readers.",
        "Disability Certificate / UDID, Previous Year Academic Marksheet, Family Income Certificate, College Fee Receipt, Bank Passbook.",
        "https://scholarships.gov.in/"
    ),
    (
        "Ayushman Bharat (PM-JAY) for Persons with Disabilities",
        "differently_abled",
        "Comprehensive free cashless health and surgical care for eligible families having persons with disabilities.",
        "Families with disabled members listed under SECC criteria or eligible under state disability welfare registers.",
        "Cashless medical and surgical cover up to ₹5 Lakhs per family per year covering critical illness, corrective surgeries, and hospitalization.",
        "UDID Card / Disability Certificate, Aadhaar Card, Ration Card / SECC verification slip.",
        "https://beneficiary.nha.gov.in/"
    ),
    (
        "NHFDC Concessional Loans for Divyangjan Entrepreneurs",
        "differently_abled",
        "Low-interest financial assistance to help persons with disabilities start businesses or pursue professional studies.",
        "Any Indian citizen with 40% or more disability aged 18 years and above.",
        "Concessional loans up to ₹50 Lakhs for micro-enterprises and higher education at interest rates between 4% and 8% per annum, with 0.5% rebate for women.",
        "UDID / Disability Certificate, Detailed Business Project Proposal, Identity & Address Proof, Bank Account Details.",
        "https://www.myscheme.gov.in/schemes/nhfdc-eduloan"
    ),
    (
        "Niramaya Health Insurance Scheme",
        "differently_abled",
        "Affordable health insurance cover for persons with Autism, Cerebral Palsy, Intellectual Disability, and Multiple Disabilities.",
        "Individuals with Autism, Cerebral Palsy, Mental Retardation, or Multiple Disabilities without any upper age limit.",
        "Health insurance cover up to ₹1 Lakh per year covering hospitalization, OPD consultations, corrective surgeries, dental treatment, and alternative therapies.",
        "Disability Certificate under National Trust Act / UDID, BPL Card / Income Certificate, Aadhaar Card, Bank Account Details.",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "Gharaunda Group Home Scheme for Adults with Disabilities",
        "differently_abled",
        "Lifelong residential shelter, medical supervision, and group home care for destitute adults with severe disabilities.",
        "Adults with Autism, Cerebral Palsy, Mental Retardation, and Multiple Disabilities aged 18+ whose parents or guardians are deceased or unable to care.",
        "Quality residential accommodation, nutritious food, medical care, therapy, and vocational engagement in supervised group homes.",
        "Disability Certificate under National Trust Act / UDID, Death Certificate of parents/guardians (if applicable), BPL Certificate.",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "Sahyogi Caregiver Training Scheme",
        "differently_abled",
        "Skill training program for family members and primary caregivers to assist persons with severe disabilities.",
        "Family members, parents, and community workers willing to provide professional home-based care for disabled individuals.",
        "Intensive certified training in patient handling, emergency first aid, speech enhancement, mobility assistance, and monthly stipend.",
        "Aadhaar Card, 10th Standard Marksheet, Relationship Proof with disabled individual (if family caregiver).",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "Disha Early Intervention and School Readiness",
        "differently_abled",
        "Therapy, day care, and early childhood intervention for children with developmental delays to enable inclusive schooling.",
        "Children with developmental disabilities aged 0 to 10 years.",
        "Specialized occupational therapy, speech therapy, physiotherapy, and psychological counseling to prepare children for mainstream schools.",
        "Disability / Assessment Certificate, Birth Certificate, Aadhaar Card of child and parents.",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "Vikaas Day Care Scheme",
        "differently_abled",
        "Enhancing interpersonal and vocational abilities of children and adults with intellectual and developmental disabilities.",
        "Individuals with Autism, Cerebral Palsy, or Mental Retardation aged 10 years and above.",
        "Day care facilities offering pre-vocational skill training, speech development, socialization, and recreational therapies.",
        "National Trust Disability Certificate / UDID, Income Proof of parents, Aadhaar Card.",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "Samarth Respite Care Homes",
        "differently_abled",
        "Short-term respite care and accommodation support for families of individuals with severe developmental disabilities.",
        "Persons with Autism, Cerebral Palsy, and Multiple Disabilities needing temporary respite care during family emergencies.",
        "Clean residential accommodation, round-the-clock medical attention, special meals, and recreational activities for short durations.",
        "UDID / Disability Certificate, Emergency request letter from family guardian, KYC Proof.",
        "https://thenationaltrust.gov.in/"
    ),
    (
        "National Fellowship for Persons with Disabilities (NFPwD)",
        "differently_abled",
        "Fellowship financial support for disabled scholars pursuing M.Phil and Ph.D. degrees in Indian universities.",
        "Persons with benchmark disabilities (40%+) who have qualified UGC-NET or CSIR-NET and secured Ph.D. admission.",
        "Monthly fellowship of ₹31,000 for JRF and ₹35,000 for SRF, plus annual contingency grant and escort/reader allowance.",
        "UGC-NET Result Card, Disability Certificate / UDID, Ph.D. Admission / Registration Proof, Bank Details.",
        "https://www.ugc.ac.in/"
    ),
    (
        "Incentives to Employers for Employing Persons with Disabilities",
        "differently_abled",
        "Government reimburses employer EPF and ESI contributions to encourage private sector hiring of persons with disabilities.",
        "Private employers providing regular employment to persons with benchmark disabilities with monthly wages up to ₹25,000.",
        "Government pays the employer's contribution to Employees Provident Fund (EPF) and ESI for the first 3 years of employment.",
        "Employee UDID / Disability Certificate, Appointment Letter, EPF/ESI Registration Number of company, Salary Wage Register.",
        "https://disabilityaffairs.gov.in/"
    )
        ]
        cursor.executemany('''
            INSERT INTO schemes (name, category, description, eligibility, benefits, required_documents, portal_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', seed_schemes)
        conn.commit()
        print(f"Database successfully seeded with 90 sample government schemes (15 per category).")
        
    conn.close()

# --- User Auth Functions ---

def register_user(username, email, password):
    """
    Registers a new user inside the database.
    Hashes the password securely.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username.strip(), email.strip(), hashed_password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already exists
    finally:
        conn.close()
    return success

def validate_user(username, password):
    """
    Validates a user's credentials.
    Returns the user row (id, username) if valid, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, password FROM users WHERE username = ?', (username.strip(),))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return {'id': user['id'], 'username': user['username']}
    return None
def update_user_password(user_id, new_password):
    """
    Updates a user's password securely.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = generate_password_hash(new_password)

    cursor.execute(
        'UPDATE users SET password = ? WHERE id = ?',
        (hashed_password, user_id)
    )

    conn.commit()
    conn.close()
def get_user_by_username(username):
    """
    Checks whether a username exists.
    Returns the user row if found, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, username, email, created_at FROM users WHERE username = ?',
        (username.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    return user
def get_user_by_email(email):
    """
    Finds a user by their registered email address.
    Returns the user row if found, else None.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, username, email FROM users WHERE LOWER(email) = LOWER(?)',
        (email.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    return user
# --- Chat History Functions ---

def save_chat_message(user_id, sender, message):
    """
    Saves a message (from user or bot) to the user's chat history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO chat_history (user_id, sender, message)
        VALUES (?, ?, ?)
    ''', (user_id, sender, message.strip()))
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    """
    Fetches the conversation log of a specific user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sender, message, timestamp 
        FROM chat_history 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_chat_history(user_id):
    """
    Deletes all chat messages for a user.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# --- Recommendation Logic ---

def search_schemes(user_query):
    """
    Searches schemes based on demographic keyword matching.
    """
    query = user_query.lower()
    category = None
    
    # 1. Demographic classification based on text keywords
    if any(word in query for word in ['student', 'college', 'scholarship', 'study', 'education', 'matric', 'post-matric', 'school']):
        category = 'student'
    elif any(word in query for word in ['farmer', 'agriculture', 'crop', 'land', 'kisan', 'cultivation', 'fertilizer', 'subsidy']):
        category = 'farmer'
    elif any(word in query for word in ['women', 'female', 'girl', 'mother', 'maternity', 'pregnancy', 'lactating', 'she']):
        category = 'women'
    elif any(word in query for word in ['senior', 'old', 'pension', 'citizen', 'aged', 'retirement', 'elderly']):
        category = 'senior_citizen'
    elif any(word in query for word in ['unemployed', 'job', 'youth', 'skill', 'training', 'placement', 'enterprise', 'stipend']):
        category = 'unemployed'
    elif any(word in query for word in ['disabled', 'handicap', 'divyang', 'blind', 'deaf', 'disability', 'rehabilitation', 'assistive']):
        category = 'differently_abled'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. Query execution based on classified category, falling back to keyword text matching
    if category:
        cursor.execute('SELECT * FROM schemes WHERE category = ?', (category,))
        results = cursor.fetchall()
    else:
        # Search by matching words inside scheme names or descriptions
        search_words = [w for w in query.split() if len(w) > 3]
        if search_words:
            sql_queries = []
            params = []
            for word in search_words:
                sql_queries.append('(name LIKE ? OR description LIKE ?)')
                params.extend([f'%{word}%', f'%{word}%'])
            sql_statement = f"SELECT * FROM schemes WHERE {' OR '.join(sql_queries)}"
            cursor.execute(sql_statement, params)
            results = cursor.fetchall()
        else:
            results = []
            
    conn.close()
    return [dict(row) for row in results]
def get_all_schemes():
    """
    Retrieves all government schemes from the database.
    Used to build the S-BERT + FAISS semantic search index.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM schemes")
    results = cursor.fetchall()

    conn.close()

    return [dict(row) for row in results]

def get_scheme_by_id(scheme_id):
    """
    Retrieves a single government scheme by its database ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_feedback(name, email, message):
    """
    Saves user feedback submission into SQLite.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    conn.commit()
    conn.close()