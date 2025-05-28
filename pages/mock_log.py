import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
import os
import plotly.express as px
import plotly.graph_objects as go
import hashlib
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import altair as alt
import random
import time
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

# --- Configuration for Comprehensive Exam Prep (Single User: rmj) ---
APP_NAME = "Apex Cogni-Synth: Quantum Prep Nexus (JEE, IAT, NEST Edition - rmj's)"
DB_FILE_MOCK_TESTS = "cognisynth_data_rmj.db" # Specific DB for rmj's data

# Hardcoded user details for 'rmj'
USER_ID_RMJ = 1
NEURAL_SIGNATURE_RMJ = "rmj"

DATE_FORMAT = "%Y-%m-%d"

# Expanded for JEE Mains, JEE Advanced, IAT, and NEST domains
UNIVERSAL_KNOWLEDGE_DOMAINS = [
    # JEE Mains / Advanced Physics
    "Physics: Mechanics (Kinematics, Laws of Motion, Work, Energy, Power, Rotational Motion)",
    "Physics: Thermodynamics & Kinetic Theory",
    "Physics: Electrodynamics (Electrostatics, Current, Magnetism, EMI, AC)",
    "Physics: Optics (Ray Optics, Wave Optics)",
    "Physics: Modern Physics (Dual Nature, Atoms, Nuclei, Semiconductors)",

    # JEE Mains / Advanced Chemistry
    "Chemistry: Physical Chemistry (Stoichiometry, States of Matter, Thermodynamics, Equilibrium, Electrochemistry, Kinetics)",
    "Chemistry: Inorganic Chemistry (Periodic Table, Bonding, S/P/D/F-Block, Coordination Compounds, Metallurgy)",
    "Chemistry: Organic Chemistry (Basic Principles, Hydrocarbons, Oxygen/Nitrogen/Halogen Compounds, Biomolecules, Polymers)",

    # JEE Mains / Advanced Mathematics
    "Mathematics: Algebra (Complex Numbers, Quadratic Eq, Seq & Series, Perm & Comb, Binomial, Matrices, Determinants)",
    "Mathematics: Calculus (Functions, Limits, Continuity, Differentiability, AOD, Integrals, Diff Eq, Area)",
    "Mathematics: Coordinate Geometry (Straight Lines, Circles, Conics)",
    "Mathematics: Vectors & 3D Geometry",
    "Mathematics: Probability & Statistics",

    # IAT / NEST Biology (for those appearing for IAT/NEST that includes Biology)
    "Biology: Zoology (Human Physiology, Genetics, Evolution, Ecology)",
    "Biology: Botany (Plant Physiology, Reproduction, Taxonomy, Cell Biology)",

    # General Aptitude / Interdisciplinary for IAT / NEST / Overall Prep
    "General Aptitude & Logical Reasoning (IAT/NEST Specific)",
    "Environmental Science & General Knowledge (NEST Specific)",
    "Interdisciplinary Synthesis & Problem-Solving",
    "Exam Strategy & Time Management",

    # Specific Mock Test Categories (Optional, for logging full mocks)
    "Mock Test: JEE Mains (Full Syllabus)",
    "Mock Test: JEE Advanced (Paper 1)",
    "Mock Test: JEE Advanced (Paper 2)",
    "Mock Test: IAT (Full Syllabus)",
    "Mock Test: NEST (Full Syllabus)",
    "Mock Test: Subject-Specific (Specify in Feedback)" # For custom mocks not fitting above
]

# --- Define Exam Max Marks ---
EXAM_MAX_MARKS = {
    "JEE Mains": 300,
    "JEE Advanced": 360, # Assuming combined score for both papers
    "IAT": 240,
    "NEST": 240,
    "Other": 100 # Default for custom entries or minor quizzes
}

# --- Streamlit Page Configuration (MUST BE THE VERY FIRST STREAMLIT COMMAND) ---
st.set_page_config(
    layout="wide",
    page_title=APP_NAME,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://quantum-support.apex.systems/cognisynth_jee_iat_nest', # Future help docs
        'Report a bug': "https://error-log.apex.systems/cognisynth_jee_iat_nest", # Future bug report
        'About': f"#{APP_NAME}\nCognitive Synthesis Engine for JEE/IAT/NEST 2125."
    }
)

