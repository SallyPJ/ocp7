import pandas as pd
import time

CSV_FILE = "../datasets/actions_list.csv"
BUDGET = 500  # Définir le budget comme une variable globale

# Charger et nettoyer les données
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

# Fonction pour trouver la meilleure combinaison d'actions avec programmation dynamique
def find_best_combination_dp(actions, budget=BUDGET):
    n = len(actions)
    # Créer un tableau pour stocker le meilleur profit pour chaque budget
    dp = [0] * (budget + 1)
    # Créer un tableau pour stocker les actions sélectionnées pour chaque budget
    selected_actions = [[] for _ in range(budget + 1)]

    # Parcourir chaque action
    for action in actions:
        cost = int(action['cost'])
        profit = action['profit_amount']

        # Mettre à jour le tableau dp de manière descendante pour éviter d'écraser les données
        for b in range(budget, cost - 1, -1):
            if dp[b - cost] + profit > dp[b]:
                dp[b] = dp[b - cost] + profit
                selected_actions[b] = selected_actions[b - cost] + [action]

    # Le meilleur profit sera à dp[budget], avec les actions correspondantes
    return selected_actions[budget], dp[budget]

# Charger les données et préparer les actions
df = upload_data(CSV_FILE)
actions = df.to_dict('records')

# Démarrer le chronomètre uniquement pour l'algorithme
start_time = time.time()
# Trouver la meilleure combinaison d'actions dans le budget avec programmation dynamique
best_combination, best_profit = find_best_combination_dp(actions)
# Arrêter le chronomètre
end_time = time.time()
# Calculer la durée d'exécution
execution_time = end_time - start_time

# Calculer le coût total des actions sélectionnées
best_combination_cost = sum(action['cost'] for action in best_combination)

# Premier tableau : Résumé des résultats
summary_df = pd.DataFrame({
    "Durée d'exécution (s)": [execution_time],
    "Nombre de combinaisons (approximé)": [len(actions) * BUDGET],
    "Coût total de la meilleure combinaison d'actions (€)": [best_combination_cost],
    "Profit de la meilleure combinaison (€)": [best_profit]
})

# Deuxième tableau : Meilleure combinaison d'actions
best_combination_df = pd.DataFrame(best_combination)

# Afficher les tableaux
print("Résumé des résultats :")
print(summary_df.to_string())
print("\nMeilleure combinaison d'actions :")
print(best_combination_df)