import pandas as pd

# Load the population data
population_df = pd.read_csv('populations_worldbank.csv')

# Load the crimes data
crimes_df = pd.read_csv('merged_crimes_per_hundred_thousand_french.csv')

# Print column names to check
print("Population DataFrame columns:", population_df.columns.tolist())
print("Crimes DataFrame columns:", crimes_df.columns.tolist())

# Clean column names
population_df.columns = population_df.columns.str.strip().str.lower().str.replace(' ', '_')
crimes_df.columns = crimes_df.columns.str.strip().str.lower().str.replace(' ', '_')

# Print cleaned column names
print("\nAfter cleaning:")
print("Population DataFrame columns:", population_df.columns.tolist())
print("Crimes DataFrame columns:", crimes_df.columns.tolist())

# Print first few rows of each dataframe to verify data
print("\nFirst few rows of population data:")
print(population_df.head())
print("\nFirst few rows of crimes data:")
print(crimes_df.head())

# Try to find common column for country
common_columns = set(population_df.columns) & set(crimes_df.columns)
print("\nCommon columns between datasets:", common_columns)

# Perform merge with error handling
try:
    # First try with 'country'
    merged_df = pd.merge(population_df, crimes_df, on='country', how='inner')
except KeyError:
    try:
        # Then try with 'country_name' if 'country' fails
        merged_df = pd.merge(population_df, crimes_df, on='country_name', how='inner')
    except KeyError:
        print("Error: Could not find matching country column. Please check the column names.")
        exit(1)

print(f"\nSuccessfully merged {len(merged_df)} rows")

# Save the merged dataframe to a new CSV file
merged_df.to_csv('merged_data_pop_total_crimes_hundred_thousand.csv', index=False)
