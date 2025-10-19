import pandas as pd
import streamlit as st

PASS_MARK = 50.0
MAX_MARKS_PER_SUBJECT = 100.0
SUBJECTS = ["Math", "Science", "English", "History", "Art"]
MAX_TOTAL_MARKS = len(SUBJECTS) * MAX_MARKS_PER_SUBJECT

def get_grade(total_marks):
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

if 'df' not in st.session_state:
    df_init = pd.DataFrame(columns=["Name"] + SUBJECTS)
    for subject in SUBJECTS:
        df_init[subject] = df_init[subject].astype(float)
    st.session_state.df = df_init

def add_marks(name, math, science, english, history, art):
    new_row = pd.DataFrame([[name, float(math), float(science), float(english), float(history), float(art)]],
                           columns=["Name"] + SUBJECTS)
    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)

def view_marks():
    return st.session_state.df

def analyze_marks():
    df = st.session_state.df.copy()

    if df.empty:
        return "No data to analyze."

    numerical_cols = SUBJECTS

    df['Total'] = df[numerical_cols].sum(axis=1)

    df['Grade'] = df['Total'].apply(get_grade)

    pass_condition = True
    analysis = {}

    for subject in SUBJECTS:
        df[f'{subject} Status'] = df[subject].apply(lambda x: 'Pass' if x >= PASS_MARK else 'Fail')
        pass_condition = pass_condition & (df[subject] >= PASS_MARK)

    df['Overall Status'] = 'Overall Fail'
    df.loc[pass_condition, 'Overall Status'] = 'Overall Pass'

    pass_fail_counts = df['Overall Status'].value_counts().reindex(['Overall Pass', 'Overall Fail'], fill_value=0)

    analysis["Overall Pass Count"] = pass_fail_counts.get('Overall Pass', 0)
    analysis["Overall Fail Count"] = pass_fail_counts.get('Overall Fail', 0)
    analysis["df_for_viz"] = df.sort_values(by='Total', ascending=False)

    return analysis

def create_visuals_streamlit(analysis_data):

    df_viz = analysis_data["df_for_viz"]

    st.subheader(f"🏆 Student Total Marks (Out of {MAX_TOTAL_MARKS}) & Grade Breakdown")
    df_breakdown = df_viz[['Name', 'Total', 'Grade']].set_index('Name')
    st.dataframe(df_breakdown, use_container_width=True)
    st.bar_chart(df_breakdown['Total'])

    pass_fail_data = pd.DataFrame({
        'Status': ['Overall Pass', 'Overall Fail'],
        'Count': [analysis_data["Overall Pass Count"], analysis_data["Overall Fail Count"]]
    })

    st.subheader(f"✅❌ Overall Pass/Fail (Pass Mark: {PASS_MARK})")
    st.bar_chart(pass_fail_data, x='Status', y='Count')

def main():

    st.title("🎓 Student Marks Analyzer (5 Subjects)")
    st.markdown("### Manage, analyze, and visualize student performance data for five subjects.")

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

    if choice == "📝 Add Marks":
        with st.form("add_marks"):
            st.markdown("### Add Student Marks")
            name = st.text_input("Enter student's name")

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

    elif choice == "📊 View Marks":
        st.markdown("### Student Marks Table")
        df_view = view_marks().copy()

        if not df_view.empty:
            df_analyzed = analyze_marks()['df_for_viz'].copy()
            df_display = df_analyzed[['Name'] + SUBJECTS + ['Total', 'Grade', 'Overall Status']]
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("The marks table is currently empty.")

    elif choice == "📈 Analyze Marks":
        analysis = analyze_marks()

        if isinstance(analysis, str):
            st.warning(analysis)
        else:
            st.markdown(f"### Overall Pass/Fail Counts")
            col_pass, col_fail = st.columns(2)
            col_pass.metric("Students Overall Passed", f"{analysis['Overall Pass Count']}")
            col_fail.metric("Students Overall Failed", f"{analysis['Overall Fail Count']}")

            st.markdown("---")

            st.markdown("### Visual Data Analysis")
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

                st.error(f"⚠️ Are you sure you want to permanently delete ALL records for **{student_to_delete}**?")

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