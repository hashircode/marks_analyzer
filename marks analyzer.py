import pandas as pd
import streamlit as st

PASS_MARK = 50.0 

if 'df' not in st.session_state:
    df_init = pd.DataFrame(columns=["Name", "Math", "Science", "English"])

    df_init["Math"] = df_init["Math"].astype(float)
    df_init["Science"] = df_init["Science"].astype(float)
    df_init["English"] = df_init["English"].astype(float)
    st.session_state.df = df_init


def add_marks(name, math, science, english):

    new_row = pd.DataFrame([[name, float(math), float(science), float(english)]], 
                           columns=["Name", "Math", "Science", "English"])
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

def view_marks():
    return st.session_state.df

def analyze_marks():

    df = st.session_state.df.copy()
    
    if df.empty:
        return "No data to analyze."
    
    numerical_cols = ["Math", "Science", "English"]
    for col in numerical_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Total'] = df[numerical_cols].sum(axis=1)

    analysis = {
        "Math Average": df['Math'].mean(),
        "Science Average": df['Science'].mean(),
        "English Average": df['English'].mean(),
        "Highest Math Marks": f"{df['Math'].max()} by {df.loc[df['Math'].idxmax()]['Name']}",
        "Highest Science Marks": f"{df['Science'].max()} by {df.loc[df['Science'].idxmax()]['Name']}",
        "Highest English Marks": f"{df['English'].max()} by {df.loc[df['English'].idxmax()]['Name']}",
        "df_for_viz": df
    }
    return analysis

def create_visuals_streamlit(analysis_data):
    avg_data = pd.DataFrame({
        'Subject': ['Math', 'Science', 'English'],
        'Average Mark': [
            analysis_data["Math Average"],
            analysis_data["Science Average"],
            analysis_data["English Average"]
        ]
    })
    
    st.subheader("Subject Average Marks")
    st.bar_chart(avg_data, x='Subject', y='Average Mark')

    df_viz = analysis_data["df_for_viz"].sort_values(by='Total', ascending=False)
    
    st.subheader("Student Total Marks Comparison")
    df_viz_total = df_viz[['Name', 'Total']].set_index('Name')
    st.bar_chart(df_viz_total)

def main():
    
    st.title("🎓 Marks Analyzer")
    st.markdown("### Analyze student marks with ease")

    menu = ["📝 Add Marks", "📊 View Marks", "📈 Analyze Marks", "❌ Delete Marks"]
    choice = st.selectbox("Select an option", menu)
    
    if choice == "📝 Add Marks":
        with st.form("add_marks"):
            st.markdown("### Add Student Marks")
            name = st.text_input("Enter student's name")
            col1, col2, col3 = st.columns(3)
            math = col1.number_input("Math marks", min_value=0.0, step=0.1)
            science = col2.number_input("Science marks", min_value=0.0, step=0.1)
            english = col3.number_input("English marks", min_value=0.0, step=0.1)


            submitted = st.form_submit_button("Add")
            if submitted:
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
            
            st.markdown("### Visual Data Analysis (Streamlit/Pandas)")
            create_visuals_streamlit(analysis)

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
                
                st.warning(f"Are you sure you want to permanently delete ALL records for **{student_to_delete}**?")
                
                submitted = st.form_submit_button("❌ Confirm Delete")
                
                if submitted:
                    initial_rows = st.session_state.df.shape[0]
                    st.session_state.df = st.session_state.df[st.session_state.df['Name'] != student_to_delete].reset_index(drop=True)
                    final_rows = st.session_state.df.shape[0]
                    
                    if initial_rows > final_rows:
                        st.success(f"Successfully deleted {initial_rows - final_rows} entry/entries for **{student_to_delete}**.")
        
                        st.rerun() 
                    else:
                        st.error(f"Failed to delete entries for {student_to_delete}.")


if __name__ == "__main__":
    main()
