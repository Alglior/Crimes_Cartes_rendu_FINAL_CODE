import pandas as pd

def extract_country_names(input_file, output_file):
    """
    Extrait uniquement les noms de pays uniques d'un fichier CSV 
    et les sauvegarde dans un nouveau fichier.
    
    Args:
        input_file (str): Chemin du fichier CSV source
        output_file (str): Chemin du fichier CSV de sortie
    """
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(input_file)
        
        # Extraction des noms de pays uniques
        unique_countries = pd.DataFrame(df['Country'].unique(), columns=['Country'])
        
        # Tri par ordre alphabétique
        unique_countries = unique_countries.sort_values('Country')
        
        # Sauvegarde dans un nouveau fichier CSV
        unique_countries.to_csv(output_file, index=False)
        
        print(f"Nombre de pays uniques extraits : {len(unique_countries)}")
        print(f"Fichier sauvegardé : {output_file}")
        
    except FileNotFoundError:
        print(f"Erreur : Le fichier {input_file} n'existe pas")
    except Exception as e:
        print(f"Une erreur est survenue : {str(e)}")

# Exemple d'utilisation
if __name__ == "__main__":
    input_file = "merged_crimes_per_hundred_thousand.csv"
    output_file = "pays_uniques.csv"
    extract_country_names(input_file, output_file)