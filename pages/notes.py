# notes.py (Modified)
import streamlit as st
import pandas as pd
from utils import load_data, save_data # Crucial: utils.py must be present

def main_notes_app(): # <-- Add this function definition
    st.title("📒 Notes Manager")

    NOTES_FILE = "notes.csv"
    # Ensure utils.py with load_data and save_data is in the same directory
    # If notes.csv doesn't exist, load_data should handle it (e.g., return an empty DataFrame)
    try:
        notes_df = load_data(NOTES_FILE)
    except FileNotFoundError:
        st.warning("Notes file (notes.csv) not found. A new one will be created upon saving notes.")
        notes_df = pd.DataFrame(columns=["Subject", "Topic", "Content"]) # Start with empty if file not found
    except Exception as e:
        st.error(f"Error loading notes: {e}. Please ensure utils.py and notes.csv are valid.")
        notes_df = pd.DataFrame(columns=["Subject", "Topic", "Content"]) # Fallback

    with st.form("Add Note"):
        subject = st.selectbox("Subject", ["Physics", "Chemistry", "Math", "Biology"])
        topic = st.text_input("Topic")
        content = st.text_area("Note")
        if st.form_submit_button("Save Note"):
            # Use pd.concat for appending in newer pandas versions
            new_note_df = pd.DataFrame([{"Subject": subject, "Topic": topic, "Content": content}])
            notes_df = pd.concat([notes_df, new_note_df], ignore_index=True)
            save_data(notes_df, NOTES_FILE)
            st.success("Note saved.")
            st.rerun() # Rerun to show updated dataframe

    st.markdown("### All Notes")
    st.dataframe(notes_df)

if __name__ == "__main__":
    main_notes_app() # This allows notes.py to still be run standalone