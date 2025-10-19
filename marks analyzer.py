import pandas as pd
import streamlit as st
# Removed: import numpy as np

# --- Configuration Constants ---
PASS_MARK = 50.0 
MAX_MARKS_PER_SUBJECT = 100.0
SUBJECTS = ["Math", "Science", "English", "History", "Art"]
MAX_TOTAL_MARKS = len(SUBJECTS) * MAX_MARKS_PER_SUBJECT # 500

# Define grade boundaries for Total marks (out of 500)
def get_grade(total_marks):
    """Assigns a letter grade based on total marks out of 500."""
    # New Grading Scale based on 500 max:
    # A=84%+, B=70%+, C=50%+, D=30%+
    if total_marks >= 420: 
        return 'A'
    elif total_marks >= 350: 
        return 'B'
    elif total_marks >= 250: 
        return 'C'
    elif total_marks >= 150: 
        return 'D'
    else:
        return 'F'

# --- Streamlit Session State Initialization ---
if 'df' not in st.session_state:
    df_init = pd.DataFrame(columns=["Name"] + SUBJECTS)

    # Ensure all subject columns are correctly typed for calculations
    for subject in SUBJECTS:
        df_init[subject] = df_init[subject].astype(float)
        
    st.session_state.df = df_init

# --- Core Pandas Logic Functions ---
def add_marks(name, math, science, english, history, art):
    """Adds a new student's marks to the DataFrame using pd.concat."""
    new_row = pd.DataFrame([[name, float(math), float(science), float(english), float(history), float(art)]], 
                           columns=["Name"] + SUBJECTS)
    # Use pd.concat for efficient row addition
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

def view_marks():
    """Returns the current marks DataFrame from session state."""
    return st.session_state.df 

def analyze_marks():
    """
    Performs data analysis using core Pandas functionalities.
    Focuses only on Total, Grade, and Overall Pass/Fail Status.
    Key statistics and top performers have been removed per user request.
    """
    df = st.session_state.df.copy()
    
    if df.empty:
        return "No data to analyze."
    
    numerical_cols = SUBJECTS
    
    # Calculate Total Marks (summing across rows)
    df['Total'] = df[numerical_cols].sum(axis=1)

    # Calculate Grades and Pass/Fail status
    df['Grade'] = df['Total'].apply(get_grade)
    
    # Initialize condition for overall pass
    pass_condition = True
    analysis = {}
    
    for subject in SUBJECTS:
        # Subject Pass/Fail status using Pandas Series.apply with a lambda
        df[f'{subject} Status'] = df[subject].apply(lambda x: 'Pass' if x >= PASS_MARK else 'Fail')
        
        # Update overall pass condition
        pass_condition = pass_condition & (df[subject] >= PASS_MARK)
        
        # Removed: Subject average and top performer analysis
    
    # Overall Pass/Fail (Pass only if ALL subjects are >= PASS_MARK)
    # 1. Initialize all to 'Overall Fail'
    df['Overall Status'] = 'Overall Fail'
    
    # 2. Use .loc with boolean masking to set 'Overall Pass'
    df.loc[pass_condition, 'Overall Status'] = 'Overall Pass'
    
    # Calculate Pass/Fail counts for the visual
    pass_fail_counts = df['Overall Status'].value_counts().reindex(['Overall Pass', 'Overall Fail'], fill_value=0)

    analysis["Overall Pass Count"] = pass_fail_counts.get('Overall Pass', 0)
    analysis["Overall Fail Count"] = pass_fail_counts.get('Overall Fail', 0)
    analysis["df_for_viz"] = df.sort_values(by='Total', ascending=False)
    
    return analysis

def create_visuals_streamlit(analysis_data):
    """
    Creates visualisations using Streamlit's built-in charting features.
    The Subject Average Bar Chart has been removed.
    """
    
    # Removed: 1. Subject Average Bar Chart
    
    # 1. Student Total Marks Comparison Bar Chart
    df_viz = analysis_data["df_for_viz"]
    
    st.subheader(f"🏆 Student Total Marks (Out of {MAX_TOTAL_MARKS}) & Grade Breakdown")
    # Display table showing Name, Total, and Grade
    df_breakdown = df_viz[['Name', 'Total', 'Grade']].set_index('Name')
    st.dataframe(df_breakdown, use_container_width=True)
    # Chart only the total marks
    st.bar_chart(df_breakdown['Total'])
    
    # 2. Pass/Fail Visual
    pass_fail_data = pd.DataFrame({
        'Status': ['Overall Pass', 'Overall Fail'],
        'Count': [analysis_data["Overall Pass Count"], analysis_data["Overall Fail Count"]]
    })
    
    st.subheader(f"✅❌ Overall Pass/Fail (Pass Mark: {PASS_MARK})")
    st.bar_chart(pass_fail_data, x='Status', y='Count')


