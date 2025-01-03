import streamlit as st
import mysql.connector
import pandas as pd
import re


# Function to establish database connection
def connect_to_database():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Vinoth@2001",
            database="orders",
            autocommit=True
        )
        mycursor = mydb.cursor(dictionary=True)
        return mydb, mycursor
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None, None


# Function to parse the SQL file and extract questions and queries
def parse_sql_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        queries = []
        current_question = None
        current_query_lines = []

        # Regex to identify question lines like "#1.", "#2.", etc.
        question_pattern = re.compile(r"^#(\d+)\.\s*(.*)$")

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                # This might be a new question line
                match = question_pattern.match(line)
                if match:
                    # If we have a current question and lines, store the previous one
                    if current_question and current_query_lines:
                        queries.append((current_question, "\n".join(current_query_lines).strip()))
                        current_query_lines = []

                    # Start a new question
                    question_number = match.group(1)
                    question_text = match.group(2).strip()
                    current_question = f"#{question_number}. {question_text}"
                else:
                    # It's a comment line but not a question marker, just ignore
                    pass
            else:
                # If we are currently tracking a question, these lines belong to the query
                if current_question is not None:
                    if line:  # Only add non-empty lines
                        current_query_lines.append(line)

        # After the loop ends, if there's a remaining question and query lines, add them too
        if current_question and current_query_lines:
            queries.append((current_question, "\n".join(current_query_lines).strip()))

        return queries

    except FileNotFoundError:
        st.error("SQL file not found. Please check the file path.")
        return []
    except Exception as e:
        st.error(f"An error occurred while loading the SQL file: {e}")
        return []


# Function to execute a single query and display results
def execute_query(query, mycursor):
    try:
        with st.spinner("Executing query..."):
            mycursor.execute(query)
            if query.strip().lower().startswith("select"):
                results = mycursor.fetchall()
                if results:
                    df = pd.DataFrame(results)
                    st.dataframe(df)
                else:
                    st.info("The query executed successfully but returned no results.")
            else:
                st.success("Query executed successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error executing query: {err}")


# Main function to run the Streamlit app
def main():
    st.title("Retail Orders Query Runner")

    # Establish database connection
    mydb, mycursor = connect_to_database()

    # Hardcoded file paths for demonstration
    file_paths_list = [
        r"C:\Users\vinuv\Documents\Retailorders 1 to 10 MYSQL.sql",
        r"C:\Users\vinuv\Documents\Retailorders 11 to 20 MYSQL.sql"
    ]

    # Display file paths in a selectbox for the user to choose one
    selected_file_path = st.selectbox(
        "Select a SQL file to load queries from:",
        options=file_paths_list
    )

    # Parse the SQL file and get the list of questions and queries
    queries = parse_sql_file(selected_file_path)

    # If there are questions in the SQL file
    if queries:
        # Display questions in a selectbox for the user to choose one
        st.subheader("Select a Question to Execute")
        question_texts = [q[0] for q in queries]  # Extract just the question text
        selected_question = st.selectbox(
            "Available Questions:",
            options=question_texts
        )

        # Find the query associated with the selected question
        selected_query = None
        for q in queries:
            if q[0] == selected_question:
                selected_query = q[1]
                break

        # Button to execute the selected query
        if selected_query and st.button("Run Selected Query"):
            if mydb and mycursor:
                st.subheader("Query Results")
                execute_query(selected_query, mycursor)
            else:
                st.error("Database connection is not available.")


# Entry point of the Streamlit app
if __name__ == "__main__":
    main()
