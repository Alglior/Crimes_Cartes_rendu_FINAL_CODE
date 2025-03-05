import pandas as pd

def replace_coordinates(file_path, output_path):
    """
    Replace specific coordinates in a CSV file.
    
    Args:
        file_path (str): Path to the input CSV file
        output_path (str): Path where the modified CSV will be saved
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Replace the specific coordinates
        # First, convert to string to ensure exact matching
        df = df.astype(str)
        
        # Replace the coordinates wherever they appear in the dataframe
        df = df.replace('45.0511621486', '45.815399')
        df = df.replace('16.4117801486', '15.966568')
        
        # Save the modified dataframe to a new CSV file
        df.to_csv(output_path, index=False)
        print(f"Coordinates successfully replaced and saved to {output_path}")
        
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
file_path = 'merged_crimes_per_hundred_thousand.csv'
output_path = 'merged_crimes_per_hundred_thousand_updated.csv'

replace_coordinates(file_path, output_path)