# --- Custom CSS for a Futuristic, Dark, and Neon Aesthetic (ONLY DARK MODE) ---
# This CSS is consistent with the main dashboard for a unified look
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

    /* Ensure html and body take full height and prevent scrollbars */
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        overflow-x: hidden; /* Prevent horizontal scrollbar */
    }

    /* CSS Variables for a consistent Neon Dark Theme */
    :root {
        --neon-blue: #00F0FF;          /* Primary neon highlight */
        --neon-purple: #9D00FF;        /* Secondary neon highlight */
        --neon-green: #39FF14;         /* Tertiary neon for success/alerts */
        --neon-orange: #FF9900;        /* Warning/pending status neon */
        --neon-yellow: #FFD700;        /* Accent glow */

        --dark-bg-deep: #05050A;       /* Very dark background for the page */
        --dark-bg-gradient-start: #1A0033; /* Dark purple for gradient */
        --dark-bg-gradient-end: #000A1A;   /* Dark blue for gradient */
        --card-bg: #1B1B25;            /* Background for cards and components */
        --sidebar-bg: #101015;         /* Slightly different dark for sidebar */

        --text-primary: #E0E0FF;       /* Light, slightly blue-ish text */
        --text-secondary: #A0A0B0;     /* Greyish text for descriptions */
        --border-color: #303040;       /* Subtle dark border */
        --divider-color: #202028;      /* Even darker for dividers */
    }

    /* Apply dark background to the entire page */
    body {
        background: linear-gradient(135deg, var(--dark-bg-gradient-start), var(--dark-bg-deep), var(--dark-bg-gradient-end));
        background-attachment: fixed; /* Ensures gradient covers full background without scrolling */
        color: var(--text-primary);
        font-family: 'Share Tech Mono', monospace; /* Monospaced for futuristic feel */
        line-height: 1.6;
    }

    /* Ensure Streamlit app container is transparent to show body background */
    .stApp {
        background-color: transparent;
    }

    /* Headers with Orbitron font and neon glow */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Orbitron', sans-serif;
        color: var(--neon-blue);
        text-shadow: 0 0 8px var(--neon-blue), 0 0 15px rgba(0, 240, 255, 0.4); /* Stronger neon glow */
        margin-top: 1.5em;
        margin-bottom: 0.8em;
        letter-spacing: 0.05em; /* Add slight spacing */
    }
    h1 { font-size: 2.8em; }
    h2 { font-size: 2.2em; }
    h3 { font-size: 1.8em; }

    /* Streamlit components styling */
    .stSidebar {
        background-color: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
        padding-top: 2rem;
        box-shadow: 2px 0 15px rgba(0, 240, 255, 0.3); /* Stronger glow */
    }

    .stButton>button {
        background-color: var(--neon-blue);
        color: var(--dark-bg-deep); /* Dark text on bright button */
        border-radius: 8px;
        padding: 0.8em 1.5em; /* Larger padding */
        font-size: 1.05em;
        font-weight: 700;
        transition: all 0.3s ease-in-out;
        border: none;
        box-shadow: 0 0 10px var(--neon-blue), 0 0 20px rgba(0, 240, 255, 0.6); /* Pronounced glow */
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button:hover {
        background-color: var(--neon-purple); /* Change color on hover */
        box-shadow: 0 0 15px var(--neon-purple), 0 0 25px rgba(157, 0, 255, 0.7); /* Change glow color */
        transform: translateY(-4px) scale(1.03); /* More pronounced lift and scale */
    }
    .stButton>button[kind="secondary"] {
        background-color: var(--card-bg);
        color: var(--neon-blue);
        border: 1px solid var(--neon-blue);
        box-shadow: 0 0 7px rgba(0, 240, 255, 0.2);
    }
    .stButton>button[kind="secondary"]:hover {
        background-color: var(--neon-blue);
        color: var(--dark-bg-deep);
        transform: none; /* No lift for secondary hover */
        box-shadow: 0 0 10px var(--neon-blue), 0 0 20px rgba(0, 240, 255, 0.6);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 15px; /* Increased gap */
        justify-content: center;
        border-bottom: 2px solid var(--divider-color); /* Subtle divider */
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px; /* Taller tabs */
        background-color: var(--card-bg);
        border-radius: 10px 10px 0 0;
        padding: 15px 30px;
        transition: all 0.3s ease-in-out;
        font-weight: 700;
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
        border-bottom: none;
        text-transform: uppercase;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 -3px 10px rgba(0, 240, 255, 0.1); /* Subtle top glow */
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2A2A3A;
        color: var(--neon-blue);
        box-shadow: 0 -3px 12px var(--neon-blue), 0 -3px 25px rgba(0, 240, 255, 0.5);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--neon-blue);
        color: var(--dark-bg-deep);
        border-bottom: 5px solid var(--neon-blue);
        border-top: 2px solid var(--neon-blue);
        box-shadow: 0 0 20px var(--neon-blue), 0 0 35px rgba(0, 240, 255, 0.8);
        transform: translateY(-3px); /* More pronounced lift */
    }

    .stMetric {
        background-color: var(--card-bg);
        padding: 2rem; /* More padding */
        border-radius: 18px; /* More rounded */
        border: 1px solid var(--border-color);
        box-shadow: 0 0 12px rgba(157, 0, 255, 0.2); /* Purple glow for metrics */
        margin-bottom: 2rem;
        transition: transform 0.4s ease-in-out, box-shadow 0.4s ease-in-out;
        text-align: center;
    }
    .stMetric:hover {
        transform: translateY(-10px); /* Greater lift */
        box-shadow: 0 0 20px var(--neon-purple), 0 0 30px rgba(157, 0, 255, 0.6);
    }
    .stMetric>div>div:first-child { /* Metric label */
        color: var(--text-secondary);
        font-size: 1.15em;
        font-family: 'Share Tech Mono', monospace;
        margin-bottom: 0.5em;
    }
    .stMetric>div>div:nth-child(2) { /* Metric value */
        color: var(--neon-yellow); /* Gold/Yellow for main value */
        font-size: 3em; /* Much larger value */
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 8px var(--neon-yellow), 0 0 15px rgba(255, 215, 0, 0.6);
        line-height: 1; /* Adjust line height */
    }
    .stMetric>div>div:last-child { /* Metric delta */
        color: var(--neon-green); /* Green for positive deltas */
        font-size: 1em;
        font-weight: bold;
    }


    .stAlert {
        border-radius: 12px;
        font-size: 1em;
        margin-bottom: 1.8rem;
        background-color: var(--card-bg);
        border: 1px solid;
        color: var(--text-primary);
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.15);
        padding: 1rem 1.5rem;
    }
    .stAlert.st-emotion-cache-1f81n9p { /* Streamlit success alert */
        background-color: #0A251E; /* Dark emerald */
        color: var(--neon-green);
        border-color: var(--neon-green);
        box-shadow: 0 0 12px rgba(57, 255, 20, 0.4);
    }
    .stAlert.st-emotion-cache-1f81n9p p { color: var(--neon-green); } /* Text within success alert */

    .stAlert.st-emotion-cache-1j0080z { /* Streamlit error alert */
        background-color: #330000; /* Dark red */
        color: #FF4B4B;
        border-color: #FF4B4B;
        box-shadow: 0 0 12px rgba(255, 75, 75, 0.4);
    }
    .stAlert.st-emotion-cache-1j0080z p { color: #FF4B4B; } /* Text within error alert */

    .stAlert.st-emotion-cache-1e74g6b { /* Streamlit warning alert */
        background-color: #332000; /* Dark orange */
        color: var(--neon-orange);
        border-color: var(--neon-orange);
        box-shadow: 0 0 12px rgba(255, 153, 0, 0.4);
    }
    .stAlert.st-emotion-cache-1e74g6b p { color: var(--neon-orange); } /* Text within warning alert */

    /* Input widgets styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div>div, .stTextArea>div>div, .stNumberInput>div>div>input {
        background-color: #2A2A3A; /* Darker input background */
        border: 1px solid var(--border-color);
        border-radius: 8px;
        color: var(--text-primary);
        padding: 0.7em 1em;
        font-size: 0.95em;
        box-shadow: inset 0 0 5px rgba(0, 240, 255, 0.1); /* Inner glow */
        transition: all 0.2s ease;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div>div:focus, .stTextArea>div>div:focus-within, .stNumberInput>div>div>input:focus {
        border-color: var(--neon-blue);
        box-shadow: inset 0 0 8px var(--neon-blue), 0 0 5px var(--neon-blue); /* Stronger focus glow */
        outline: none;
    }

    /* Slider styling */
    .stSlider>div>div>div:nth-child(1) { /* Track background */
        background: var(--border-color);
    }
    .stSlider>div>div>div:nth-child(2) { /* Filled track */
        background: var(--neon-blue);
    }
    .stSlider [data-testid="stThumbValue"] { /* Value label above thumb */
        background-color: var(--neon-blue);
        color: var(--dark-bg-deep);
        border-radius: 5px;
        padding: 2px 8px;
        font-weight: bold;
    }

    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid var(--border-color);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.1);
    }

    .stDataFrame .ag-header-cell-label {
        color: var(--neon-blue); /* Header text color */
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9em;
        text-transform: uppercase;
    }
    .stDataFrame .ag-theme-streamlit {
        --ag-background-color: var(--card-bg);
        --ag-odd-row-background-color: #20202A; /* Slightly lighter for odd rows */
        --ag-row-hover-background-color: #303040;
        --ag-border-color: var(--divider-color);
        --ag-data-color: var(--text-primary);
        --ag-font-family: 'Share Tech Mono', monospace;
        --ag-selected-row-background-color: #003344; /* Darker blue when selected */
    }

    /* Information boxes */
    .stAlert.st-emotion-cache-12fmw13 { /* Streamlit info alert */
        background-color: #101525;
        color: var(--neon-blue);
        border-color: var(--neon-blue);
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
    }
    .stAlert.st-emotion-cache-12fmw13 p { color: var(--neon-blue); }

    /* Markdown elements */
    p {
        color: var(--text-primary);
    }
    a {
        color: var(--neon-blue);
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }

    /* Centering content within columns */
    .st-emotion-cache-ocqkz7 {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }
    .st-emotion-cache-ocqkz7 .stMetric {
        width: 100%; /* Ensure metric takes full width of its column */
    }

    /* General containers/blocks */
    .st-emotion-cache-h5rg5t, .st-emotion-cache-10qadwd, .st-emotion-cache-1p1fspc { /* These are common Streamlit containers */
        background-color: var(--card-bg);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid var(--border-color);
        box-shadow: 0 0 15px rgba(157, 0, 255, 0.15); /* Soft purple glow for general cards */
        margin-bottom: 2rem;
    }

    /* Specific adjustments for plotly charts to match theme */
    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Utility Functions ---

