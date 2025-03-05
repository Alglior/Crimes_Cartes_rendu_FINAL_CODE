import os
import pandas as pd
import glob
import unicodedata
import re

# Path to the folder containing CSV files
input_folder = '/home/antec/Documents/data/crime_per_type/output_clean_QGIS'

# Output file names
output_file_hundred_thousand = 'merged_crimes_per_hundred_thousand.csv'
output_file_number = 'merged_crimes_number.csv'

# Path to the europe.csv file
europe_file = 'europe.csv'

print(f"Input folder: {input_folder}")
print(f"Input folder exists: {os.path.exists(input_folder)}")
print(f"Europe file exists: {os.path.exists(europe_file)}")

# Load the europe.csv file
europe_df = pd.read_csv(europe_file)

# Function to normalize string (remove diacritics and convert to lowercase)
def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn').lower()

# Function to extract lat and lon from the Coordinate column
def extract_coordinates(coord_string):
    lat_match = re.search(r'lat:\s*([-\d.]+)', coord_string)
    lon_match = re.search(r'lon:\s*([-\d.]+)', coord_string)
    lat = float(lat_match.group(1)) if lat_match else None
    lon = float(lon_match.group(1)) if lon_match else None
    return pd.Series({'lat': lat, 'lon': lon})

# Extract lat and lon from the Coordinate column
europe_df[['lat', 'lon']] = europe_df['Coordinate'].apply(extract_coordinates)

# Create a dictionary for quick lookup of country data
country_data = {normalize_string(row['NAME']): row.to_dict() 
                for _, row in europe_df.iterrows()}

# Add custom entry for England and Wales
country_data['england and wales'] = {
    'FIPS': 'UKEW',
    'ISO2': 'XE',  # Custom code
    'ISO3': 'XEW',  # Custom code
    'UN': '826',  # Using UK's UN code
    'NAME': 'England and Wales',
    'lat': 52.3555,  # Approximate coordinates for England and Wales
    'lon': -1.1743
}

# Add name variations
name_variations = {
    'czechia': 'czech republic',
    'Turkey': 'Türkiye',
    'The former Yugoslav Republic of Macedonia': 'North Macedonia',
    # Add more variations here if needed
}

# Function to get country data
def get_country_data(country):
    normalized_country = normalize_string(country)
    if normalized_country in name_variations:
        normalized_country = name_variations[normalized_country]
    return country_data.get(normalized_country, {})

# Lists to store dataframes
hundred_thousand_dataframes = []
number_dataframes = []

# Check if the folder exists
if not os.path.exists(input_folder):
    print(f"The folder {input_folder} does not exist.")
    exit()

# Get all CSV files in the folder
csv_files = glob.glob(os.path.join(input_folder, '*.csv'))

print(f"CSV files found: {csv_files}")

if not csv_files:
    print(f"No CSV files found in the folder {input_folder}")
    exit()

for file in csv_files:
    try:
        # Extract the crime type and data type from the filename
        filename_parts = os.path.basename(file).split('_')
        crime_type = ' '.join(filename_parts[2:-1])
        data_type = filename_parts[-1].replace('.csv', '')
        
        # Read the CSV file
        df = pd.read_csv(file)
        
        if df.empty:
            print(f"The file {file} is empty and will be ignored.")
            continue
        
        # Add columns for crime type and data type
        df['Crime Type'] = crime_type
        df['Data Type'] = data_type
        
        # Add country data columns
        df['FIPS'] = df['Country'].map(lambda x: get_country_data(x).get('FIPS', ''))
        df['ISO2'] = df['Country'].map(lambda x: get_country_data(x).get('ISO2', ''))
        df['ISO3'] = df['Country'].map(lambda x: get_country_data(x).get('ISO3', ''))
        df['UN'] = df['Country'].map(lambda x: get_country_data(x).get('UN', ''))
        df['NAME'] = df['Country'].map(lambda x: get_country_data(x).get('NAME', x))
        df['lat'] = df['Country'].map(lambda x: get_country_data(x).get('lat', ''))
        df['lon'] = df['Country'].map(lambda x: get_country_data(x).get('lon', ''))
        
        # Add the dataframe to the appropriate list
        if 'hundred thousand' in data_type.lower():
            hundred_thousand_dataframes.append(df)
        elif 'number' in data_type.lower():
            number_dataframes.append(df)
        
        print(f"File {file} processed successfully.")
    except Exception as e:
        print(f"Error processing file {file}: {str(e)}")

# Check if any valid DataFrames were created
if not hundred_thousand_dataframes and not number_dataframes:
    print("No valid DataFrames were created. Check your CSV files.")
    exit()

# Merge and save "Per hundred thousand inhabitants" data
if hundred_thousand_dataframes:
    merged_hundred_thousand = pd.concat(hundred_thousand_dataframes, ignore_index=True)
    merged_hundred_thousand = merged_hundred_thousand[['Country', 'FIPS', 'ISO2', 'ISO3', 'UN', 'NAME', 'lat', 'lon', 'Year', 'Value', 'Crime Type', 'Data Type']]
    merged_hundred_thousand.to_csv(output_file_hundred_thousand, index=False)
    print(f"'Per hundred thousand inhabitants' data merged into {output_file_hundred_thousand}")
    print(f"Total rows in 'Per hundred thousand inhabitants' file: {len(merged_hundred_thousand)}")

# Merge and save "Number" data
if number_dataframes:
    merged_number = pd.concat(number_dataframes, ignore_index=True)
    merged_number = merged_number[['Country', 'FIPS', 'ISO2', 'ISO3', 'UN', 'NAME', 'lat', 'lon', 'Year', 'Value', 'Crime Type', 'Data Type']]
    merged_number.to_csv(output_file_number, index=False)
    print(f"'Number' data merged into {output_file_number}")
    print(f"Total rows in 'Number' file: {len(merged_number)}")

print("Merging process completed.")

# Print countries with missing data
all_data = pd.concat([merged_hundred_thousand, merged_number], ignore_index=True)
missing_data = all_data[all_data['FIPS'].isna() | all_data['ISO2'].isna() | all_data['ISO3'].isna() | all_data['UN'].isna() | all_data['lat'].isna() | all_data['lon'].isna()]
if not missing_data.empty:
    print("\nCountries with missing data:")
    print(missing_data['Country'].unique())