# --- Streamlit Application Layout (Main) ---
def main():
    
    st.title("🎓 Student Marks Analyzer (5 Subjects)")
    st.markdown("### Manage, analyze, and visualize student performance data for five subjects.")

    # Sidebar Configuration for clarity
    st.sidebar.title("Configuration")
    st.sidebar.info(f"**Subjects:** {', '.join(SUBJECTS)}")
    st.sidebar.info(f"**Pass Mark:** {PASS_MARK:.0f} / {MAX_MARKS_PER_SUBJECT:.0f}")
    st.sidebar.markdown(f"""
        **Grade Scale (Out of {MAX_TOTAL_MARKS} Total):**
        * A: 420+ (84%+)
        * B: 350-419 (70%+)
        * C: 250-349 (50%+)
        * D: 150-249 (30%+)
        * F: <150
    """)

    menu = ["📝 Add Marks", "📊 View Marks", "📈 Analyze Marks", "❌ Delete Marks"]
    choice = st.selectbox("Select an option", menu)
    
    # --- Add Marks Section ---
    if choice == "📝 Add Marks":
        with st.form("add_marks"):
            st.markdown("### Add Student Marks")
            name = st.text_input("Enter student's name")
            
            # Use columns for a cleaner input layout for 5 subjects
            st.markdown("##### Core Subjects")
            col1, col2, col3 = st.columns(3)
            math = col1.number_input("Math", min_value=0.0, max_value=MAX_MARKS_PER_SUBJECT, step=0.1)
            science = col2.number_input("Science", min_value=0.0, max_value=MAX_MARKS_PER_SUBJECT, step=0.1)
            english = col3.number_input("English", min_value=0.0, max_value=MAX_MARKS_PER_SUBJECT, step=0.1)
            
            st.markdown("##### Additional Subjects")
            col4, col5 = st.columns(2)
            history = col4.number_input("History", min_value=0.0, max_value=MAX_MARKS_PER_SUBJECT, step=0.1)
            art = col5.number_input("Art", min_value=0.0, max_value=MAX_MARKS_PER_SUBJECT, step=0.1)


            submitted = st.form_submit_button("Add Marks")
            if submitted:
                if name.strip() == "":
                    st.error("Please enter a student name.")
                else:
                    add_marks(name.strip(), math, science, english, history, art)
                    st.success(f"Marks for **{name}** added successfully.")
    
    # --- View Marks Section ---
    elif choice == "📊 View Marks":
        st.markdown("### Student Marks Table")
        df_view = view_marks().copy()
        
        if not df_view.empty:
            # Re-run analysis to show current grades/status in the view table
            df_analyzed = analyze_marks()['df_for_viz'].copy()
            # Select and reorder columns for display
            df_display = df_analyzed[['Name'] + SUBJECTS + ['Total', 'Grade', 'Overall Status']]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("The marks table is currently empty.")
    
    # --- Analyze Marks Section ---
    elif choice == "📈 Analyze Marks":
        analysis = analyze_marks()
        
        if isinstance(analysis, str):
            st.warning(analysis)
        else:
            # Removed: Key Statistics (Averages) and Top Performers sections

            # Display Pass/Fail Counts (Only key metrics left)
            st.markdown(f"### Overall Pass/Fail Counts")
            col_pass, col_fail = st.columns(2)
            col_pass.metric("Students Overall Passed", f"{analysis['Overall Pass Count']}")
            col_fail.metric("Students Overall Failed", f"{analysis['Overall Fail Count']}")
            
            st.markdown("---")
            
            # Display Visuals
            st.markdown("### Visual Data Analysis")
            create_visuals_streamlit(analysis)

    # --- Delete Marks Section ---
    elif choice == "❌ Delete Marks":
        st.markdown("### Delete Student Marks")
        
        df = view_marks()
        
        if df.empty:
            st.warning("No students currently registered to delete.")
        else:
            student_names = df['Name'].unique().tolist()
            
            with st.form("delete_form"):
                st.write("Current Marks:")
                st.dataframe(df, use_container_width=True)

                student_to_delete = st.selectbox("Select student whose entries you want to delete:", student_names)
                
                st.error(f"⚠️ Are you sure you want to permanently delete ALL records for **{student_to_delete}**?")
                
                submitted = st.form_submit_button("❌ Confirm Delete")
                
                if submitted:
                    initial_rows = st.session_state.df.shape[0]
                    # Pandas boolean indexing to filter out the row to be deleted
                    st.session_state.df = st.session_state.df[st.session_state.df['Name'] != student_to_delete].reset_index(drop=True)
                    final_rows = st.session_state.df.shape[0]
                    
                    if initial_rows > final_rows:
                        st.success(f"Successfully deleted {initial_rows - final_rows} entry/entries for **{student_to_delete}**.")
                        st.rerun() 
                    else:
                        st.error(f"Failed to delete entries for {student_to_delete}.")


if __name__ == "__main__":
    main()