# Function to generate a stable, unique ID for entries
def generate_unique_id(user_id, assessment_date, domain, score):
    """Generates a consistent SHA256 hash based on input parameters."""
    unique_string = f"{user_id}-{assessment_date}-{domain}-{score}-{random.random()}" # Add random to prevent collisions for same inputs
    return hashlib.sha256(unique_string.encode()).hexdigest()

# Context manager for database connection
@st.cache_resource(ttl=3600) # Cache connection for 1 hour
def get_db_connection_mock_tests():
    """Establishes and returns a SQLite database connection for mock tests."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE_MOCK_TESTS, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        app_logger.info(f"Successfully connected to database: {DB_FILE_MOCK_TESTS}")
        return conn
    except sqlite3.Error as e:
        app_logger.error(f"Database connection error for {DB_FILE_MOCK_TESTS}: {e}")
        st.error(f"🚨 Database connection error for Mock Tests: {e}")
        return None

def create_mock_test_table(conn):
    """Creates the mock_test_results table if it doesn't already exist."""
    if conn is None:
        return False
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mock_test_results (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                assessment_date TEXT,
                exam_type TEXT, -- Added exam_type column
                test_name TEXT, -- Added test_name column
                domain TEXT,
                total_questions INTEGER, -- Added total_questions
                attempted INTEGER, -- Added attempted
                correct INTEGER, -- Added correct
                wrong INTEGER, -- Added wrong
                physics_score REAL, -- Added physics_score
                chemistry_score REAL, -- Added chemistry_score
                maths_score REAL, -- Added maths_score
                biology_score REAL, -- Added biology_score
                total_score INTEGER,
                max_score_possible INTEGER, 
                percentile REAL, -- Added percentile
                rank INTEGER, -- Added rank
                target_score REAL, -- Added target_score
                difficulty TEXT,
                time_taken_minutes INTEGER,
                feedback TEXT,
                neural_signature TEXT,
                timestamp TEXT -- Added timestamp
            )
        """)
        conn.commit()
        app_logger.info("Mock test results table ensured.")
        return True
    except sqlite3.Error as e:
        app_logger.error(f"Error creating mock test results table: {e}")
        st.error(f"🚨 Error creating mock test results table: {e}")
        return False

def add_mock_test_result(conn, user_id, assessment_date, exam_type, test_name, domain,
                         total_questions, attempted, correct, wrong,
                         physics_score, chemistry_score, maths_score, biology_score,
                         total_score, max_score_possible, percentile, rank, target_score,
                         difficulty, time_taken_minutes, feedback, neural_signature, timestamp):
    """Adds a new mock test result to the database."""
    if conn is None:
        st.error("Database connection not established. Cannot add data.")
        return False
    try:
        test_id = generate_unique_id(user_id, assessment_date, domain, total_score)
        conn.execute("""
            INSERT INTO mock_test_results (
                id, user_id, assessment_date, exam_type, test_name, domain,
                total_questions, attempted, correct, wrong,
                physics_score, chemistry_score, maths_score, biology_score,
                total_score, max_score_possible, percentile, rank, target_score,
                difficulty, time_taken_minutes, feedback, neural_signature, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (test_id, user_id, assessment_date, exam_type, test_name, domain,
              total_questions, attempted, correct, wrong,
              physics_score, chemistry_score, maths_score, biology_score,
              total_score, max_score_possible, percentile, rank, target_score,
              difficulty, time_taken_minutes, feedback, neural_signature, timestamp))
        conn.commit()
        app_logger.info(f"Added mock test result: {test_name} ({exam_type}) on {assessment_date} with score {total_score}/{max_score_possible}")
        return True
    except sqlite3.Error as e:
        app_logger.error(f"Error adding mock test result: {e}")
        st.error(f"🚨 Error adding mock test result: {e}")
        return False

