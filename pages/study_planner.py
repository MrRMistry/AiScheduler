import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date
import logging
import plotly.express as px
import plotly.graph_objects as go
from contextlib import contextmanager

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)

# --- Database Configuration ---
DB_FILE = "study_data.db" # Using the same DB file as dpp_logger for consistency
DATE_FORMAT = "%Y-%m-%d"

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="🗓️ Quantum Study Planner",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
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
        box_shadow: 0 0 15px var(--neon-purple), 0 0 25px rgba(157, 0, 255, 0.7); /* Change glow color */
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
        box_shadow: 0 0 10px var(--neon-blue), 0 0 20px rgba(0, 240, 255, 0.6);
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
        box_shadow: 0 0 20px var(--neon-purple), 0 0 30px rgba(157, 0, 255, 0.6);
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

def create_study_tasks_table(conn):
    """Creates the study_tasks table if it doesn't already exist."""
    if conn is None:
        return False
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS study_tasks (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Subject TEXT NOT NULL,
                Topic TEXT NOT NULL,
                DueDate TEXT NOT NULL,
                Priority TEXT NOT NULL,
                Status TEXT NOT NULL,
                Notes TEXT,
                CreatedDate TEXT NOT NULL,
                UNIQUE(Subject, Topic, DueDate)
            );
        """)
        conn.commit()
        app_logger.info("Study tasks table ensured.")
        return True
    except sqlite3.Error as e:
        st.error(f"🚨 Error creating table: {e}")
        app_logger.exception("Failed to create study_tasks table.")
        return False

@st.cache_data(ttl=300) # Cache data for 5 minutes
def load_study_tasks(_conn):
    """Loads all study tasks from the database into a Pandas DataFrame."""
    if _conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM study_tasks ORDER BY DueDate ASC, Priority ASC, ID DESC", _conn)
        if not df.empty:
            df['DueDate'] = pd.to_datetime(df['DueDate'], errors='coerce')
            df['CreatedDate'] = pd.to_datetime(df['CreatedDate'], errors='coerce')
        app_logger.info("Study tasks loaded successfully.")
        return df
    except Exception as e:
        st.error(f"🚨 Error loading study tasks: {e}")
        app_logger.exception("Failed to load study tasks.")
        return pd.DataFrame()

def insert_study_task(conn, task_data):
    """Inserts a new study task entry into the database."""
    if conn is None:
        return False
    try:
        conn.execute("""
            INSERT INTO study_tasks
            (Subject, Topic, DueDate, Priority, Status, Notes, CreatedDate)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, task_data)
        conn.commit()
        app_logger.info(f"Inserted study task: {task_data}")
        return True
    except sqlite3.IntegrityError:
        st.warning("⚠️ A task with this Subject, Topic, and Due Date already exists. Please modify details or delete the existing one.")
        return False
    except sqlite3.Error as e:
        st.error(f"🚨 Error inserting study task: {e}")
        app_logger.exception("Failed to insert study task.")
        return False

def update_study_task(conn, task_id, task_data):
    """Updates an existing study task entry."""
    if conn is None:
        return False
    try:
        conn.execute("""
            UPDATE study_tasks
            SET Subject = ?, Topic = ?, DueDate = ?, Priority = ?,
                Status = ?, Notes = ?
            WHERE ID = ?;
        """, (*task_data, task_id))
        conn.commit()
        app_logger.info(f"Updated study task ID {task_id}")
        return True
    except sqlite3.IntegrityError:
        st.warning("⚠️ An entry with this Subject, Topic, and Due Date already exists. Please choose unique values.")
        return False
    except sqlite3.Error as e:
        st.error(f"🚨 Error updating study task: {e}")
        app_logger.exception("Failed to update study task.")
        return False

def delete_study_task(conn, task_id):
    """Deletes a study task entry by its ID."""
    if conn is None:
        return False
    try:
        conn.execute("DELETE FROM study_tasks WHERE ID = ?", (task_id,))
        conn.commit()
        app_logger.info(f"Deleted study task ID: {task_id}")
        return True
    except sqlite3.Error as e:
        st.error(f"🚨 Error deleting study task: {e}")
        app_logger.exception("Failed to delete study task.")
        return False

# --- Utility Functions ---

