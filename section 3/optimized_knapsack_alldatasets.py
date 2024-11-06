import pandas as pd
import time

CSV_FILES = ["../datasets/actions_list.csv", "../datasets/dataset1_Python+P7.csv", "../datasets/dataset2_Python+P7.csv"]
BUDGET = 500*100

# Charger et nettoyer les données
def upload_data(CSV_FILE):
    """
    Charger et nettoyer les données
    :param CSV_FILE:
    :return: dataframe
    """
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

    return dataframe


def find_best_combination(actions, budget=BUDGET):
    """
    :param actions:
    :param budget:
    :return selected_actions[budget]:
    :return max_profit_for_budget[budget]:
    :return total_combinations:
    """

    # Créer un tableau pour stocker le meilleur profit pour chaque budget (de 0 à 50000). Commence à 0 d'où le + 1
    max_profit_for_budget = [0] * (budget + 1)

    # Créer un tableau pour stocker les actions sélectionnées pour chaque budget (Ex : selected_actions = [
    #     #[],  # Indice 0 : budget de 0 centime
    #     #[],  # Indice 1 : budget de 1 centime...
    selected_actions = [[] for _ in range(budget + 1)]

    # Compter le nombre total de combinaisons évaluées
    total_combinations = 0

    # Parcourir chaque action de la liste actions.
    for action in actions:
        cost = int(action['cost'])  # On récupère le coût de l'action
        profit = action['profit_amount']

        # Mettre à jour le tableau dp de manière descendante pour éviter d'écraser les données
        for budget_level in range(budget, cost - 1, -1): # Start = budget, stop = cost-1 (sinon coût exclus), step = -1
            total_combinations += 1
            # Vérifier si l'ajout de cette action au budget actuel augmente le profit maximal
            if max_profit_for_budget[budget_level - cost] + profit > max_profit_for_budget[budget_level]:
                # Mettre à jour le profit maximal pour ce niveau de budget en incluant cette action
                max_profit_for_budget[budget_level] = max_profit_for_budget[budget_level - cost] + profit
                # Mettre à jour la liste d'actions sélectionnées pour atteindre ce profit maximal à ce niveau de budget
                selected_actions[budget_level] = selected_actions[budget_level - cost] + [action]

    # Le meilleur profit sera à dp[budget], avec les actions correspondantes
    return selected_actions[budget], max_profit_for_budget[budget], total_combinations

def display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations):

    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost / 100],  # Diviser par 100 pour afficher en euros
        "Profit de la meilleure combinaison (€)": [round(best_profit / 100, 2)]
    })

    # Deuxième tableau : Meilleure combinaison d'actions
    best_combination_dataframe = pd.DataFrame(best_combination)

    # Diviser les colonnes 'cost' et 'profit_amount' par 100 pour l'affichage en euros
    best_combination_dataframe['cost'] = best_combination_dataframe['cost'] / 100
    best_combination_dataframe['profit_amount'] = (best_combination_dataframe['profit_amount'] / 100).round(2)

    # Multiplier la colonne 'profit' par 100 et réintégration du symbole % pour l'affichage en pourcentage
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

        # Démarrer le chronomètre uniquement pour l'algorithme
        start_time = time.time()
        # Trouver la meilleure combinaison d'actions dans le budget avec programmation dynamique
        best_combination, best_profit, total_combinations = find_best_combination(actions)
        # Arrêter le chronomètre
        end_time = time.time()
        # Calculer la durée d'exécution
        execution_time = end_time - start_time

        # Calculer le coût total des actions sélectionnées
        best_combination_cost = sum(action['cost'] for action in best_combination)
        display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations)


if __name__ == "__main__":
    main(CSV_FILES)