def load_mock_test_results(conn, user_id=None):
    """Loads mock test results from the database, optionally filtered by user_id."""
    if conn is None:
        return pd.DataFrame()
    try:
        if user_id:
            df = pd.read_sql_query("SELECT * FROM mock_test_results WHERE user_id = ? ORDER BY assessment_date DESC", conn, params=(user_id,))
        else:
            df = pd.read_sql_query("SELECT * FROM mock_test_results ORDER BY assessment_date DESC", conn)
        
        if not df.empty:
            df['assessment_date'] = pd.to_datetime(df['assessment_date']).dt.date
            df['timestamp'] = pd.to_datetime(df['timestamp']) # Ensure timestamp is datetime
            
            # Ensure numeric types and handle potential NaNs
            df['total_score'] = pd.to_numeric(df['total_score'], errors='coerce').fillna(0)
            df['max_score_possible'] = pd.to_numeric(df['max_score_possible'], errors='coerce').fillna(100) # Default to 100
            df['time_taken_minutes'] = pd.to_numeric(df['time_taken_minutes'], errors='coerce').fillna(0)
            df['total_questions'] = pd.to_numeric(df['total_questions'], errors='coerce').fillna(0).astype(int)
            df['attempted'] = pd.to_numeric(df['attempted'], errors='coerce').fillna(0).astype(int)
            df['correct'] = pd.to_numeric(df['correct'], errors='coerce').fillna(0).astype(int)
            df['wrong'] = pd.to_numeric(df['wrong'], errors='coerce').fillna(0).astype(int)
            df['physics_score'] = pd.to_numeric(df['physics_score'], errors='coerce').fillna(0.0)
            df['chemistry_score'] = pd.to_numeric(df['chemistry_score'], errors='coerce').fillna(0.0)
            df['maths_score'] = pd.to_numeric(df['maths_score'], errors='coerce').fillna(0.0)
            df['biology_score'] = pd.to_numeric(df['biology_score'], errors='coerce').fillna(0.0)
            df['percentile'] = pd.to_numeric(df['percentile'], errors='coerce').fillna(0.0)
            df['rank'] = pd.to_numeric(df['rank'], errors='coerce').fillna(0).astype(int)
            df['target_score'] = pd.to_numeric(df['target_score'], errors='coerce').fillna(0.0)

            # Calculate percentage_score for consistent analysis and display
            # Handle division by zero for max_score_possible
            df['percentage_score'] = (df['total_score'] / df['max_score_possible'] * 100).round(2)
            df.loc[df['max_score_possible'] == 0, 'percentage_score'] = 0.0 # Set to 0 if max_score_possible is 0

            # Calculate accuracy based on correct/attempted for question analysis
            df['accuracy_q'] = (df['correct'] / df['attempted'] * 100).round(2)
            df.loc[df['attempted'] == 0, 'accuracy_q'] = 0.0 # Set to 0 if attempted is 0

            # Calculate unattempted questions
            df['unattempted'] = df['total_questions'] - df['attempted']

        app_logger.info(f"Loaded {len(df)} mock test results for user {user_id if user_id else 'all'}.")
        return df
    except Exception as e:
        app_logger.error(f"Error loading mock test results: {e}", exc_info=True)
        st.error(f"🚨 Error loading mock test results: {e}")
        return pd.DataFrame()

def delete_mock_test_result(conn, test_id):
    """Deletes a mock test result by its ID."""
    if conn is None:
        st.error("Database connection not established. Cannot delete data.")
        return False
    try:
        conn.execute("DELETE FROM mock_test_results WHERE id = ?", (test_id,))
        conn.commit()
        app_logger.info(f"Deleted mock test result with ID: {test_id}")
        return True
    except sqlite3.Error as e:
        app_logger.error(f"Error deleting mock test result: {e}")
        st.error(f"🚨 Error deleting mock test result: {e}")
        return False

def update_mock_test_result(conn, test_id, column, value):
    """Updates a single column for a given mock test result ID."""
    if conn is None:
        st.error("Database connection not established. Cannot update data.")
        return False
    try:
        # Basic validation for column name to prevent SQL injection for column names
        allowed_columns = [
            'assessment_date', 'exam_type', 'test_name', 'domain',
            'total_questions', 'attempted', 'correct', 'wrong',
            'physics_score', 'chemistry_score', 'maths_score', 'biology_score',
            'total_score', 'max_score_possible', 'percentile', 'rank', 'target_score',
            'difficulty', 'time_taken_minutes', 'feedback', 'neural_signature'
        ]
        if column not in allowed_columns:
            st.error(f"Invalid column for update: {column}")
            return False

        # Convert date objects to string for DB storage
        if column == 'assessment_date' and isinstance(value, date):
            value = value.strftime(DATE_FORMAT)

        conn.execute(f"UPDATE mock_test_results SET {column} = ? WHERE id = ?", (value, test_id))
        conn.commit()
        app_logger.info(f"Updated mock test ID {test_id}: set {column} to {value}")
        return True
    except sqlite3.Error as e:
        app_logger.error(f"Error updating mock test result (ID: {test_id}, Column: {column}, Value: {value}): {e}")
        st.error(f"🚨 Error updating mock test result: {e}")
        return False