def validate_task_inputs(subject, topic, due_date):
    """Performs input validation for study task fields."""
    if not subject.strip():
        st.error("Subject cannot be empty.")
        return False
    if not topic.strip():
        st.error("Topic cannot be empty.")
        return False
    if due_date < date.today():
        st.error("Due Date cannot be in the past.")
        return False
    return True

def clear_caches_and_rerun():
    """Clears Streamlit caches and reruns the app."""
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# --- Streamlit UI ---

st.title("✨ Quantum Study Planner")
st.markdown("Organize your study tasks, track progress, and conquer your academic goals.")

# Get the persistent database connection
conn = get_connection()

# Ensure database table exists
if conn is None or not create_study_tasks_table(conn):
    st.stop() # Stop if connection or table creation fails

# --- Sidebar for Navigation/Quick Actions ---
with st.sidebar:
    st.header("⚡ Quick Actions")
    st.image("https://images.unsplash.com/photo-1543286386-713ed02f1a6b?q=80&w=1770&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_column_width=True, caption="Plan your journey to success!")
    st.info("💡 Tip: Use the tabs to add new tasks, manage existing ones, or view your progress.")
    if st.button("🔄 Refresh All Data", help="Clear data cache and reload all study tasks."):
        clear_caches_and_rerun()
        st.success("Data refreshed!")
    st.markdown("---")
    st.subheader("About This App")
    st.markdown("""
        This Quantum Study Planner helps you meticulously plan and track your study efforts.
        Prioritize tasks, set due dates, and monitor your completion status.
        \n\nDeveloped by Your Name/Team
    """)
    st.markdown(f"Current Time (IST): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# --- Main Content Tabs ---
tab1, tab2, tab3 = st.tabs(["➕ Add New Task", "📚 Manage Tasks", "📈 Study Analytics"])

with tab1:
    st.header("📝 Add a New Study Task")
    st.markdown("Define your next study objective. Precision in planning leads to mastery!")

    with st.form("task_add_form", clear_on_submit=True):
        st.markdown("### Task Details")
        col_subj, col_topic = st.columns(2)
        with col_subj:
            subject = st.selectbox("📚 **Subject**", ["Physics", "Chemistry", "Maths", "Biology", "Computer Science", "General"], help="Choose the subject for this task.")
        with col_topic:
            topic = st.text_input("📖 **Topic/Task Description**", placeholder="e.g., Kinematics - Projectile Motion, Organic Chemistry - Alkanes", help="Briefly describe the study task.")

        col_due, col_prio, col_status = st.columns(3)
        with col_due:
            due_date = st.date_input("🗓️ **Due Date**", date.today() + timedelta(days=7), help="Set the deadline for this task.")
        with col_prio:
            priority = st.selectbox("⚡ **Priority**", ["High", "Medium", "Low"], index=0, help="Assign a priority level.")
        with col_status:
            status = st.selectbox("✅ **Status**", ["Pending", "In Progress", "Completed", "Deferred"], help="Current status of the task.")

        notes = st.text_area("✍️ **Notes** (Optional)", placeholder="Breakdown steps, resources needed, potential challenges...", max_chars=500, help="Add any relevant notes or reflections on this task.")

        st.markdown("---")
        submitted = st.form_submit_button("➕ **Add Study Task**", use_container_width=True, type="primary")

        if submitted:
            if validate_task_inputs(subject, topic, due_date):
                task_row_data = (subject.strip(), topic.strip(), str(due_date),
                                 priority, status, notes.strip(), str(datetime.now().date()))
                if insert_study_task(conn, task_row_data):
                    st.success("🎉 Study task added successfully! Check 'Manage Tasks' tab.")
                    clear_caches_and_rerun()
                # else: warning/error is handled by insert_study_task already
            else:
                st.error("Please correct the input errors above.")

with tab2:
    st.header("📋 Your Study Task Matrix")
    st.markdown("Review, filter, edit, or delete your study tasks. Keep your plan dynamic!")

    df_tasks = load_study_tasks(_conn=conn)

    if df_tasks.empty:
        st.info("No study tasks recorded yet. Let's start planning your first task in the 'Add New Task' tab!")
    else:
        st.subheader("🔍 Filter & Search Options")
        col_filter_subj, col_filter_status, col_search_text = st.columns([1, 1, 2])
        with col_filter_subj:
            selected_subject = st.selectbox("Filter by Subject", ["All"] + df_tasks["Subject"].unique().tolist(), key="filter_subject_task")
        with col_filter_status:
            selected_status = st.selectbox("Filter by Status", ["All"] + df_tasks["Status"].unique().tolist(), key="filter_status_task")
        with col_search_text:
            search_query = st.text_input("Search (Topic, Notes)", placeholder="e.g., calculus, difficult, revise", key="search_query_task")

        filtered_df = df_tasks.copy()
        if selected_subject != "All":
            filtered_df = filtered_df[filtered_df["Subject"] == selected_subject]
        if selected_status != "All":
            filtered_df = filtered_df[filtered_df["Status"] == selected_status]
        if search_query:
            search_query_lower = search_query.lower()
            filtered_df = filtered_df[
                filtered_df.apply(lambda row:
                    search_query_lower in str(row["Topic"]).lower() or
                    search_query_lower in str(row["Notes"]).lower(), axis=1
                )
            ]

        if filtered_df.empty:
            st.warning("No tasks match your current filters. Try adjusting your selections.")
        else:
            st.subheader(f"📊 Displaying {len(filtered_df)} Matching Study Task(s)")
            # Highlight overdue tasks
            current_date = pd.Timestamp(date.today())
            def highlight_overdue(row):
                if row['Status'] != 'Completed' and row['DueDate'] < current_date:
                    return ['background-color: #330000; color: #FF4B4B'] * len(row) # Dark red background for overdue
                return [''] * len(row)

            st.dataframe(filtered_df.set_index("ID").style.apply(highlight_overdue, axis=1), use_container_width=True, height=400)

            st.download_button(
                label="📥 Download Filtered Tasks as CSV",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name=f"study_tasks_filtered_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download the currently filtered study tasks as a CSV file."
            )

            st.markdown("---")
            col_edit, col_delete = st.columns(2)

            with col_edit:
                st.subheader("✏️ Edit a Study Task")
                edit_id_options = filtered_df["ID"].tolist()
                if not edit_id_options:
                    st.info("No entries available for editing under current filters.")
                else:
                    selected_edit_id = st.selectbox("Select ID to Edit", edit_id_options, key="edit_select_id_tab2", help="Choose the ID of the task entry you wish to modify.")
                    if selected_edit_id:
                        entry_to_edit = df_tasks[df_tasks["ID"] == selected_edit_id].iloc[0]
                        with st.form(f"edit_form_{selected_edit_id}"):
                            st.markdown(f"**Editing Task ID: {selected_edit_id}**")
                            e_subject = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "Computer Science", "General"], index=["Physics", "Chemistry", "Maths", "Biology", "Computer Science", "General"].index(entry_to_edit["Subject"]))
                            e_topic = st.text_input("Topic/Task Description", value=entry_to_edit["Topic"])
                            e_due_date = st.date_input("Due Date", value=entry_to_edit["DueDate"].date())
                            e_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(entry_to_edit["Priority"]))
                            e_status = st.selectbox("Status", ["Pending", "In Progress", "Completed", "Deferred"], index=["Pending", "In Progress", "Completed", "Deferred"].index(entry_to_edit["Status"]))
                            e_notes = st.text_area("Notes (opt)", value=entry_to_edit["Notes"], max_chars=500)

                            update_button = st.form_submit_button("🔄 Update Task", type="primary", use_container_width=True)
                            if update_button:
                                if validate_task_inputs(e_subject, e_topic, e_due_date):
                                    updated_data = (e_subject.strip(), e_topic.strip(), str(e_due_date),
                                                    e_priority, e_status, e_notes.strip())
                                    if update_study_task(conn, selected_edit_id, updated_data):
                                        st.success(f"🎉 Task ID {selected_edit_id} updated successfully!")
                                        clear_caches_and_rerun()

            with col_delete:
                st.subheader("🗑️ Delete a Study Task")
                delete_id_options = filtered_df["ID"].tolist()
                if not delete_id_options:
                    st.info("No entries to delete under current filters.")
                else:
                    selected_delete_id = st.selectbox("Select ID to Delete", delete_id_options, key="delete_select_id_tab2", help="Choose the ID of the task entry to remove.")
                    if selected_delete_id:
                        if st.button(f"Permanently Delete Task ID {selected_delete_id}", type="secondary", use_container_width=True):
                            st.warning(f"Are you absolutely sure you want to delete task entry ID {selected_delete_id}? This action cannot be undone.")
                            confirm_delete_btn = st.button("🚨 Confirm Deletion", type="primary", key="confirm_del_btn_task")
                            if confirm_delete_btn:
                                if delete_study_task(conn, selected_delete_id):
                                    st.success(f"🗑️ Task ID {selected_delete_id} deleted.")
                                    clear_caches_and_rerun()

