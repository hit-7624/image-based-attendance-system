import pandas as pd
from groq import Groq
import os
from dotenv import load_dotenv 
import sys 
import glob 

def load_data(file_path, sheet_name):
    """Loads data from a specific sheet in the specified Excel file."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if 'Roll Number' not in df.columns:
            print(f"Error: Sheet '{sheet_name}' in file '{os.path.basename(file_path)}' must contain a 'Roll Number' column.")
            return None
        df = df.astype(str)
        return df
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except ValueError as e:
         print(f"Error: Sheet named '{sheet_name}' not found in '{os.path.basename(file_path)}'. {e}")
         return None
    except Exception as e:
        print(f"Error loading sheet '{sheet_name}' from file '{os.path.basename(file_path)}': {e}")
        return None

def format_data_for_prompt(df):
    """Converts the DataFrame to a string format suitable for the LLM prompt."""
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
    load_dotenv() # Load environment variables from .env file
    groq_api_key = os.environ.get("GROQ_API_KEY") # Get key from environment
    attendance_folder = "attendance_data"

    if not groq_api_key:
        print("Error: GROQ_API_KEY not found.")
        print("Please ensure the .env file exists and contains GROQ_API_KEY='your_actual_key'")
        sys.exit(1)

    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        sys.exit(1)

    selected_file_path = None
    search_path = os.path.join(attendance_folder, '*.xlsx')
    excel_files = glob.glob(search_path)

    if not excel_files:
        print(f"Error: No .xlsx files found in the folder '{attendance_folder}'.")
        print("Please make sure the folder exists and contains your attendance Excel files.")
        sys.exit(1)

    print("\nAvailable Subjects (Excel Files):")
    for i, file_path in enumerate(excel_files):
        print(f"{i + 1}. {os.path.basename(file_path)}")

    while True:
        try:
            choice_str = input(f"Enter the NUMBER of the subject file you want to query: ")
            selected_index = int(choice_str) - 1
            if 0 <= selected_index < len(excel_files):
                selected_file_path = excel_files[selected_index]
                break
            else:
                print(f"Invalid number. Please enter a number between 1 and {len(excel_files)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (EOFError, KeyboardInterrupt):
             print("\nExiting.")
             sys.exit(0)

    print(f"\nSelected subject file: '{os.path.basename(selected_file_path)}'")

    sheet_name = None
    xls = pd.ExcelFile(selected_file_path)
    sheet_names = xls.sheet_names
    if not sheet_names:
        print(f"Error: No sheets found in the selected file '{os.path.basename(selected_file_path)}'.")
        sys.exit(1)

    if len(sheet_names) == 1:
        sheet_name = sheet_names[0]
        print(f"Automatically selected the only sheet: '{sheet_name}'")
    else:
        print("\nAvailable sheets in this file:")
        for i, name in enumerate(sheet_names):
            print(f"{i + 1}. {name}")
        while True:
            try:
                choice = input(f"Enter the number or name of the sheet you want to query: ")
                try:
                    selected_index = int(choice) - 1
                    if 0 <= selected_index < len(sheet_names):
                        sheet_name = sheet_names[selected_index]
                        break
                    else:
                        print("Invalid number choice. Please try again.")
                except ValueError:
                    if choice in sheet_names:
                        sheet_name = choice
                        break
                    else:
                        print(f"Sheet '{choice}' not found. Please enter a valid number or name.")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                sys.exit(0)
        print(f"\nSelected sheet: '{sheet_name}'")

    # --- Load Data from Selected File and Sheet ---
    print(f"Loading data from file '{os.path.basename(selected_file_path)}', sheet '{sheet_name}'...")
    data_df = load_data(selected_file_path, sheet_name)
    if data_df is None:
        sys.exit(1)
    if data_df.empty:
        print(f"Warning: Sheet '{sheet_name}' in file '{os.path.basename(selected_file_path)}' contains no data rows below the header.")
    data_context = format_data_for_prompt(data_df)
    print("Data loaded successfully.")

    # --- Interaction Loop ---
    print(f"\nExcel Chatbot initialized for Subject: '{os.path.basename(selected_file_path)}', Sheet: '{sheet_name}'.")
    print("Ask questions about attendance based on Roll Number and Dates (e.g., 'Attendance for Roll Number 5 on 19-4-25?').")
    print("Type 'quit' to exit.")

    while True:
        try:
            query = input("Query: ")
        except EOFError:
            print("\nExiting.")
            break
        if query.lower() == 'quit':
            print("Exiting.")
            break
        if not query.strip():
            continue
        try:
            print("Processing query...")
            answer = ask_groq(client, data_context, query)
            print(f"\nAnswer: {answer}\n")
        except Exception as e: 
            print(f"An unexpected error occurred while processing the query: {e}")

if __name__ == "__main__":
    main()