# --- AI Nexus Co-Pilot Logic (Simplified Mock) ---
def ai_nexus_response(user_query: str, user_df: pd.DataFrame, profile_directives: dict) -> str:
    """Generates a mock AI response based on query and user data."""
    app_logger.info(f"AI Nexus received query: '{user_query}' with {len(user_df)} data points.")
    
    if "performance summary" in user_query.lower():
        if user_df.empty:
            return "Neural pathways indicate no assessment data. Initiate a mock test for analysis."
        
        # Use percentage_score for average calculations
        avg_percentage_score = user_df['percentage_score'].mean()
        avg_time = user_df['time_taken_minutes'].mean()
        num_tests = len(user_df)
        
        summary = f"Synthesizing performance overview for {profile_directives.get('user_name', 'your profile')}:\n"
        summary += f"- Total Assessments: {num_tests}\n"
        summary += f"- Average Percentage Score: {avg_percentage_score:.2f} %\n"
        summary += f"- Average Time Taken: {avg_time:.2f} minutes per assessment\n"
        
        # Identify weak and strong domains based on percentage score
        domain_performance = user_df.groupby('domain')['percentage_score'].mean().sort_values()
        if not domain_performance.empty:
            weakest_domain = domain_performance.index[0]
            strongest_domain = domain_performance.index[-1]
            
            summary += f"- Apparent Core Competency: **{strongest_domain}** (Avg Score: {domain_performance.iloc[-1]:.2f}%)\n"
            summary += f"- Identified Area for Neural Optimization: **{weakest_domain}** (Avg Score: {domain_performance.iloc[0]:.2f}%)\n"
            
            # Add a motivational or action-oriented suggestion
            suggestions = [
                "Recommendation: Allocate additional cognitive processing units to {weakest_domain} simulations.",
                "Action Protocol: Engage targeted drills in {weakest_domain} for neural recalibration.",
                "Directive: Review foundational theorems within {weakest_domain} to optimize comprehension."
            ]
            summary += random.choice(suggestions).format(weakest_domain=weakest_domain)
        else:
            summary += "- Domain-specific analysis requires more varied data.\n"
        
        return summary
    
    elif "predict score" in user_query.lower():
        if len(user_df) < 5: # Need enough data for a meaningful prediction
            return "Insufficient data for robust predictive modeling. Log at least 5 assessments for enhanced foresight."
        
        try:
            df_for_pred = user_df.copy()
            df_for_pred['difficulty_encoded'] = df_for_pred['difficulty'].map({'Easy': 1, 'Medium': 2, 'Hard': 3, 'Very Hard': 4})
            
            # Filter out any rows with NaN in critical columns after encoding or with missing percentage_score
            X = df_for_pred[['time_taken_minutes', 'difficulty_encoded']].dropna()
            y = df_for_pred.loc[X.index, 'percentage_score'].dropna() # Predict percentage score
            
            # Ensure X and y align after dropping NaNs
            common_indices = X.index.intersection(y.index)
            X = X.loc[common_indices]
            y = y.loc[common_indices]

            if X.empty or len(X) < 2:
                return "Not enough valid numerical data points for prediction."
                
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(X[['time_taken_minutes', 'difficulty_encoded']], y)
            
            # Predict for average case or next expected test
            last_test_time = df_for_pred['time_taken_minutes'].iloc[0] # Assuming latest
            last_test_difficulty_encoded = df_for_pred['difficulty_encoded'].iloc[0]
            
            future_scenarios = pd.DataFrame({
                'time_taken_minutes': [last_test_time * 0.9, last_test_time, last_test_time * 1.1],
                'difficulty_encoded': [min(4, last_test_difficulty_encoded + 1), last_test_difficulty_encoded, max(1, last_test_difficulty_encoded - 1)]
            })
            
            predictions = model.predict(future_scenarios).round(2)
            
            prediction_summary = (
                f"Predictive analysis for {profile_directives.get('user_name', 'your profile')}:\n"
                f"- If you optimize time (e.g., {future_scenarios['time_taken_minutes'].iloc[0]:.0f} min) and tackle harder modules, expected percentage score: {predictions[0]:.2f}%\n"
                f"- Based on recent trends, expected percentage score on similar assessment: {predictions[1]:.2f}%\n"
                f"- With extended cognitive processing (e.g., {future_scenarios['time_taken_minutes'].iloc[2]:.0f} min) on easier modules, expected percentage score: {predictions[2]:.2f}%\n"
                "\n*Warning: Predictive models are probabilistic. Actual outcomes may vary based on neural state fluctuations.*"
            )
            return prediction_summary
        except Exception as e:
            app_logger.error(f"Error during predictive modeling: {e}", exc_info=True)
            return "System anomaly detected during predictive processing. Insufficient data or model calibration required."
            
    elif "motivate me" in user_query.lower() or "inspire me" in user_query.lower():
        motivations = [
            "Neural pathways are forging new connections. Every challenge is a data point for growth.",
            "Your cognitive processor is a marvel. Engage, adapt, overcome.",
            "The quantum realm of knowledge awaits. Your potential is boundless. Transmit your energy!",
            "Errors are simply opportunities for debugging. Recalibrate and advance.",
            "The future of your success is coded in your consistent effort."
        ]
        return random.choice(motivations)
        
    elif "neural signature" in user_query.lower():
        return f"Your current active neural signature is: `{profile_directives.get('neural_signature', 'UNKNOWN')}`."
    
    else:
        return "Query not recognized. Please formulate a more precise neural command, e.g., 'performance summary', 'predict score', 'motivate me', or 'neural signature'."

# --- Streamlit App Layout and Logic ---

