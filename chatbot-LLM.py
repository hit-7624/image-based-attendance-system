import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
import sys
import glob

def load_data(file_path, sname):
    """Loads data from a specific sheet in the specified Excel file."""
    df = pd.read_excel(file_path, sheet_name=sname)
    df = df.astype(str)
    return df


def make_data(df):
    """Converts the DataFrame to a string format suitable for the LLM prompt."""
#    print(df.to_string(index=False, header=True))
    return df.to_string(index=False, header=True)

def ask_groq(client, data_context, query):
    """Sends the query and data context to the Groq API and returns the answer."""
    system_prompt = f"""You are an assistant that answers questions based ONLY on the provided data from a specific Excel sheet representing a subject's attendance.
The data represents student attendance for a specific subject/sheet.
- The first column is 'Roll Number'.
- Each subsequent column header represents a specific date (e.g., '19-4-25', '20/4/25').
- The values in the date columns indicate the attendance status for the corresponding 'Roll Number' on that specific date (e.g., 'Present', 'Absent', 'P', 'A', or blank).
Here is the data from the selected sheet:
{data_context}
Answer the user's query using ONLY this data. Do not make up information or use external knowledge.
Respond in a concise, human-readable format.
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return "Sorry, I encountered an error trying to process your request with the Groq API."


def main():
    # --- Configuration ---
    load_dotenv()
    groq_api_key = os.environ.get("GROQ_API_KEY")
    attendance_folder = "attendance_data"

    if not groq_api_key:
        print("Error: GROQ_API_KEY not found.")
        sys.exit(1)

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        sys.exit(1)

    search_path = os.path.join(attendance_folder, '*.xlsx')
    excel_files = glob.glob(search_path)

    print("\nAvailable Subjects (Excel Files):")
    for i, file_path in enumerate(excel_files):
        print(f"{i + 1}. {os.path.basename(file_path)}")

    while True:
        choice_str = input(f"Enter the NUMBER of the subject file: ")
        if choice_str.lower() == 'quit':
             print("\nExiting.")
             sys.exit(0)
        if choice_str.isdigit():
            si = int(choice_str) - 1
            if 0 <= si < len(excel_files):
                spath = excel_files[si]
                break


    # print({os.path.basename(spath)})
    print(f"\nSelected subject file: '{os.path.basename(spath)}'")

    sname = "Sheet1"

    # --- Load Data ---
    print(f"Loading data from file '{os.path.basename(spath)}', sheet '{sname}'...")
    data_df = load_data(spath, sname)

    data_context = make_data(data_df)
    print("data loaded successfully.")

    # --- Interaction Loop ---
    print(f"\nchatbot initialized for Subject: '{os.path.basename(spath)}', Sheet: '{sname}'.")
    print("ask questions about attendance. Type 'quit' to exit.")

    while True:
        query = input("Query: ")



        if query.lower() == 'quit':
            print("Exiting.")
            break



        print("Processing query...")
        answer = ask_groq(client, data_context, query)
        print(f"\nAnswer: {answer}\n")

if __name__ == "__main__":
    main()
