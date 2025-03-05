import os
import csv
import tempfile
import shutil

def remove_second_line(file_path):
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='')
    
    with open(file_path, 'r', newline='') as infile, temp_file:
        reader = csv.reader(infile)
        writer = csv.writer(temp_file)
        
        # Write the header (first line)
        header = next(reader, None)
        if header:
            writer.writerow(header)
        
        # Skip the second line
        next(reader, None)
        
        # Write the rest of the lines
        for row in reader:
            writer.writerow(row)
    
    # Replace the original file with the temporary file
    shutil.move(temp_file.name, file_path)

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            remove_second_line(file_path)
            print(f"Processed {filename}")

# Directory containing the CSV files
directory = "output_clean_QGIS"

# Process all CSV files in the directory
process_directory(directory)
print("All CSV files have been processed.")