def cognisynth_app():
    conn = get_db_connection_mock_tests()
    if conn:
        create_mock_test_table(conn)
    
    # Initialize session state variables
    if 'ai_nexus_chat_history' not in st.session_state:
        st.session_state.ai_nexus_chat_history = []
    if 'mock_test_df' not in st.session_state:
        st.session_state.mock_test_df = load_mock_test_results(conn, USER_ID_RMJ)
    if 'selected_exam_type' not in st.session_state:
        st.session_state.selected_exam_type = "Other"

    st.markdown('<h1 class="main-header">📚 JEE Mock Test Logger</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: var(--text-secondary);">Track your preparation for JEE Advanced, JEE Mains, IAT & NEST</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Tabs
    tab_log, tab_manage, tab_analyze, tab_ai_nexus = st.tabs([
        "📝 Log New Assessment", "📊 Manage Data Matrix", "📈 Performance Analytics", "🧠 AI Nexus Co-Pilot"
    ])

    with tab_log:
        st.subheader("Log New Assessment Data Point")
        with st.form("mock_test_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                assessment_date = st.date_input("Assessment Date", value=date.today())
                exam_type = st.selectbox("Exam Type", options=list(EXAM_MAX_MARKS.keys()), key="exam_type_log_form")
                test_name = st.text_input("Test Name", placeholder="e.g., Mock Test 1, Full Syllabus Test")
                domain = st.selectbox("Knowledge Domain", options=UNIVERSAL_KNOWLEDGE_DOMAINS)
                difficulty = st.radio("Difficulty Level", options=["Easy", "Medium", "Hard", "Very Hard"], index=1)
                time_taken_minutes = st.number_input("Time Taken (minutes)", min_value=1, value=180)
                
            with col2:
                # Dynamic input for Max Score
                max_score_possible = st.number_input(
                    f"Maximum Score for {exam_type}",
                    min_value=1,
                    value=EXAM_MAX_MARKS.get(exam_type, 100), # Default to exam type's max, else 100
                    step=1,
                    key="max_score_input"
                )
                
                # Dynamic input for Total Score
                total_score = st.number_input(
                    f"Your Score (out of {max_score_possible})",
                    min_value=0,
                    max_value=max_score_possible, # Max value is dynamic based on max_score_possible
                    value=min(int(max_score_possible * 0.75), max_score_possible), # Default to 75% of max
                    step=1,
                    key="total_score_input"
                )

                # Question-based inputs (optional, can be left at 0 if not applicable)
                total_questions = st.number_input("Total Questions", min_value=0, value=0)
                attempted = st.number_input("Questions Attempted", min_value=0, max_value=total_questions, value=0)
                correct = st.number_input("Correct Answers", min_value=0, max_value=attempted, value=0)
                wrong = st.number_input("Wrong Answers", min_value=0, max_value=attempted, value=0)

            st.markdown("---")
            st.subheader("Subject-wise Scores (Optional)")
            col_sub1, col_sub2, col_sub3, col_sub4 = st.columns(4)
            with col_sub1:
                physics_score = st.number_input("Physics Score", value=0.0)
            with col_sub2:
                chemistry_score = st.number_input("Chemistry Score", value=0.0)
            with col_sub3:
                maths_score = st.number_input("Mathematics Score", value=0.0)
            with col_sub4:
                biology_score = st.number_input("Biology Score (if applicable)", value=0.0)


            st.markdown("---")
            col_perf1, col_perf2 = st.columns(2)
            with col_perf1:
                percentile = st.number_input("Percentile", min_value=0.0, max_value=100.0, value=0.0)
                rank = st.number_input("Rank", min_value=1, value=1)
            with col_perf2:
                target_score = st.number_input("Target Score", value=0.0)
                feedback = st.text_area("Self-Reflective Feedback / Notes")


            submit_button = st.form_submit_button("Record Assessment Data Point")

            if submit_button:
                if not test_name:
                    st.error("Please enter a Test Name.")
                elif total_score > max_score_possible:
                    st.error("Score cannot be greater than Maximum Score Possible.")
                else:
                    if add_mock_test_result(
                        conn, USER_ID_RMJ, assessment_date.strftime(DATE_FORMAT), exam_type, test_name, domain,
                        total_questions, attempted, correct, wrong,
                        physics_score, chemistry_score, maths_score, biology_score,
                        total_score, max_score_possible, percentile, rank, target_score,
                        difficulty, time_taken_minutes, feedback, NEURAL_SIGNATURE_RMJ, datetime.now().isoformat()
                    ):
                        st.success("✅ Assessment data point recorded successfully!")
                        st.session_state.mock_test_df = load_mock_test_results(conn, USER_ID_RMJ) # Refresh DataFrame
                        st.toast("New data point integrated into cognitive matrix.", icon="✅")
                        st.rerun() # Rerun to clear form and refresh data
                    else:
                        st.error("❌ Failed to record assessment data point.")

    with tab_manage:
        st.subheader("Manage Historical Data Matrix")
        st.info("Edit or delete existing assessment data points below. Raw scores are shown, percentage calculated.")

        if st.session_state.mock_test_df.empty:
            st.info("No historical assessment data to manage. Log new data first.")
        else:
            # Display DataFrame for editing
            # Exclude 'percentage_score' and 'accuracy_q', 'unattempted' from direct editing, as they're calculated fields
            df_display_for_edit = st.session_state.mock_test_df.drop(
                columns=['percentage_score', 'accuracy_q', 'unattempted'], errors='ignore'
            )

            edited_df = st.data_editor(
                df_display_for_edit,
                key="mock_test_data_editor_2125",
                num_rows="dynamic",
                column_config={
                    "id": st.column_config.Column("ID", disabled=True),
                    "user_id": st.column_config.Column("User ID", disabled=True),
                    "neural_signature": st.column_config.Column("Neural Signature", disabled=True),
                    "timestamp": st.column_config.DatetimeColumn("Timestamp", disabled=True, format="YYYY-MM-DD HH:mm:ss"),
                    "assessment_date": st.column_config.DateColumn("Assessment Date", format="YYYY-MM-DD"),
                    "exam_type": st.column_config.SelectboxColumn("Exam Type", options=list(EXAM_MAX_MARKS.keys()), required=True),
                    "test_name": st.column_config.TextColumn("Test Name", required=True),
                    "domain": st.column_config.SelectboxColumn("Knowledge Domain", options=UNIVERSAL_KNOWLEDGE_DOMAINS),
                    "total_score": st.column_config.NumberColumn("Your Score", min_value=0, format="%d"),
                    "max_score_possible": st.column_config.NumberColumn("Max Score", min_value=1, format="%d"),
                    "total_questions": st.column_config.NumberColumn("Total Qs", min_value=0, format="%d"),
                    "attempted": st.column_config.NumberColumn("Attempted Qs", min_value=0, format="%d"),
                    "correct": st.column_config.NumberColumn("Correct Qs", min_value=0, format="%d"),
                    "wrong": st.column_config.NumberColumn("Wrong Qs", min_value=0, format="%d"),
                    "physics_score": st.column_config.NumberColumn("Phy Score", format="%.1f"),
                    "chemistry_score": st.column_config.NumberColumn("Chem Score", format="%.1f"),
                    "maths_score": st.column_config.NumberColumn("Math Score", format="%.1f"),
                    "biology_score": st.column_config.NumberColumn("Bio Score", format="%.1f"),
                    "percentile": st.column_config.NumberColumn("Percentile", min_value=0.0, max_value=100.0, format="%.1f"),
                    "rank": st.column_config.NumberColumn("Rank", min_value=1, format="%d"),
                    "target_score": st.column_config.NumberColumn("Target Score", format="%.1f"),
                    "difficulty": st.column_config.SelectboxColumn("Difficulty", options=["Easy", "Medium", "Hard", "Very Hard"]),
                    "time_taken_minutes": st.column_config.NumberColumn("Time (mins)", min_value=1, format="%d"),
                    "feedback": st.column_config.TextColumn("Feedback")
                },
                hide_index=True,
            )

            # Check for changes and apply
            # The data_editor returns a dictionary, not a DataFrame with .edited_rows etc.
            # We need to compare the original DataFrame with the edited one.
            # This logic will handle updates, additions, and deletions.

            # Re-load data after data_editor interaction to get the latest state for comparison
            current_df_from_db = load_mock_test_results(conn, USER_ID_RMJ)

            # Compare the edited_df with the current_df_from_db to find changes
            # Streamlit's data_editor returns the *full* edited dataframe, not just changes.
            # We need to manually compare.

            # Convert to appropriate types for comparison if necessary
            current_df_from_db['assessment_date'] = current_df_from_db['assessment_date'].astype(str)
            edited_df['assessment_date'] = edited_df['assessment_date'].astype(str)

            # Identify deleted rows (rows in current_df_from_db but not in edited_df by 'id')
            deleted_ids = current_df_from_db[~current_df_from_db['id'].isin(edited_df['id'])]['id'].tolist()

            # Identify added and edited rows (by comparing 'id' and then values)
            updated_or_added_rows = []
            for idx, row in edited_df.iterrows():
                row_id = row['id']
                if row_id in current_df_from_db['id'].values:
                    # Existing row - check for edits
                    original_row = current_df_from_db[current_df_from_db['id'] == row_id].iloc[0]
                    # Check if any value has changed (excluding calculated columns)
                    changed = False
                    for col in original_row.index:
                        if col not in ['id', 'user_id', 'neural_signature', 'timestamp', 'percentage_score', 'accuracy_q', 'unattempted']:
                            # Handle potential type mismatches or NaNs for comparison
                            val_edited = row.get(col)
                            val_original = original_row.get(col)

                            if pd.isna(val_edited) and pd.isna(val_original):
                                continue # Both are NaN, consider them equal
                            if val_edited != val_original:
                                changed = True
                                break
                    if changed:
                        updated_or_added_rows.append(row) # Treat as update
                else:
                    # New row (id not in original df)
                    updated_or_added_rows.append(row) # Treat as add

            if deleted_ids or updated_or_added_rows:
                st.markdown("---")
                st.subheader("Apply Data Matrix Changes")
                if st.button("Commit Changes to Database", type="primary"):
                    success_count = 0
                    
                    for test_id in deleted_ids:
                        if delete_mock_test_result(conn, test_id):
                            success_count += 1
                        else:
                            st.error(f"Failed to delete entry ID: {test_id}.")

                    for row_data in updated_or_added_rows:
                        # For existing rows, update. For new rows, add.
                        if row_data['id'] in current_df_from_db['id'].values:
                            # Update existing row
                            for col, value in row_data.items():
                                if col not in ['id', 'user_id', 'neural_signature', 'timestamp', 'percentage_score', 'accuracy_q', 'unattempted']:
                                    update_mock_test_result(conn, row_data['id'], col, value)
                            success_count += 1 # Count as one successful update
                        else:
                            # Add new row
                            # Ensure all necessary fields are present for new additions
                            if all(col in row_data and pd.notna(row_data[col]) for col in ['assessment_date', 'exam_type', 'test_name', 'domain', 'total_score', 'max_score_possible']):
                                assessment_date_str = row_data['assessment_date']
                                if isinstance(row_data['assessment_date'], date):
                                    assessment_date_str = row_data['assessment_date'].strftime(DATE_FORMAT)

                                if add_mock_test_result(
                                    conn, USER_ID_RMJ, assessment_date_str, row_data['exam_type'], row_data['test_name'], row_data['domain'],
                                    row_data.get('total_questions', 0), row_data.get('attempted', 0), row_data.get('correct', 0), row_data.get('wrong', 0),
                                    row_data.get('physics_score', 0.0), row_data.get('chemistry_score', 0.0), row_data.get('maths_score', 0.0), row_data.get('biology_score', 0.0),
                                    row_data['total_score'], row_data['max_score_possible'], row_data.get('percentile', 0.0), row_data.get('rank', 0), row_data.get('target_score', 0.0),
                                    row_data.get('difficulty', 'Medium'), row_data.get('time_taken_minutes', 0), row_data.get('feedback', ''), NEURAL_SIGNATURE_RMJ, datetime.now().isoformat()
                                ):
                                    success_count += 1
                                else:
                                    st.error(f"Failed to add new row: {row_data}")
                            else:
                                st.warning(f"Skipping incomplete new row: {row_data}")

                    if success_count > 0:
                        st.success(f"✅ Successfully committed {success_count} data matrix changes!")
                        st.session_state.mock_test_df = load_mock_test_results(conn, USER_ID_RMJ) # Refresh DataFrame
                        st.toast("Data matrix re-synchronized.", icon="✨")
                        st.rerun()
                    else:
                        st.info("No changes were applied or committed.")
            else:
                st.info("No uncommitted changes detected in the data matrix.")


    with tab_analyze:
        st.subheader("Performance Analytics & Trend Analysis")

        if st.session_state.mock_test_df.empty:
            st.info("No data available for analysis. Log some assessments first.")
        else:
            df_analysis = st.session_state.mock_test_df.copy()

            # Ensure assessment_date is datetime for plotting
            df_analysis['assessment_date'] = pd.to_datetime(df_analysis['assessment_date'])
            df_analysis = df_analysis.sort_values('assessment_date')

            st.markdown("---")
            st.subheader("Overall Performance Trend (Percentage Score)")
            fig_score_trend = px.line(df_analysis, x='assessment_date', y='percentage_score', color='exam_type', # Color by exam_type
                                      title='Percentage Score Trend Over Time by Exam Type',
                                      labels={'assessment_date': 'Assessment Date', 'percentage_score': 'Score (%)'})
            fig_score_trend.update_layout(title_x=0.5, yaxis_range=[0,100]) # Ensure y-axis is 0-100 for percentages
            st.plotly_chart(fig_score_trend, use_container_width=True)

            st.markdown("---")
            st.subheader("Domain Proficiency Radar Chart (Average Percentage Score)")
            # Calculate average percentage score per domain
            domain_avg_scores = df_analysis.groupby('domain')['percentage_score'].mean().reset_index()

            if not domain_avg_scores.empty:
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=domain_avg_scores['percentage_score'],
                    theta=domain_avg_scores['domain'],
                    fill='toself',
                    name='Average Score',
                    marker_color=px.colors.sequential.Plasma[5]
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis_title="Avg Score (%)", # Updated title
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            tickvals=[0, 25, 50, 75, 100],
                            ticktext=['0%', '25%', '50%', '75%', '100%'], # Updated tick labels
                            linecolor='rgba(0, 240, 255, 0.5)', # Neon blue for grid lines
                            gridcolor='rgba(0, 240, 255, 0.2)'
                        ),
                        angularaxis=dict(
                            linecolor='rgba(0, 240, 255, 0.5)',
                            gridcolor='rgba(0, 240, 255, 0.2)'
                        ),
                        bgcolor='rgba(27, 27, 37, 0.7)' # Semi-transparent card background
                    ),
                    showlegend=True,
                    title='Domain Proficiency Overview (Percentage Score)', # Updated title
                    title_x=0.5,
                    font=dict(color='var(--text-primary)', family='Share Tech Mono'),
                    paper_bgcolor='transparent', # Make background transparent
                    plot_bgcolor='transparent',
                    hoverlabel=dict(bgcolor="rgba(0, 240, 255, 0.8)", font_size=12, font_family="Share Tech Mono")
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("No domain-wise data to generate radar chart.")

            st.markdown("---")
            st.subheader("Percentage Score vs. Time Taken & Difficulty")
            fig_scatter_3d = px.scatter_3d(df_analysis,
                                           x='time_taken_minutes',
                                           y='difficulty',
                                           z='percentage_score', # Use percentage score
                                           color='exam_type', # Color by exam type
                                           title='Percentage Score vs. Time Taken and Difficulty', # Updated title
                                           labels={'time_taken_minutes': 'Time Taken (minutes)', 'percentage_score': 'Score (%)'}, # Updated label
                                           color_discrete_sequence=px.colors.qualitative.Plotly
                                          )
            fig_scatter_3d.update_layout(title_x=0.5)
            st.plotly_chart(fig_scatter_3d, use_container_width=True)

            st.markdown("---")
            st.subheader("Subject-wise Performance (Average Percentage Score)")
            # Calculate average percentage score for each subject
            subject_avg_scores = df_analysis[[
                'physics_score', 'chemistry_score', 'maths_score', 'biology_score', 'max_score_possible'
            ]].copy()
            
            # Convert subject scores to percentage
            for col in ['physics_score', 'chemistry_score', 'maths_score', 'biology_score']:
                subject_avg_scores[col] = (subject_avg_scores[col] / subject_avg_scores['max_score_possible'] * 100).round(2)
                subject_avg_scores.loc[subject_avg_scores['max_score_possible'] == 0, col] = 0.0 # Handle division by zero

            # Drop max_score_possible for aggregation
            subject_avg_scores = subject_avg_scores.drop(columns=['max_score_possible'])
            
            # Melt the DataFrame to long format for Plotly Express
            subject_avg_scores_melted = subject_avg_scores.melt(var_name='Subject', value_name='Average Percentage Score')
            
            # Filter out subjects with no data (all zeros or NaNs after conversion)
            subject_avg_scores_melted = subject_avg_scores_melted[subject_avg_scores_melted['Average Percentage Score'] > 0]

            if not subject_avg_scores_melted.empty:
                fig_subject_bar = px.bar(
                    subject_avg_scores_melted,
                    x='Subject',
                    y='Average Percentage Score',
                    title='Average Percentage Score Per Subject',
                    labels={'Average Percentage Score': 'Average Score (%)'},
                    color='Average Percentage Score',
                    color_continuous_scale=px.colors.sequential.Plasma
                )
                fig_subject_bar.update_layout(title_x=0.5, yaxis_range=[0,100])
                st.plotly_chart(fig_subject_bar, use_container_width=True)
            else:
                st.info("No subject-wise data to display.")


    with tab_ai_nexus:
        st.subheader("🧠 AI Nexus Co-Pilot: Cognitive Guidance Interface")
        st.info("Engage your AI Co-Pilot for personalized insights, predictions, and motivational directives.")

        profile_directives = {
            "user_name": "rmj",
            "neural_signature": NEURAL_SIGNATURE_RMJ,
            "current_date": date.today().strftime(DATE_FORMAT),
            "knowledge_domains": UNIVERSAL_KNOWLEDGE_DOMAINS
        }

        # Display chat history
        chat_container = st.container(height=400, border=True)
        with chat_container:
            for speaker, message in st.session_state.ai_nexus_chat_history:
                if speaker == "user":
                    st.chat_message("user", avatar="👤").write(message)
                else:
                    st.chat_message("ai_nexus", avatar="🤖").write(message)

        user_query = st.chat_input("Transmit Neural Query to AI Nexus Co-Pilot...")
        
        if user_query:
            st.session_state.ai_nexus_chat_history.append(("user", user_query))
            user_df = st.session_state.mock_test_df # Pass the current DataFrame
            if not user_df.empty:
                # Ensure data types are correct for AI processing
                user_df['total_score'] = pd.to_numeric(user_df['total_score'], errors='coerce')
                user_df['max_score_possible'] = pd.to_numeric(user_df['max_score_possible'], errors='coerce')
                user_df['percentage_score'] = (user_df['total_score'] / user_df['max_score_possible'] * 100).round(2)
                user_df.loc[user_df['max_score_possible'] == 0, 'percentage_score'] = 0.0 # Handle division by zero
                user_df['time_taken_minutes'] = pd.to_numeric(user_df['time_taken_minutes'], errors='coerce')
                user_df['assessment_date'] = pd.to_datetime(user_df['assessment_date'])
                
                with st.spinner("AI Nexus Co-Pilot is synthesizing response..."):
                    response = ai_nexus_response(user_query, user_df.sort_values(by="assessment_date"), profile_directives)
                    st.session_state.ai_nexus_chat_history.append(("ai_nexus", response))
                st.rerun()
            else:
                st.toast("Please transmit a neural query to your AI Nexus Co-Pilot.", icon="❓")
        
        if st.button("🧹 Purge Chat Log", type="secondary"):
            st.session_state.ai_nexus_chat_history = []
            st.toast("Chat log purged from temporary memory banks.", icon="🧹")
            st.rerun()

# This part ensures that if this file is run directly (for testing as a standalone app), it still works.
# In a multi-page app, the main app would import and call `cognisynth_app()`.
if __name__ == "__main__":
    cognisynth_app()