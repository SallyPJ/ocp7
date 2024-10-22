import pandas as pd
from itertools import combinations
import time


CSV_FILE = "../datasets/actions_list.csv"
# Charger et nettoyer les données
'''
Génération des combinaisons : O(2^n)
Calcul des profits : 0(n)
Complexité totale : O(2^n * n)
'''
def upload_data(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    df.rename(columns={'Coût par action (en euros)': 'cost', 'Bénéfice (après 2 ans)': 'profit'}, inplace=True)

    # Convertir les colonnes en types appropriés
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
    df['profit'] = df['profit'].str.replace('%', '').astype(float) / 100
    df['profit_amount'] = df['profit'] * df['cost']

    # Supprimer les lignes avec des valeurs manquantes ou incorrectes
    df.dropna(subset=['cost', 'profit'], inplace=True)

    return df


# Fonction pour calculer le profit total et le coût d'une combinaison
def calculate_profit_combinations(combinaison):
    total_cost = sum(action['cost'] for action in combinaison)
    total_profit = sum(action['profit_amount'] for action in combinaison)
    return total_cost, total_profit


# Fonction pour trouver la meilleure combinaison d'actions
def find_best_combination(actions, budget=500):
    best_profit = 0
    best_combination = []
    total_combinations = 0

    # Générer toutes les combinaisons possibles
    for r in range(1, len(actions) + 1):
        for combinaison in combinations(actions, r):
            total_combinations += 1
            total_cost, total_profit = calculate_profit_combinations(combinaison)

            # Vérifier si le coût total est inférieur ou égal au budget
            if total_cost <= budget and total_profit > best_profit:
                best_profit = total_profit
                best_combination = combinaison

    return best_combination, best_profit,total_combinations


# Charger les données et préparer les actions
df = upload_data(CSV_FILE)
actions = df.to_dict('records')

# Démarrer le chronomètre uniquement pour l'algorithme
start_time = time.time()
# Trouver la meilleure combinaison d'actions dans le budget
best_combination, best_profit, total_combinations = find_best_combination(actions)
# Arrêter le chronomètre
end_time = time.time()
# Calculer la durée d'exécution
execution_time = end_time - start_time

# Calculer le coût total des actions sélectionnées
best_combination_cost = sum(action['cost'] for action in best_combination)

# Premier tableau : Résumé des résultats
summary_df = pd.DataFrame({
    "Durée d'exécution (s)": [execution_time],
    "Nombre de combinaisons": [total_combinations],
    "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost],
    "Profit de la meilleure combinaison (€)": [best_profit]

})

# Deuxième tableau : Meilleure combinaison d'actions
best_combination_df = pd.DataFrame(best_combination)

# Afficher les tableaux
print("Résumé des résultats :")
print(summary_df.to_string())
print("\nMeilleure combinaison d'actions :")
print(best_combination_df)