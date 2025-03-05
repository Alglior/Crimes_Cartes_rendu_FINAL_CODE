import pandas as pd
import numpy as np
from datetime import datetime

def calculate_crime_index(merged_df, weights_df):
    """
    Calculate crime index based on crime rates and their weights using merged data
    that already contains population information.
    
    Parameters:
    merged_df: DataFrame with both crime and population data
    weights_df: DataFrame with crime weights
    
    Returns:
    DataFrame with calculated crime indices by country and year
    """
    # Add helper function for ISO 8601 conversion
    def convert_to_iso8601(year):
        # Convert year to ISO 8601 format (assuming start of year)
        return datetime(int(year), 1, 1).isoformat()

    # Print column names for debugging
    print("Available columns:", merged_df.columns.tolist())
    
    # Convert weights to dictionary for easier lookup
    weights_dict = dict(zip(weights_df['Crime'], weights_df['Poids (1-10)']))
    
    # Clean up the value column
    merged_df['value'] = merged_df['value'].replace(':', np.nan)
    merged_df['value'] = pd.to_numeric(merged_df['value'], errors='coerce')
    
    # Helper function to get population for a specific row
    def get_population(row):
        year = int(row['year'])
        pop_col = f'population_{year}'
        return row[pop_col]

    # Add population column before grouping
    merged_df['population'] = merged_df.apply(get_population, axis=1)

    # First, calculate total crimes per type for each country/year
    country_totals = merged_df.groupby(['country', 'year', 'crime_type']).agg({
        'value': 'sum',
        'population': 'first',
        'lat': 'first',
        'lon': 'first'
    }).reset_index()

    # Calculate crime rate per 100,000 population for each crime type
    country_totals['Crime_Rate'] = (country_totals['value'] / country_totals['population']) * 100000

    # Convert weights to dictionary
    weights_dict = dict(zip(weights_df['Crime'], weights_df['Poids (1-10)']))

    # Apply weights to each crime type
    country_totals['Weighted_Value'] = country_totals.apply(
        lambda row: row['Crime_Rate'] * weights_dict.get(row['crime_type'], 0)
        if pd.notnull(row['Crime_Rate']) else 0,
        axis=1
    )

    # Modify the final groupby to include lat and lon
    crime_index = country_totals.groupby(['country', 'year']).agg({
        'Weighted_Value': 'sum',
        'lat': 'first',
        'lon': 'first'
    }).reset_index()

    # Rename columns (now including lat and lon)
    crime_index.columns = ['Country', 'Year', 'Crime_Index', 'Latitude', 'Longitude']

    # Normalize to 0-100 scale
    max_index = crime_index['Crime_Index'].max()
    crime_index['Normalized_Index'] = (crime_index['Crime_Index'] / max_index) * 100

    # Don't drop latitude and longitude when dropping Crime_Index
    crime_index = crime_index[['Country', 'Year', 'Normalized_Index', 'Latitude', 'Longitude']]

    # Convert Year to ISO 8601 format
    crime_index['Year'] = crime_index['Year'].apply(convert_to_iso8601)

    # Ensure proper column order with formatted date
    crime_index = crime_index[['Country', 'Year', 'Normalized_Index', 'Latitude', 'Longitude']]

    # Sort by country alphabetically and year in reverse order
    crime_index = crime_index.sort_values(['Country', 'Year'], ascending=[True, False])
    
    return crime_index

# Remove the separate normalize_crime_index function since it's now integrated

# Example usage:
merged_df = pd.read_csv('merged_data_pop_total_crimes.csv', encoding='utf-8')
weights_df = pd.read_csv('poids_crimes.csv', encoding='utf-8')

# Calculate crime index (normalization is now included)
crime_index = calculate_crime_index(merged_df, weights_df)

# Save results with UTF-8 encoding
crime_index.to_csv('crime_index_results.csv', index=False, encoding='utf-8')