import os
from openpyxl import load_workbook

def rename_excel_files(directory='per_sheets', cells=['C5', 'C6', 'C7']):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"The directory {directory} does not exist.")
        return

    # Get all .xls and .xlsx files in the directory
    excel_files = [f for f in os.listdir(directory) if f.endswith(('.xls', '.xlsx'))]

    for file in excel_files:
        file_path = os.path.join(directory, file)
        
        try:
            # Load the workbook
            wb = load_workbook(file_path, read_only=True, data_only=True)
            sheet = wb.active

            # Extract values from specified cells
            new_name_parts = []
            for cell in cells:
                value = sheet[cell].value
                if value:
                    new_name_parts.append(str(value))

            # Create new filename
            if new_name_parts:
                new_name = '_'.join(new_name_parts) + os.path.splitext(file)[1]
                new_path = os.path.join(directory, new_name)

                # Rename the file
                os.rename(file_path, new_path)
                print(f"Renamed '{file}' to '{new_name}'")
            else:
                print(f"Skipped '{file}': No valid values found in specified cells")

        except Exception as e:
            print(f"Error processing '{file}': {str(e)}")

if __name__ == "__main__":
    rename_excel_files()