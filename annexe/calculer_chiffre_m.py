def calculer_chiffre_m(chiffre):
    if chiffre >= 1000000:
        chiffre = chiffre / 1000000
        # Formatage avec 2 décimales et séparateur de milliers
        return f"{chiffre:,.2f}M".replace(',', ' ')
    elif chiffre >= 1000:
        chiffre = chiffre / 1000
        return f"{chiffre:,.2f}K".replace(',', ' ')
    else:
        return f"{chiffre:,.0f}".replace(',', ' ')

# user input in loop
while True:
    chiffre = int(input("Entrez un chiffre: "))
    print(calculer_chiffre_m(chiffre))
    if chiffre == 0:
        break
