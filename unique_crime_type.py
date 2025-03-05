import pandas as pd

# Read the merged crimes file
df = pd.read_csv('merged_crimes_per_hundred_thousand_french.csv')

# Get unique Countrys
unique_crimes = df['Country'].unique()

# Create a DataFrame with unique Countrys
unique_crimes_df = pd.DataFrame(unique_crimes, columns=['crime_type'])

# Save to CSV file
unique_crimes_df.to_csv('unique_country_types.csv', index=False)

print(f"Found {len(unique_crimes)} unique Countrys and saved to 'unique_country_types.csv'")