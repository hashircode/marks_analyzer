import pandas as pd
import streamlit as st

# --- Constants ---
PASS_MARK = 50.0 # This constant is no longer used for visuals, but kept for future use if needed.

# --- Initialization and Data Persistence ---

# Use st.session_state for data persistence (crucial for Streamlit apps)
if 'df' not in st.session_state:
    df_init = pd.DataFrame(columns=["Name", "Math", "Science", "English"])
    # Ensure numerical columns are correctly typed
    df_init["Math"] = df_init["Math"].astype(float)
    df_init["Science"] = df_init["Science"].astype(float)
    df_init["English"] = df_init["English"].astype(float)
    st.session_state.df = df_init


def add_marks(name, math, science, english):
    # Use st.session_state.df
    # Ensure inputs are converted to the correct type for the DataFrame
    new_row = pd.DataFrame([[name, float(math), float(science), float(english)]], 
                           columns=["Name", "Math", "Science", "English"])
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

def view_marks():
    # Use st.session_state.df
    return st.session_state.df

def analyze_marks():
    # Use st.session_state.df
    df = st.session_state.df.copy()
    
    if df.empty:
        return "No data to analyze."
    
    # Ensure numerical columns are correctly typed before calculation
    numerical_cols = ["Math", "Science", "English"]
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate Total Marks for student comparison
    df['Total'] = df[numerical_cols].sum(axis=1)

    analysis = {
        # Averages
        "Math Average": df['Math'].mean(),
        "Science Average": df['Science'].mean(),
        "English Average": df['English'].mean(),
        # Highest Scores
        "Highest Math Marks": f"{df['Math'].max()} by {df.loc[df['Math'].idxmax()]['Name']}",
        "Highest Science Marks": f"{df['Science'].max()} by {df.loc[df['Science'].idxmax()]['Name']}",
        "Highest English Marks": f"{df['English'].max()} by {df.loc[df['English'].idxmax()]['Name']}",
        # DataFrame for visualizations
        "df_for_viz": df
    }
    return analysis

def create_visuals_streamlit(analysis_data):
    # 1. Subject Average Comparison Bar Chart (KEPT)
    avg_data = pd.DataFrame({
        'Subject': ['Math', 'Science', 'English'],
        'Average Mark': [
            analysis_data["Math Average"],
            analysis_data["Science Average"],
            analysis_data["English Average"]
        ]
    })
    
    st.subheader("Subject Average Marks")
    # Streamlit's built-in bar chart
    st.bar_chart(avg_data, x='Subject', y='Average Mark')

    # 2. Student Total Marks Comparison Bar Chart (KEPT)
    df_viz = analysis_data["df_for_viz"].sort_values(by='Total', ascending=False)
    
    st.subheader("Student Total Marks Comparison")
    # Use Streamlit's built-in bar chart on the Total column
    # We must set the index to 'Name' for the chart to use it as the X-axis
    df_viz_total = df_viz[['Name', 'Total']].set_index('Name')
    st.bar_chart(df_viz_total)

# The create_percentage_visuals function has been removed.


def main():
    
    st.title("🎓 Marks Analyzer")
    st.markdown("### Analyze student marks with ease")

    # Added "❌ Delete Marks" to the menu
    menu = ["📝 Add Marks", "📊 View Marks", "📈 Analyze Marks", "❌ Delete Marks"]
    choice = st.selectbox("Select an option", menu)
    
    if choice == "📝 Add Marks":
        with st.form("add_marks"):
            st.markdown("### Add Student Marks")
            name = st.text_input("Enter student's name")
            # --- Subject Marks Entry Fields ---
            col1, col2, col3 = st.columns(3)
            math = col1.number_input("Math marks", min_value=0.0, step=0.1)
            science = col2.number_input("Science marks", min_value=0.0, step=0.1)
            english = col3.number_input("English marks", min_value=0.0, step=0.1)
            # --- End Subject Marks Entry Fields ---

            submitted = st.form_submit_button("Add")
            if submitted:
                # Basic validation
                if name.strip() == "":
                    st.error("Please enter a student name.")
                else:
                    add_marks(name.strip(), math, science, english)
                    st.success(f"Marks for **{name}** added successfully.")
    
    elif choice == "📊 View Marks":
        st.markdown("### Student Marks Table")
        st.dataframe(view_marks(), use_container_width=True)
    
    elif choice == "📈 Analyze Marks":
        analysis = analyze_marks()
        
        if isinstance(analysis, str):
            st.warning(analysis)
        else:
            st.markdown("### Key Statistics")
            
            # Display Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Math Average", f"{analysis['Math Average']:.2f}")
            col2.metric("Science Average", f"{analysis['Science Average']:.2f}")
            col3.metric("English Average", f"{analysis['English Average']:.2f}")
            
            st.markdown("---")
            st.markdown("### Top Performers")
            st.info(f"**Highest Math Marks:** {analysis['Highest Math Marks']}")
            st.info(f"**Highest Science Marks:** {analysis['Highest Science Marks']}")
            st.info(f"**Highest English Marks:** {analysis['Highest English Marks']}")
            
            st.markdown("---")
            
            # Only the main visual function remains
            st.markdown("### Visual Data Analysis (Streamlit/Pandas)")
            create_visuals_streamlit(analysis)

    # --- DELETE OPTION ---
    elif choice == "❌ Delete Marks":
        st.markdown("### Delete Student Marks")
        
        df = view_marks()
        
        if df.empty:
            st.warning("No students currently registered to delete.")
        else:
            # Use unique names for the selection box
            student_names = df['Name'].unique().tolist()
            
            with st.form("delete_form"):
                st.write("Current Marks:")
                st.dataframe(df, use_container_width=True)

                student_to_delete = st.selectbox("Select student whose entries you want to delete:", student_names)
                
                # Warning before deletion
                st.warning(f"Are you sure you want to permanently delete ALL records for **{student_to_delete}**?")
                
                submitted = st.form_submit_button("❌ Confirm Delete")
                
                if submitted:
                    # Deletion logic: Filter out all rows where 'Name' matches the selection
                    initial_rows = st.session_state.df.shape[0]
                    st.session_state.df = st.session_state.df[st.session_state.df['Name'] != student_to_delete].reset_index(drop=True)
                    final_rows = st.session_state.df.shape[0]
                    
                    if initial_rows > final_rows:
                        st.success(f"Successfully deleted {initial_rows - final_rows} entry/entries for **{student_to_delete}**.")
                        # Rerun the script to update the display immediately
                        st.rerun() 
                    else:
                        st.error(f"Failed to delete entries for {student_to_delete}.")


if __name__ == "__main__":
    main()
