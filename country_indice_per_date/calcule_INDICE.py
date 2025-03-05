import pandas as pd
import numpy as np

def get_crime_weights():
    """
    Define crime weights based on the French classification
    Weights are on a scale of 1-10
    """
    return {
        'homicide intentionnel': 10,
        'tentative d\'homicide volontaire': 9,
        'viol': 9,
        'violence sexuelle': 8,
        'exploitation sexuelle': 8,
        'agression sexuelle': 7,
        'attaque grave': 7,
        'enlèvement': 8,
        'participation à un groupe criminel organisé': 6,
        'vol qualifié': 6,
        'blanchiment d\'argent': 5,
        'vol par effraction': 5,
        'vol par effraction de résidences privées': 6,
        'vol d\'un véhicule motorisé ou de pièces de celui-ci': 5,
        'vol': 4,
        'actes illicites impliquant des drogues ou des précurseurs contrôlés': 6,
        'corruption': 4,
        'pots-de-vin': 3,
        'pédopornographie': 9,
        'actes contre les systèmes informatiques': 3,
        'fraude': 2
    }

def calculate_crime_index(df):
    """
    Calculate crime index per country per year using the formula:
    Index = Σ(Number of infractions × Weight) / Population
    """
    crime_weights = get_crime_weights()
    df_processed = df.copy()
    
    # Convert value column to numeric
    df_processed['value'] = pd.to_numeric(df_processed['value'], errors='coerce')
    
    # Normalize crime type strings
    df_processed['crime_type'] = df_processed['crime_type'].str.lower().str.strip()
    
    # Add weight column based on crime type
    df_processed['weight'] = df_processed['crime_type'].map(crime_weights)
    
    # Calculate weighted infractions (Nombre d'infractions × Poids)
    df_processed['weighted_infractions'] = df_processed['value'] * df_processed['weight']
    
    # Get population for the corresponding year
    df_processed['population'] = df_processed.apply(
        lambda row: pd.to_numeric(row[f'population_{row["year"]}'], errors='coerce'), 
        axis=1
    )
    
    # Remove rows with missing values
    df_processed = df_processed.dropna(subset=['weighted_infractions', 'population'])
    
    # Group by country and year to calculate final index
    result = (df_processed.groupby(['country', 'year'])
              .agg({
                  'weighted_infractions': 'sum',  # Sum of (Nombre d'infractions × Poids)
                  'population': 'first'
              })
              .reset_index())
    
    # Calculate final index
    result['crime_index'] = result['weighted_infractions'] / result['population']
    
    return result[['country', 'year', 'crime_index', 'weighted_infractions']]

def main():
    try:
        df = pd.read_csv('merged_data_pop_total_crimes.csv')
        result = calculate_crime_index(df)
        result = result.sort_values(['country', 'year'])
        
        # Save results
        result.to_csv('crime_indices_by_country_year.csv', index=False)
        
        # Print summary statistics
        print(f"Number of countries processed: {result['country'].nunique()}")
        print(f"Years covered: {result['year'].min()} to {result['year'].max()}")
        print(f"Average crime index: {result['crime_index'].mean():.6f}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    main()