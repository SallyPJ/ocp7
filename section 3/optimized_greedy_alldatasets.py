import pandas as pd
from time import perf_counter
CSV_FILES = ["../datasets/actions_list.csv", "../datasets/dataset1_Python+P7.csv", "../datasets/dataset2_Python+P7.csv"]
BUDGET = 500*100

# Charger et nettoyer les données
def upload_data(CSV_FILE):

    # Charger les données et créer une copie
    dataframe = pd.read_csv(CSV_FILE).copy()

    # Renommer les colonnes
    column_mapping = {
        'Coût par action (en euros)': 'cost',
        'price': 'cost',
        'Actions #': 'name',
        'Bénéfice (après 2 ans)': 'profit',
    }
    dataframe.rename(columns=column_mapping, inplace=True)

    # Supprimer les lignes avec des valeurs manquantes
    dataframe.dropna(subset=['cost', 'profit'], inplace=True)

    # Convertir les valeurs des benefices des pourcentages vers des décimales
    dataframe['profit'] = dataframe['profit'].astype(str).str.replace('%', '')
    dataframe['profit'] = pd.to_numeric(dataframe['profit'],
                                        errors='coerce') / 100

    # Supprimer les actions avec un coût de 0 ou inférieur,
    # supérieur au budget,
    # ou ayant un bénéfice négatif
    dataframe = dataframe[(dataframe['cost'] > 0)
                          & (dataframe['cost'] <= BUDGET)
                          & (dataframe['profit'] > 0)]

    # Supprimer les doublons basés sur la colonne 'name'
    dataframe = dataframe[~dataframe['name'].duplicated(keep=False)]

    # Convertir les valeurs des actions des euros vers les centimes
    dataframe['cost'] = pd.to_numeric(dataframe['cost'], errors='coerce') * 100

    # Calculer le montant des benefices en centimes
    dataframe['profit_amount'] = dataframe['profit'] * dataframe['cost']
    print(dataframe['profit_amount'])

    return dataframe

# Fonction pour trouver la meilleure combinaison d'actions avec programmation dynamique
def greedy_best_combination(actions, budget=BUDGET):
    # Calculer le rapport profit/coût pour chaque action
    for action in actions:
        action['ratio'] = (action['profit_amount']
                           / action['cost']) if action['cost'] > 0 else 0

    # Trier les actions par rapport profit/coût en ordre décroissant
    actions_sorted = sorted(actions, key=lambda x: x['ratio'], reverse=True)

    best_combination = []
    total_cost = 0
    total_profit = 0
    total_combinations = 0

    # Ajouter les actions dans la combinaison tant que le budget le permet
    for action in actions_sorted:
        total_combinations += 1
        if total_cost + action['cost'] <= budget:
            best_combination.append(action)
            total_cost += action['cost']
            total_profit += action['profit_amount']

    return best_combination, total_profit, total_cost, total_combinations


def display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations):
    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost / 100],
        "Profit de la meilleure combinaison (€)": [round(best_profit / 100, 2)]
    })

    # Deuxième tableau : Meilleure combinaison d'actions
    best_combination_dataframe = pd.DataFrame(best_combination)

    # Diviser la colonne 'cost' par 100 pour l'affichage en euros
    best_combination_dataframe['cost'] = best_combination_dataframe['cost'] / 100
    best_combination_dataframe['profit_amount'] = (best_combination_dataframe['profit_amount'] / 100).round(2)
    best_combination_dataframe['profit'] = best_combination_dataframe['profit'] * 100
    best_combination_dataframe['profit'] = best_combination_dataframe['profit'].astype(str) + '%'

    print("Résumé des résultats :")
    print(summary_dataframe.to_string())
    print("Meilleure combinaison d'actions :")
    print(best_combination_dataframe)


def main(csv_files):
    for file in csv_files:
        print(f"Traitement du fichier : {file}")
        # Charger les données et préparer les actions
        df = upload_data(file)
        actions = df.to_dict('records')

        start_time = perf_counter()
        best_combination, best_profit, best_combination_cost, total_combinations = greedy_best_combination(actions, budget=BUDGET)
        end_time = perf_counter()
        execution_time = end_time - start_time

        # Calculer le coût total des actions sélectionnées

        display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations)


if __name__ == "__main__":
    main(CSV_FILES)



