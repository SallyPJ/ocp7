import pandas as pd
import time

CSV_FILES = ["../datasets/actions_list.csv", "../datasets/dataset1_Python+P7.csv", "../datasets/dataset2_Python+P7.csv"]
BUDGET = 500  # Définir le budget comme une variable globale

# Charger et nettoyer les données
def upload_data(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    column_mapping = {
        'Coût par action (en euros)': 'cost',
        'price': 'cost',
        'Bénéfice (après 2 ans)': 'profit',
    }
    df.rename(columns=column_mapping, inplace=True)

    # Convertir les colonnes en types appropriés
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
    df = df[(df['cost'] > 0) & (df['cost'] <= BUDGET)]
    # Traiter la colonne 'profit' pour gérer les chaînes et les chiffres
    df['profit'] = df['profit'].astype(str).str.replace('%', '')  # Convertir tout en chaîne et supprimer les %
    df['profit'] = pd.to_numeric(df['profit'],
                                 errors='coerce') / 100  # Convertir en nombre et diviser par 100 pour obtenir le pourcentage
    df['profit_amount'] = df['profit'] * df['cost']

    # Supprimer les lignes avec des valeurs manquantes ou incorrectes
    df.dropna(subset=['cost', 'profit'], inplace=True)

    return df

# Fonction pour trouver la meilleure combinaison d'actions avec programmation dynamique
def find_best_combination_dp(actions, budget=BUDGET):

    # Créer un tableau pour stocker le meilleur profit pour chaque budget
    max_profit_for_budget = [0] * (budget + 1)
    # Créer un tableau pour stocker les actions sélectionnées pour chaque budget
    best_action_combination = [[] for _ in range(budget + 1)]

    # Parcourir chaque action
    for action in actions:
        cost = action['cost']
        profit = action['profit_amount']

        # Mettre à jour le tableau dp de manière descendante pour éviter d'écraser les données
        for b in range(budget, cost - 1, -1):
            if max_profit_for_budget[b - cost] + profit > max_profit_for_budget[b]:
                max_profit_for_budget[b] = max_profit_for_budget[b - cost] + profit
                best_action_combination[b] = best_action_combination[b - cost] + [action]

    # Le meilleur profit sera à dp[budget], avec les actions correspondantes
    return best_action_combination[budget], max_profit_for_budget[budget]

def process_datasets(csv_files):
    for file in csv_files:
        print(f"Traitement du fichier : {file}")
        # Charger les données et préparer les actions
        df = upload_data(file)
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


process_datasets(CSV_FILES)