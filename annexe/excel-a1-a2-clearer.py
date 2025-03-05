import os
from openpyxl import load_workbook

def clear_a1_a2_cells(directory='per_sheets'):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    # Get all .xlsx files in the directory
    excel_files = [f for f in os.listdir(directory) if f.endswith('.xlsx')]

    for file in excel_files:
        file_path = os.path.join(directory, file)
        
        try:
            # Load the workbook
            wb = load_workbook(file_path)
            sheet = wb.active

            # Clear cells A1 and A2
            sheet['A1'] = None
            sheet['A2'] = None

            # Save the changes
            wb.save(file_path)
            print(f"Cleared cells A1 and A2 in '{file}'")

        except Exception as e:
            print(f"Error processing '{file}': {str(e)}")

if __name__ == "__main__":
    clear_a1_a2_cells()
