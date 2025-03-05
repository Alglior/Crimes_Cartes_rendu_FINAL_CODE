import pandas as pd
import requests
import time
from datetime import datetime
import numpy as np
import os

def get_country_code(country_name):
    """
    Convertit les noms de pays en codes ISO utilisés par la Banque Mondiale
    """
    country_codes = {
        "Albanie": "ALB", 
        "Autriche": "AUT",
        "Belgique": "BEL",
        "Bosnie-Herzégovine": "BIH",
        "Bulgarie": "BGR",
        "Croatie": "HRV",
        "Chypre": "CYP",
        "Tchéquie": "CZE",
        "Danemark": "DNK",
        "Estonie": "EST",
        "Finlande": "FIN",
        "France": "FRA",
        "Allemagne": "DEU",
        "Grèce": "GRC",
        "Hongrie": "HUN",
        "Islande": "ISL",
        "Irlande": "IRL",
        "Italie": "ITA",
        "Kosovo": "XKX",
        "Lettonie": "LVA",
        "Liechtenstein": "LIE",
        "Lituanie": "LTU",
        "Luxembourg": "LUX",
        "Malte": "MLT",
        "Monténégro": "MNE",
        "Pays-Bas": "NLD",
        "Macédoine du Nord": "MKD",
        "Norvège": "NOR",
        "Pologne": "POL",
        "Portugal": "PRT",
        "Roumanie": "ROU",
        "Serbie": "SRB",
        "Slovaquie": "SVK",
        "Slovénie": "SVN",
        "Espagne": "ESP",
        "Suède": "SWE",
        "Suisse": "CHE",
        "Turquie": "TUR"
    }
    return country_codes.get(country_name)

def get_population_data(country_code, start_year=2008, end_year=2022):
    """
    Récupère les données de population depuis l'API de la Banque Mondiale
    """
    if not country_code:
        return {year: np.nan for year in range(start_year, end_year + 1)}
    
    try:
        url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/SP.POP.TOTL"
        params = {
            "format": "json",
            "date": f"{start_year}:{end_year}",
            "per_page": 100
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()[1] if len(response.json()) > 1 else []
        
        populations = {year: np.nan for year in range(start_year, end_year + 1)}
        
        for entry in data:
            year = int(entry['date'])
            if start_year <= year <= end_year:
                populations[year] = entry['value']
        
        return populations
        
    except Exception as e:
        print(f"Erreur pour {country_code}: {str(e)}")
        return {year: np.nan for year in range(start_year, end_year + 1)}

def save_df(df, filename):
    """
    Sauvegarde le DataFrame dans un CSV avec gestion des erreurs
    """
    try:
        df.to_csv(filename, index=False)
        print(f"Données sauvegardées dans {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {str(e)}")

def process_countries():
    output_file = 'populations_worldbank.csv'
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(output_file):
        try:
            df = pd.read_csv(output_file)
            print(f"Reprise du fichier existant: {output_file}")
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier existant: {str(e)}")
            df = pd.DataFrame(columns=['Country'] + [f'Population_{year}' for year in range(2008, 2023)])
    else:
        df = pd.DataFrame(columns=['Country'] + [f'Population_{year}' for year in range(2008, 2023)])

    countries = [
        "Albanie", "Autriche", "Belgique", "Bosnie-Herzégovine", "Bulgarie",
        "Croatie", "Chypre", "Tchéquie", "Danemark", "Estonie", "Finlande",
        "France", "Allemagne", "Grèce", "Hongrie", "Islande", "Irlande",
        "Italie", "Kosovo", "Lettonie", "Liechtenstein", "Lituanie",
        "Luxembourg", "Malte", "Monténégro", "Pays-Bas", "Macédoine du Nord",
        "Norvège", "Pologne", "Portugal", "Roumanie", "Serbie", "Slovaquie",
        "Slovénie", "Espagne", "Suède", "Suisse", "Turquie"
    ]
    
    # Filtrer les pays déjà traités
    processed_countries = df['Country'].tolist() if not df.empty else []
    countries_to_process = [c for c in countries if c not in processed_countries]
    
    print(f"Pays déjà traités: {len(processed_countries)}")
    print(f"Pays restants à traiter: {len(countries_to_process)}")
    
    for country in countries_to_process:
        print(f"\nTraitement de {country}...")
        country_code = get_country_code(country)
        
        if country_code:
            populations = get_population_data(country_code)
            
            data = {'Country': country}
            data.update({f'Population_{year}': populations[year] for year in range(2008, 2023)})
            
            # Ajout de la nouvelle ligne
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
            
            # Sauvegarde après chaque pays
            save_df(df, output_file)
            
            time.sleep(0.5)
        else:
            print(f"Code pays non trouvé pour {country}")
    
    return df

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"Début du traitement: {start_time}")
    
    result_df = process_countries()
    
    end_time = datetime.now()
    print(f"\nFin du traitement: {end_time}")
    print(f"Durée totale: {end_time - start_time}")
    
    print("\nAperçu des résultats finaux:")
    print(result_df.head())
    
    missing_stats = result_df.isna().sum()
    print("\nNombre de valeurs manquantes par colonne:")
    print(missing_stats)