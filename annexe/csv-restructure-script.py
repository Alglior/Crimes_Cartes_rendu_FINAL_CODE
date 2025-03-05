import os
import pandas as pd
import glob

def restructure_excel(input_file, output_file):
    try:
        print(f"Reading file: {input_file}")
        df = pd.read_excel(input_file, index_col=0)
        
        print("Melting dataframe...")
        df_melted = df.melt(ignore_index=False, var_name='Year', value_name='Value')
        
        print("Resetting index...")
        df_melted = df_melted.reset_index()
        
        print("Renaming columns...")
        df_melted = df_melted.rename(columns={'index': 'Country'})
        
        print("Removing NaN values...")
        df_melted = df_melted.dropna()
        
        print("Sorting dataframe...")
        df_melted = df_melted.sort_values(['Country', 'Year'])
        
        print(f"Saving to: {output_file}")
        df_melted.to_csv(output_file, index=False)
        print(f"Successfully processed {input_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")

def process_directory(input_dir, output_dir):
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist.")
        return
    
    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir)
    
    excel_files = glob.glob(os.path.join(input_dir, '*.xlsx'))
    print(f"Found {len(excel_files)} Excel files in the input directory.")
    
    if len(excel_files) == 0:
        print("No Excel files found in the input directory.")
        return
    
    for excel_file in excel_files:
        file_name = os.path.basename(excel_file)
        output_file = os.path.join(output_dir, f'restructured_{os.path.splitext(file_name)[0]}.csv')
        restructure_excel(excel_file, output_file)

# Usage
input_directory = 'per_sheets'
output_directory = 'output_clean_QGIS'

if __name__ == "__main__":
    print("Starting Excel restructuring process...")
    process_directory(input_directory, output_directory)
    print("Process completed.")