with tab3:
    st.header("📈 Your Study Analytics")
    st.markdown("Visualize your task completion, workload distribution, and upcoming deadlines.")

    df_analytics = load_study_tasks(_conn=conn)

    if df_analytics.empty:
        st.info("No data available for analytics. Please add some study tasks first in the 'Add New Task' tab!")
    else:
        # Ensure DueDate is datetime for plotting
        df_analytics['DueDate'] = pd.to_datetime(df_analytics['DueDate'])

        st.subheader("📊 Overall Task Summary")
        col_total, col_pending, col_completed = st.columns(3)
        with col_total:
            st.metric("Total Tasks", len(df_analytics))
        with col_pending:
            st.metric("Pending Tasks", len(df_analytics[df_analytics["Status"] == "Pending"]))
        with col_completed:
            st.metric("Completed Tasks", len(df_analytics[df_analytics["Status"] == "Completed"]))

        st.markdown("---")
        st.subheader("🎯 Task Status Distribution")
        status_counts = df_analytics["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_status = px.pie(status_counts, values="Count", names="Status", title="Distribution of Task Statuses",
                            color_discrete_sequence=px.colors.qualitative.Dark24,
                            hole=0.4) # Donut chart
        fig_status.update_traces(textinfo='percent+label', pull=[0.05 if s == 'Pending' else 0 for s in status_counts['Status']])
        fig_status.update_layout(title_x=0.5, showlegend=True)
        st.plotly_chart(fig_status, use_container_width=True)

        st.markdown("---")
        st.subheader("📅 Tasks by Due Date (Upcoming & Overdue)")

        # Filter for relevant tasks for trend/upcoming
        df_upcoming = df_analytics[df_analytics["Status"] != "Completed"].copy()
        if not df_upcoming.empty:
            df_upcoming['DaysUntilDue'] = (df_upcoming['DueDate'] - pd.Timestamp(date.today())).dt.days

            # Create a combined 'Topic (Subject)' column for better hover info
            df_upcoming['TaskDisplay'] = df_upcoming['Topic'] + " (" + df_upcoming['Subject'] + ")"

            fig_due_date = px.scatter(df_upcoming, x='DueDate', y='Priority',
                                      color='Status', size='DaysUntilDue',
                                      hover_name='TaskDisplay',
                                      hover_data={'Priority': False, 'DaysUntilDue': True, 'Status': False, 'Subject': True, 'Notes': True},
                                      title='Tasks by Due Date and Priority',
                                      labels={'DueDate': 'Due Date', 'Priority': 'Priority Level'},
                                      color_discrete_map={
                                          "Pending": "#FF4B4B", # Red for pending
                                          "In Progress": "#FFD700", # Yellow for in progress
                                          "Deferred": "#A0A0B0" # Grey for deferred
                                      })

            # Map priority levels to numerical for Y-axis sorting/display if desired
            priority_order = {"High": 3, "Medium": 2, "Low": 1}
            df_upcoming['PriorityNumerical'] = df_upcoming['Priority'].map(priority_order)
            fig_due_date.update_yaxes(categoryorder='array', categoryarray=["Low", "Medium", "High"], title_text="Priority")
            fig_due_date.update_layout(title_x=0.5)
            st.plotly_chart(fig_due_date, use_container_width=True)
        else:
            st.info("No pending, in-progress, or deferred tasks to display in the due date analysis.")

        st.markdown("---")
        st.subheader("📚 Tasks per Subject")
        subject_counts = df_analytics["Subject"].value_counts().reset_index()
        subject_counts.columns = ["Subject", "Count"]

        fig_subject_tasks = px.bar(subject_counts, x='Subject', y='Count',
                                   title='Number of Tasks Per Subject',
                                   labels={'Count': 'Number of Tasks'},
                                   color='Count', color_continuous_scale=px.colors.sequential.Plasma)
        fig_subject_tasks.update_layout(title_x=0.5)
        st.plotly_chart(fig_subject_tasks, use_container_width=True)