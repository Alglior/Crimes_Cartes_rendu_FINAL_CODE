import pandas as pd

def add_country_codes():
    # Charger le CSV
    df = pd.read_csv('merged_crimes_per_hundred_thousand_french.csv')
    
    # Dictionnaire de mapping des noms complexes vers des noms simplifiés
    name_mapping = {
        "Irlande du Nord (Royaume-Uni) (NUTS 2021)": "Irlande du Nord",
        "Écosse (NUTS 2021)": "Écosse",
        "Kosovo*": "Kosovo",
        "République tchèque": "Tchéquie"
    }
    
    # Dictionnaire des codes pays
    country_codes = {
        "Tchéquie": {"FIPS": "EZ", "ISO2": "CZ", "ISO3": "CZE"},
        "Kosovo": {"FIPS": "KV", "ISO2": "XK", "ISO3": "XKX"},
        "Irlande du Nord": {"FIPS": "UK", "ISO2": "GB-NIR", "ISO3": "GBR"},
        "Écosse": {"FIPS": "UK", "ISO2": "GB-SCT", "ISO3": "GBR"},
        "Turquie": {"FIPS": "TU", "ISO2": "TR", "ISO3": "TUR"}
    }
    
    # Simplifier d'abord les noms
    df['NAME'] = df['NAME'].replace(name_mapping)
    
    # Créer une fonction pour appliquer les codes
    def apply_codes(row):
        if pd.isnull(row['FIPS']) or pd.isnull(row['ISO2']) or pd.isnull(row['ISO3']):
            if row['NAME'] in country_codes:
                codes = country_codes[row['NAME']]
                row['FIPS'] = codes['FIPS']
                row['ISO2'] = codes['ISO2']
                row['ISO3'] = codes['ISO3']
        return row
    
    # Appliquer les codes pays
    df = df.apply(apply_codes, axis=1)
    
    # Sauvegarder le fichier mis à jour
    output_file = 'merged_crimes_per_hundred_thousand_french_updated.csv'
    df.to_csv(output_file, index=False)
    
    # Afficher les statistiques
    print(f"Mise à jour terminée. Fichier sauvegardé : {output_file}")
    print("\nStatistiques :")
    for country in country_codes.keys():
        count = len(df[df['NAME'] == country])
        print(f"{country}: {count} entrées trouvées et mises à jour")
    
    # Afficher les noms uniques restants pour vérification
    print("\nListe de tous les noms de pays uniques dans le fichier :")
    print(sorted(df['NAME'].unique()))

if __name__ == "__main__":
    try:
        add_country_codes()
    except Exception as e:
        print(f"Une erreur s'est produite : {str(e)}")