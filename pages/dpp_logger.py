import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime
import logging
import plotly.express as px
from contextlib import contextmanager
import os

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

# --- Database Configuration ---
DB_FILE = "study_data.db"
DATE_FORMAT = "%Y-%m-%d"

# --- Streamlit Page Configuration ---
# Setting page config here for standalone running.
# In a multi-page app, the main app's page config will take precedence if it's placed in a 'pages' folder.
st.set_page_config(
    page_title="🧪 DPP Logger",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# --- Custom CSS for a Futuristic, Dark, and Neon Aesthetic (ONLY DARK MODE) ---
# This CSS is identical to the one in your main dashboard for consistency
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

# --- Database Functions ---

@st.cache_resource
def get_connection():
    """Establishes and returns a SQLite database connection.
    This connection is cached and reused across Streamlit reruns.
    """
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Access columns by name
        app_logger.info(f"Successfully connected to database: {DB_FILE}")
        return conn
    except sqlite3.Error as e:
        st.error(f"🚨 Database connection error: {e}")
        app_logger.exception("Failed to connect to database.")
        return None

def create_dpp_log_table(conn):
    """Creates the dpp_log table if it doesn't already exist."""
    if conn is None:
        return False
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dpp_log (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Subject TEXT NOT NULL,
                Chapter TEXT NOT NULL,
                DPP_Number TEXT NOT NULL,
                Score INTEGER NOT NULL,
                Accuracy INTEGER NOT NULL,
                Time_Taken INTEGER NOT NULL,
                Notes TEXT,
                UNIQUE(Date, Subject, Chapter, DPP_Number)
            );
        """)
        conn.commit()
        app_logger.info("DPP log table ensured.")
        return True
    except sqlite3.Error as e:
        st.error(f"🚨 Error creating table: {e}")
        app_logger.exception("Failed to create dpp_log table.")
        return False

@st.cache_data(ttl=300) # Cache data for 5 minutes
def load_dpp_logs(_conn):
    """Loads all DPP logs from the database into a Pandas DataFrame."""
    if _conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM dpp_log ORDER BY Date DESC, ID DESC", _conn)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        app_logger.info("DPP logs loaded successfully.")
        return df
    except Exception as e:
        st.error(f"🚨 Error loading DPP logs: {e}")
        app_logger.exception("Failed to load DPP logs.")
        return pd.DataFrame()

def insert_dpp_log(conn, dpp_data):
    """Inserts a new DPP log entry into the database."""
    if conn is None:
        return False
    try:
        conn.execute("""
            INSERT INTO dpp_log
            (Date, Subject, Chapter, DPP_Number, Score, Accuracy, Time_Taken, Notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, dpp_data)
        conn.commit()
        app_logger.info(f"Inserted DPP log: {dpp_data}")
        return True
    except sqlite3.IntegrityError:
        st.warning("⚠️ This exact DPP (Date, Subject, Chapter, DPP Number) already exists. Please modify details or delete the existing one.")
        return False
    except sqlite3.Error as e:
        st.error(f"🚨 Error inserting DPP log: {e}")
        app_logger.exception("Failed to insert DPP log.")
        return False

def update_dpp_log(conn, log_id, dpp_data):
    """Updates an existing DPP log entry."""
    if conn is None:
        return False
    try:
        conn.execute("""
            UPDATE dpp_log
            SET Date = ?, Subject = ?, Chapter = ?, DPP_Number = ?,
                Score = ?, Accuracy = ?, Time_Taken = ?, Notes = ?
            WHERE ID = ?;
        """, (*dpp_data, log_id))
        conn.commit()
        app_logger.info(f"Updated DPP log ID {log_id}")
        return True
    except sqlite3.IntegrityError:
        st.warning("⚠️ An entry with this Date, Subject, Chapter, and DPP Number already exists. Please choose unique values.")
        return False
    except sqlite3.Error as e:
        st.error(f"🚨 Error updating DPP log: {e}")
        app_logger.exception("Failed to update DPP log.")
        return False

def delete_dpp_log(conn, log_id):
    """Deletes a DPP log entry by its ID."""
    if conn is None:
        return False
    try:
        conn.execute("DELETE FROM dpp_log WHERE ID = ?", (log_id,))
        conn.commit()
        app_logger.info(f"Deleted DPP log ID: {log_id}")
        return True
    except sqlite3.Error as e:
        st.error(f"🚨 Error deleting DPP log: {e}")
        app_logger.exception("Failed to delete DPP log.")
        return False

# --- Utility Functions ---

def validate_dpp_inputs(score, accuracy, time_taken, chapter, dpp_number):
    """Performs input validation for DPP log fields."""
    if not chapter.strip():
        st.error("Chapter Name cannot be empty.")
        return False
    if not dpp_number.strip():
        st.error("DPP Number cannot be empty.")
        return False
    if not (0 <= score <= 100):
        st.error("Score must be between 0 and 100.")
        return False
    if not (0 <= accuracy <= 100):
        st.error("Accuracy must be between 0 and 100.")
        return False
    if time_taken <= 0:
        st.error("Time Taken must be greater than 0.")
        return False
    return True

def clear_caches_and_rerun():
    """Clears Streamlit caches and reruns the app."""
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# --- Streamlit UI ---

st.title("🚀 DPP Progress Tracker")
st.markdown("Track your Daily Practice Problems performance with ease and visualize your growth.")

# Get the persistent database connection
conn = get_connection()

# Ensure database table exists
if conn is None or not create_dpp_log_table(conn):
    st.stop() # Stop if connection or table creation fails

# --- Sidebar for Navigation/Quick Actions ---
with st.sidebar:
    st.header("⚡ Quick Actions")
    st.image("https://images.unsplash.com/photo-1510531704581-5b97826359de?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_column_width=True, caption="Stay focused, stay productive!")
    st.info("💡 Tip: Navigate between tabs to log, manage, and analyze your DPPs.")
    if st.button("🔄 Refresh All Data", help="Clear data cache and reload all DPP entries. Useful after manual DB changes."):
        clear_caches_and_rerun()
        st.success("Data refreshed!")
    st.markdown("---")
    st.subheader("About This App")
    st.markdown("""
        This application helps you keep a detailed log of your Daily Practice Problems (DPPs).
        Track your scores, accuracy, and time taken to identify areas for improvement.
        \n\nDeveloped by Your Name/Team
    """)
    st.markdown(f"Current Time (IST): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# --- Main Content Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Log New DPP", "📚 View & Manage DPPs", "📈 Analytics & Insights"])

with tab1:
    st.header("✨ Log Your Daily Practice Problem")
    st.markdown("Record your performance after completing a DPP. Detailed logs lead to better insights!")

    with st.form("dpp_add_form", clear_on_submit=True):
        st.markdown("### DPP Details")
        col_date, col_subject = st.columns(2)
        with col_date:
            dpp_date = st.date_input("🗓️ **DPP Date**", date.today(), help="Select the date you completed this DPP.")
        with col_subject:
            subject = st.selectbox("📚 **Subject**", ["Physics", "Chemistry", "Maths", "Biology", "Others"], help="Choose the subject of this DPP.")

        col_chap, col_dpp_num = st.columns(2)
        with col_chap:
            chapter = st.text_input("📖 **Chapter Name**", placeholder="e.g., Kinematics, Chemical Bonding", help="Enter the specific chapter the DPP belongs to.")
        with col_dpp_num:
            dpp_number = st.text_input("🔢 **DPP Number**", placeholder="e.g., DPP 03, Test 1", help="Specify the DPP number or identifier.")

        st.markdown("### Performance Metrics")
        col_score, col_accuracy, col_time = st.columns(3)
        with col_score:
            score = st.number_input("💯 **Score** (out of 100)", min_value=0, max_value=100, value=75, help="Your raw score on the DPP.")
        with col_accuracy:
            accuracy = st.slider("🎯 **Accuracy (%)**", 0, 100, 75, help="Your percentage of correct answers. Move the slider to adjust.")
        with col_time:
            time_taken = st.number_input("⏱️ **Time Taken** (minutes)", min_value=1, value=60, help="Time spent solving the DPP in minutes.")

        notes = st.text_area("✍️ **Notes** (Optional)", placeholder="Key learnings, common mistakes, areas to review, question types...", max_chars=500, help="Add any relevant notes or reflections on this DPP.")

        st.markdown("---")
        submitted = st.form_submit_button("✅ **Submit DPP Log**", use_container_width=True, type="primary")

        if submitted:
            if validate_dpp_inputs(score, accuracy, time_taken, chapter, dpp_number):
                dpp_row_data = (str(dpp_date), subject.strip(), chapter.strip(),
                                 dpp_number.strip(), score, accuracy, time_taken, notes.strip())
                if insert_dpp_log(conn, dpp_row_data):
                    st.success("🎉 DPP logged successfully! Check 'View & Manage DPPs' tab.")
                    clear_caches_and_rerun()
                else:
                    st.error("Please correct the input errors above.")

with tab2:
    st.header("📋 Your DPP History")
    st.markdown("Easily review, filter, edit, or delete your past DPP entries. Keep your records organized!")

    df_logs = load_dpp_logs(_conn=conn)

    if df_logs.empty:
        st.info("No DPP entries recorded yet. Let's start logging your first DPP in the 'Log New DPP' tab!")
    else:
        st.subheader("🔍 Filter & Search Options")
        col_filter_subj, col_filter_date, col_search_text = st.columns([1, 1, 2])
        with col_filter_subj:
            selected_subject = st.selectbox("Filter by Subject", ["All"] + df_logs["Subject"].unique().tolist(), key="filter_subject")
        with col_filter_date:
            unique_dates = sorted(df_logs["Date"].dt.date.unique().tolist(), reverse=True)
            selected_date = st.selectbox("Filter by Date", ["All"] + unique_dates, format_func=lambda x: "All" if x == "All" else x.strftime(DATE_FORMAT), key="filter_date")
        with col_search_text:
            search_query = st.text_input("Search (Chapter, DPP No., Notes)", placeholder="e.g., optics, DPP 05, errors", key="search_query")

        filtered_df = df_logs.copy()
        if selected_subject != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]
        if selected_date != "All":
            filtered_df = filtered_df[filtered_df["Date"].dt.date == selected_date]
        if search_query:
            search_query_lower = search_query.lower()
            filtered_df = filtered_df[
                filtered_df.apply(lambda row:
                    search_query_lower in str(row["Chapter"]).lower() or
                    search_query_lower in str(row["DPP_Number"]).lower() or
                    search_query_lower in str(row["Notes"]).lower(), axis=1
                )
            ]

        if filtered_df.empty:
            st.warning("No DPPs match your current filters. Try adjusting your selections.")
        else:
            st.subheader(f"📊 Displaying {len(filtered_df)} Matching DPP Entry(s)")
            st.dataframe(filtered_df.set_index("ID"), use_container_width=True, height=350)

            st.download_button(
                label="📥 Download Filtered Data as CSV",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name=f"dpp_logs_filtered_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download the currently filtered DPP entries as a CSV file."
            )

            st.markdown("---")
            col_edit, col_delete = st.columns(2)

            with col_edit:
                st.subheader("✏️ Edit a DPP Entry")
                edit_id_options = filtered_df["ID"].tolist()
                if not edit_id_options:
                    st.info("No entries available for editing under current filters.")
                else:
                    selected_edit_id = st.selectbox("Select ID to Edit", edit_id_options, key="edit_select_id_tab2", help="Choose the ID of the DPP entry you wish to modify.")
                    if selected_edit_id:
                        entry_to_edit = df_logs[df_logs["ID"] == selected_edit_id].iloc[0]
                        with st.form(f"edit_form_{selected_edit_id}"):
                            st.markdown(f"**Editing Entry ID: {selected_edit_id}**")
                            e_date = st.date_input("Date", value=entry_to_edit["Date"].date())
                            e_subject = st.selectbox("Subject", ["Physics","Chemistry","Maths","Biology","Others"], index=["Physics","Chemistry","Maths","Biology","Others"].index(entry_to_edit["Subject"]))
                            e_chapter = st.text_input("Chapter Name", value=entry_to_edit["Chapter"])
                            e_dpp_num = st.text_input("DPP Number", value=entry_to_edit["DPP_Number"])
                            e_score = st.number_input("Score", min_value=0, max_value=100, value=int(entry_to_edit["Score"]))
                            e_accuracy = st.slider("Accuracy (%)", 0, 100, value=int(entry_to_edit["Accuracy"]))
                            e_time_taken = st.number_input("Time Taken (min)", min_value=1, value=int(entry_to_edit["Time_Taken"]))
                            e_notes = st.text_area("Notes (opt)", value=entry_to_edit["Notes"], max_chars=500)

                            update_button = st.form_submit_button("🔄 Update Entry", type="primary", use_container_width=True)
                            if update_button:
                                if validate_dpp_inputs(e_score, e_accuracy, e_time_taken, e_chapter, e_dpp_num):
                                    updated_data = (str(e_date), e_subject.strip(), e_chapter.strip(),
                                                     e_dpp_num.strip(), e_score, e_accuracy, e_time_taken, e_notes.strip())
                                    if update_dpp_log(conn, selected_edit_id, updated_data):
                                        st.success(f"🎉 Entry ID {selected_edit_id} updated successfully!")
                                        clear_caches_and_rerun()

            with col_delete:
                st.subheader("🗑️ Delete a DPP Entry")
                delete_id_options = filtered_df["ID"].tolist()
                if not delete_id_options:
                    st.info("No entries to delete under current filters.")
                else:
                    selected_delete_id = st.selectbox("Select ID to Delete", delete_id_options, key="delete_select_id_tab2", help="Choose the ID of the DPP entry to remove.")
                    if selected_delete_id:
                        if st.button(f"Permanently Delete Entry ID {selected_delete_id}", type="secondary", use_container_width=True):
                            st.warning(f"Are you absolutely sure you want to delete DPP entry ID {selected_delete_id}? This action cannot be undone.")
                            confirm_delete_btn = st.button("🚨 Confirm Deletion", type="primary", key="confirm_del_btn")
                            if confirm_delete_btn:
                                if delete_dpp_log(conn, selected_delete_id):
                                    st.success(f"🗑️ Entry ID {selected_delete_id} deleted.")
                                    clear_caches_and_rerun()

