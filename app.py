import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime, timedelta
import random
import os
import plotly.express as px
import plotly.graph_objects as go
from contextlib import contextmanager
import logging

# --- Setup Logging for the dashboard ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
dashboard_logger = logging.getLogger(__name__)

# --- Configuration & Constants ---
DPP_DB_FILE = "study_data.db" # Database for DPP logs (from dpp_logger.py)
PLANNER_DB_FILE = "study_data.db" # Database for Study Planner tasks (from study_planner.py)
QUOTE_FILE = "quotes.txt"

# --- Streamlit Page Configuration (MUST BE THE VERY FIRST STREAMLIT COMMAND) ---
# Explicitly set theme to dark and remove default menu/footer for a cleaner look
st.set_page_config(
    page_title="🚀 Quantum Study Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
    # Force dark theme via page config - this sets the data-theme attribute on <body>
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- Custom CSS for a Futuristic, Dark, and Neon Aesthetic (ONLY DARK MODE) ---
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

# --- Database Connection Context Manager ---
@contextmanager
def get_db_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        yield conn
    except sqlite3.Error as e:
        dashboard_logger.error(f"Database connection error for {db_file}: {e}")
        st.error(f"🚨 Database connection error for {db_file}: {e}")
    finally:
        if conn:
            conn.close()

# --- Data Loading Functions ---

@st.cache_data(ttl=300) # Cache for 5 minutes
def load_dpp_logs_from_db():
    """Loads DPP logs from the database."""
    if not os.path.exists(DPP_DB_FILE):
        dashboard_logger.warning(f"DPP log database file '{DPP_DB_FILE}' not found.")
        return pd.DataFrame() # Return empty DataFrame if DB doesn't exist
    try:
        with get_db_connection(DPP_DB_FILE) as conn:
            df = pd.read_sql("SELECT * FROM dpp_log ORDER BY Date DESC, ID DESC", conn)
            if not df.empty:
                df['Date'] = pd.to_datetime(df['Date']).dt.date
                df['Time_Taken'] = pd.to_numeric(df['Time_Taken'], errors='coerce')
                df['Accuracy'] = pd.to_numeric(df['Accuracy'], errors='coerce')
            dashboard_logger.info(f"Loaded {len(df)} DPP logs.")
            return df
    except Exception as e:
        dashboard_logger.error(f"Error loading DPP logs from '{DPP_DB_FILE}': {e}", exc_info=True)
        st.warning(f"⚠️ Could not load DPP log data from '{DPP_DB_FILE}': {e}. Ensure the DPP Logger app has been run to create the DB.")
        return pd.DataFrame()

@st.cache_data(ttl=300) # Cache for 5 minutes
def load_planner_tasks_from_db():
    """Loads study planner tasks from the database."""
    if not os.path.exists(PLANNER_DB_FILE):
        dashboard_logger.warning(f"Study Planner database file '{PLANNER_DB_FILE}' not found.")
        return pd.DataFrame()
    try:
        with get_db_connection(PLANNER_DB_FILE) as conn:
            cursor = conn.cursor()
            # CHANGE 1: Change 'tasks' to 'study_tasks' for PRAGMA table_info
            cursor.execute("PRAGMA table_info(study_tasks)")
            columns_info = cursor.fetchall()
            available_columns = [col[1] for col in columns_info]

            # CHANGE 2: Update select_cols to match the actual columns in 'study_tasks'
            # Based on study_planner.py, the primary columns are:
            # ID, Subject, Topic, DueDate, Status, Priority, Notes, CreatedDate
            select_cols = ['ID', 'Subject', 'Topic', 'DueDate', 'Status', 'Priority']

            # Add optional columns if they exist in the table
            if 'Notes' in available_columns:
                select_cols.append('Notes')
            if 'CreatedDate' in available_columns:
                select_cols.append('CreatedDate')

            query_cols = ", ".join(select_cols)
            # CHANGE 3: Change 'FROM tasks' to 'FROM study_tasks' and 'ORDER BY deadline' to 'ORDER BY DueDate'
            df = pd.read_sql_query(f"SELECT {query_cols} FROM study_tasks ORDER BY DueDate ASC", conn)

            if not df.empty:
                # Convert DueDate to date object
                df['DueDate'] = pd.to_datetime(df['DueDate'], errors='coerce').dt.date
                if 'CreatedDate' in df.columns:
                    df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], errors='coerce')
            dashboard_logger.info(f"Loaded {len(df)} planner tasks.")
            return df
    except Exception as e:
        dashboard_logger.error(f"Error loading Study Planner data from '{PLANNER_DB_FILE}': {e}", exc_info=True)
        st.warning(f"⚠️ Could not load Study Planner data from '{PLANNER_DB_FILE}': {e}. Ensure the Study Planner app has been run to create the DB.")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_daily_quote():
    """Reads a random quote from quotes.txt."""
    if os.path.exists(QUOTE_FILE):
        with open(QUOTE_FILE, 'r') as f:
            quotes = [q.strip() for q in f if q.strip()]
        if quotes:
            return random.choice(quotes)
    return "💡 Discipline is the bridge between goals and accomplishment." # Default quote

