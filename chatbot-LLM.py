import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv
import sys
import glob
import re
from pyfiglet import Figlet

# ANSI Color Codes
COLORS = [
    "\033[91m", # Red
    "\033[92m", # Green
    "\033[93m", # Yellow
    "\033[94m", # Blue
    "\033[95m", # Magenta
    "\033[96m", # Cyan
    "\033[97m", # White
]
RESET = "\033[0m"

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
    system_prompt = f"""You are an assistant that answers questions based ONLY on the provided data from a specific Excel sheet representing a subject's attendance.
The data represents student attendance for a specific subject/sheet.
- The first column is 'Roll Number'.
- Each subsequent column header represents a specific date (e.g., '19-04-2025', '20-04-2025').
- The values in the date columns indicate the attendance status for the corresponding 'Roll Number' on that specific date (e.g., 'Present', 'Absent', 'P', 'A', or blank).
Here is the data from the selected sheet:
{data_context}
Answer the user's query using ONLY this data. Do not make up information or use external knowledge.
and if query is like aggegation of data, then answer in a concise, human-readable format.
and answer in a way that is easy to understand for a non-technical audience.
and hide internal calulation from user.
and always think before answering the question.
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
            model="deepseek-r1-distill-llama-70b",
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

    # --- Print Banner ---
    f = Figlet(font='slant')
    print(f"{COLORS[3]}{f.renderText('C H A T B O T')}{RESET}") # Blue Banner
    print(f"{COLORS[2]}{'-' * 50}{RESET}") # Yellow Separator

    if not groq_api_key:
        print(f"{COLORS[0]}Error: GROQ_API_KEY not found.{RESET}") # Red Error
        sys.exit(1)

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"{COLORS[0]}Failed to initialize Groq client: {e}{RESET}") # Red Error
        sys.exit(1)

    search_path = os.path.join(attendance_folder, '*.xlsx')
    excel_files = glob.glob(search_path)

    if not excel_files:
        print(f"{COLORS[0]}Error: No Excel files found in the '{attendance_folder}' directory.{RESET}") # Red Error
        sys.exit(1)

    print(f"\n{COLORS[5]}Available Subjects (Excel Files):{RESET}") # Cyan Header
    for i, file_path in enumerate(excel_files):
        color = COLORS[i % len(COLORS)] # Cycle through colors
        base_name = os.path.basename(file_path)
        subject_name = os.path.splitext(base_name)[0] # Remove .xlsx
        print(f"{color}{i + 1}{RESET}. {subject_name}")

    while True:
        choice_str = input(f"Enter the NUMBER of the subject file: ")
        if choice_str.lower() == 'quit':
             print(f"\n{COLORS[6]}Exiting.{RESET}") # White Exit message
             sys.exit(0)
        if choice_str.isdigit():
            si = int(choice_str) - 1
            if 0 <= si < len(excel_files):
                spath = excel_files[si]
                break

    selected_base_name = os.path.basename(spath)
    selected_subject_name = os.path.splitext(selected_base_name)[0]

    print(f"\n{COLORS[4]}Selected subject file: {COLORS[2]}'{selected_subject_name}'{RESET}") # Magenta msg, Yellow filename

    sname = "Sheet1"

    # --- Load Data ---
    print(f"{COLORS[6]}Loading data from file {COLORS[2]}'{selected_subject_name}'{COLORS[6]}, sheet {COLORS[2]}'{sname}'{COLORS[6]}...{RESET}") # White msg, Yellow filename/sheet
    data_df = load_data(spath, sname)

    data_context = make_data(data_df)
    print(f"{COLORS[1]}data loaded successfully.{RESET}") # Green Success message

    # --- Interaction Loop ---
    print(f"\n{COLORS[5]}chatbot initialized for Subject: {COLORS[2]}'{selected_subject_name}'{COLORS[5]}, Sheet: {COLORS[2]}'{sname}'{COLORS[5]}.{RESET}") # Cyan msg, Yellow filename/sheet
    print(f"{COLORS[5]}ask questions about attendance. Type 'quit' to exit.{RESET}") # Cyan Instructions

    while True:
        query = input(f"{COLORS[2]}Query: {RESET}") # Yellow Prompt

        if query.lower() == 'quit':
            print(f"{COLORS[6]}Exiting.{RESET}") # White Exit message
            break

        print(f"{COLORS[6]}Processing query...{RESET}") # White Processing message
        answer = ask_groq(client, data_context, query)

        # Remove content between <think> tags before printing
        # cleaned_answer = answer
        cleaned_answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip()

        print(f"\n{COLORS[1]}Answer:{RESET} {COLORS[6]}{cleaned_answer}{RESET}\n") # Green label, White answer text

if __name__ == "__main__":
    main()