with tab3:
    st.header("📈 Your Performance Analytics")
    st.markdown("Gain insights from your DPP data. Identify strengths, weaknesses, and track your progress over time.")

    df_logs_analysis = load_dpp_logs(_conn=conn)

    if df_logs_analysis.empty:
        st.info("No data available for analytics. Please add some DPP logs first in the 'Log New DPP' tab!")
    else:
        df_logs_analysis['Date'] = pd.to_datetime(df_logs_analysis['Date'])
        df_logs_analysis = df_logs_analysis.sort_values(by='Date')

        st.subheader("📊 Overall Performance Summary")
        col_avg_score, col_avg_accuracy, col_avg_time, col_total_dpps = st.columns(4)
        with col_avg_score:
            st.metric("Average Score", f"{df_logs_analysis['Score'].mean():.2f}")
        with col_avg_accuracy:
            st.metric("Average Accuracy", f"{df_logs_analysis['Accuracy'].mean():.2f}%")
        with col_avg_time:
            st.metric("Average Time Taken", f"{df_logs_analysis['Time_Taken'].mean():.2f} min")
        with col_total_dpps:
            st.metric("Total DPPs Logged", len(df_logs_analysis))

        st.markdown("---")
        st.subheader("📈 Performance Trends Over Time")

        # Interactive Score over Time using Plotly Express
        fig_score_time = px.line(df_logs_analysis, x='Date', y='Score', title='Score Over Time',
                                 labels={'Score': 'Score (out of 100)'},
                                 hover_data=['Subject', 'Chapter', 'DPP_Number', 'Accuracy'])
        fig_score_time.update_layout(hovermode="x unified", title_x=0.5)
        fig_score_time.update_traces(mode='lines+markers')
        st.plotly_chart(fig_score_time, use_container_width=True)

        # Interactive Accuracy over Time using Plotly Express
        fig_accuracy_time = px.line(df_logs_analysis, x='Date', y='Accuracy', title='Accuracy Over Time',
                                     labels={'Accuracy': 'Accuracy (%)'},
                                     hover_data=['Subject', 'Chapter', 'DPP_Number', 'Score'],
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_accuracy_time.update_layout(hovermode="x unified", title_x=0.5)
        fig_accuracy_time.update_traces(mode='lines+markers')
        st.plotly_chart(fig_accuracy_time, use_container_width=True)

        st.markdown("---")
        st.subheader("📚 Subject-wise Performance Breakdown")

        subject_performance = df_logs_analysis.groupby('Subject').agg(
            Avg_Score=('Score', 'mean'),
            Avg_Accuracy=('Accuracy', 'mean'),
            Total_DPPs=('ID', 'count'),
            Avg_Time_Taken=('Time_Taken', 'mean')
        ).reset_index().sort_values(by="Avg_Accuracy", ascending=False)

        st.dataframe(subject_performance.set_index("Subject").round(2), use_container_width=True)

        # Interactive Bar chart for Average Accuracy by Subject
        fig_subject_accuracy = px.bar(subject_performance, x='Subject', y='Avg_Accuracy',
                                     title='Average Accuracy by Subject',
                                     labels={'Avg_Accuracy': 'Average Accuracy (%)'},
                                     color='Avg_Accuracy', color_continuous_scale=px.colors.sequential.Tealgrn,
                                     hover_data=['Total_DPPs', 'Avg_Score'])
        fig_subject_accuracy.update_layout(title_x=0.5)
        st.plotly_chart(fig_subject_accuracy, use_container_width=True)

        st.markdown("---")
        st.subheader("Distribution of Performance Metrics")

        col_hist1, col_hist2 = st.columns(2)
        with col_hist1:
            # Interactive Histogram for Accuracy Distribution
            fig_hist_accuracy = px.histogram(df_logs_analysis, x='Accuracy', nbins=10,
                                             title='Distribution of Accuracy Scores',
                                             labels={'Accuracy': 'Accuracy (%)'},
                                             color_discrete_sequence=['#4287f5'])
            fig_hist_accuracy.update_layout(title_x=0.5)
            st.plotly_chart(fig_hist_accuracy, use_container_width=True)

        with col_hist2:
            # Interactive Histogram for Time Taken Distribution
            fig_hist_time = px.histogram(df_logs_analysis, x='Time_Taken', nbins=10,
                                         title='Distribution of Time Taken',
                                         labels={'Time_Taken': 'Time Taken (minutes)'},
                                         color_discrete_sequence=['#ff6347'])
            fig_hist_time.update_layout(title_x=0.5)
            st.plotly_chart(fig_hist_time, use_container_width=True)