# --- Main Dashboard UI ---

st.title("🚀 Quantum Study Dashboard")
st.markdown("Your centralized hub for DPP progress and study planning.")

# Display Daily Quote
st.info(f"**Today's Quantum Insight:** *\"{get_daily_quote()}\"*")

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Performance Overview", "🗓️ Study Planner Snapshot", "⚙️ Data Management"])

with tab1:
    st.header("📊 DPP Performance Overview")
    st.markdown("Track your Daily Practice Problems (DPP) progress and accuracy.")

    dpp_df = load_dpp_logs_from_db()

    if dpp_df.empty:
        st.info("No DPP logs found. Please use the DPP Logger app to record your practice sessions.")
    else:
        # Key Metrics
        total_dpps = len(dpp_df)
        avg_accuracy = dpp_df['Accuracy'].mean()
        avg_time = dpp_df['Time_Taken'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total DPPs Logged", total_dpps)
        with col2:
            st.metric("Average Accuracy", f"{avg_accuracy:.2f}%")
        with col3:
            st.metric("Average Time/DPP", f"{avg_time:.2f} mins")

        st.markdown("---")
        st.subheader("Subject-wise Performance")
        subject_performance = dpp_df.groupby('Subject').agg(
            Total_DPPs=('ID', 'count'),
            Avg_Accuracy=('Accuracy', 'mean'),
            Avg_Time_Taken=('Time_Taken', 'mean')
        ).reset_index()
        subject_performance.columns = ['Subject', 'Total DPPs', 'Average Accuracy', 'Average Time Taken']
        st.dataframe(subject_performance, use_container_width=True)

        st.markdown("---")
        st.subheader("DPP Accuracy Trend Over Time")
        # Ensure 'Date' is datetime for plotting
        dpp_df_sorted = dpp_df.sort_values('Date')
        fig_dpp_trend = px.line(dpp_df_sorted, x='Date', y='Accuracy', color='Subject',
                                title='Accuracy Trend Over Time',
                                labels={'Accuracy': 'Accuracy (%)'})
        fig_dpp_trend.update_layout(title_x=0.5)
        st.plotly_chart(fig_dpp_trend, use_container_width=True)

with tab2:
    st.header("🗓️ Study Planner Snapshot")
    st.markdown("Quick glance at your upcoming tasks, deadlines, and progress.")

    planner_df = load_planner_tasks_from_db()

    if planner_df.empty:
        st.info("No study tasks found. Please use the Quantum Study Planner app to add your tasks.")
    else:
        # Key Metrics for Study Planner
        total_tasks = len(planner_df)
        pending_tasks = planner_df[planner_df['Status'] == 'Pending']
        completed_tasks = planner_df[planner_df['Status'] == 'Completed']

        col_plan1, col_plan2, col_plan3 = st.columns(3)
        with col_plan1:
            st.metric("Total Study Tasks", total_tasks)
        with col_plan2:
            # CHANGE 5: Update column reference from 'deadline' to 'DueDate' and 'status' to 'Status'
            overdue_tasks_count = len(pending_tasks[pending_tasks['DueDate'] < date.today()])
            st.metric("Overdue Tasks", overdue_tasks_count)
        with col_plan3:
            # CHANGE 6: Update column reference from 'deadline' to 'DueDate' and 'status' to 'Status'
            upcoming_tasks_count = len(planner_df[(planner_df['Status'] == 'Pending') & (planner_df['DueDate'] >= date.today())])
            st.metric("Upcoming Tasks", upcoming_tasks_count)

        st.markdown("---")
        st.subheader("Task Status Distribution")
        status_counts = planner_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status_pie = px.pie(status_counts, values='Count', names='Status',
                                title='Distribution of Study Task Statuses',
                                color_discrete_sequence=px.colors.qualitative.Dark24, hole=0.3)
        fig_status_pie.update_layout(title_x=0.5)
        st.plotly_chart(fig_status_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("Upcoming Study Tasks (Next 7 Days)")
        seven_days_from_now = date.today() + timedelta(days=7)
        # CHANGE 7: Update column reference from 'deadline' to 'DueDate' and 'status' to 'Status'
        upcoming_df = planner_df[
            (planner_df['Status'] != 'Completed') &
            (planner_df['DueDate'] >= date.today()) &
            (planner_df['DueDate'] <= seven_days_from_now)
        ].sort_values('DueDate')

        if upcoming_df.empty:
            st.info("No pending tasks due in the next 7 days. Great job or time to plan!")
        else:
            # Select relevant columns for display
            display_cols = ['ID', 'Subject', 'Topic', 'DueDate', 'Priority', 'Status']
            st.dataframe(upcoming_df[display_cols], use_container_width=True)


with tab3:
    st.header("⚙️ Data Management & Support")
    st.markdown("Manage your application data, download backups, or perform resets.")

    st.subheader("Backup & Restore")
    st.info("Regularly back up your data to prevent loss.")
    col_backup, col_restore = st.columns(2)
    with col_backup:
        if os.path.exists(DPP_DB_FILE):
            with open(DPP_DB_FILE, "rb") as f:
                st.download_button(
                    label="📥 Download DPP Data (study_data.db)",
                    data=f.read(),
                    file_name="study_data_backup.db",
                    mime="application/octet-stream",
                    use_container_width=True
                )
        else:
            st.error(f"DPP database file (`{DPP_DB_FILE}`) not found.")

    with col_restore:
        # Implement restore logic if desired (requires file uploader and DB overwrite)
        st.warning("Restore functionality not yet implemented. Manual replacement of DB file is required.")

    st.markdown("---")
    st.subheader("Clear Application Data")
    st.warning("🚨 **Caution:** Clearing data is irreversible and will permanently delete all stored information for the selected module.")

    col_clear_dpp, col_clear_planner = st.columns(2)

    with col_clear_dpp:
        if st.button("🗑️ Clear All DPP Log Data", type="secondary", use_container_width=True):
            if st.checkbox("I understand and want to permanently delete ALL DPP log data.", key="confirm_clear_dpp"):
                try:
                    with get_db_connection(DPP_DB_FILE) as conn:
                        conn.execute("DELETE FROM dpp_log")
                        conn.commit()
                    st.success("✅ All DPP log data cleared successfully!")
                    st.cache_data.clear() # Clear cache for DPP logs
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear DPP log data: {e}. Ensure table 'dpp_log' exists.")

    with col_clear_planner:
        if st.button("🗑️ Clear All Study Planner Data", type="secondary", use_container_width=True):
            if st.checkbox("I understand and want to permanently delete ALL Study Planner data.", key="confirm_clear_planner"):
                try:
                    with get_db_connection(PLANNER_DB_FILE) as conn:
                        # CHANGE 8: Change 'DELETE FROM tasks' to 'DELETE FROM study_tasks'
                        conn.execute("DELETE FROM study_tasks")
                        # Remove or comment out lines for tables not explicitly created by your apps
                        # conn.execute("DELETE FROM time_logs") # This table is not created by study_planner.py or dpp_logger.py
                        # conn.execute("DELETE FROM streaks") # This table is not created by study_planner.py or dpp_logger.py
                        # conn.execute("DELETE FROM badges") # This table is not created by study_planner.py or dpp_logger.py
                        conn.commit()
                    st.success("✅ All Study Planner data cleared successfully!")
                    st.cache_data.clear() # Clear cache for planner tasks
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear Study Planner data: {e}. Ensure table 'study_tasks' exists.")
                    # Original message was too specific to non-existent tables:
                    # st.error(f"Failed to clear Study Planner data: {e}. Check tables 'tasks', 'time_logs', 'streaks', 'badges'.")

    st.markdown("---")
    st.subheader("💬 Quotes Management")
    st.info("To add or change daily motivation quotes, please edit the `quotes.txt` file directly in the application's folder. Each quote should be on a new line for proper parsing.")