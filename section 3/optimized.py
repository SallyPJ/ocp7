import pandas as pd
from time import perf_counter


CSV_FILES = ["../datasets/actions_list.csv", "../datasets/dataset1_Python+P7.csv", "../datasets/dataset2_Python+P7.csv"]
BUDGET = 500 * 100  # Budget en centimes


def upload_data(file):
    """
    Charger et nettoyer les données
    :param file:
    :return:
    """
    # Charger les données et créer une copie du fichier
    dataframe = pd.read_csv(file).copy()

    # Renommer les colonnes des fichiers CSV
    column_mapping = {
        'Coût par action (en euros)': 'cost',
        'price': 'cost',
        'Actions #': 'name',
        'Bénéfice (après 2 ans)': 'profit',
    }
    dataframe.rename(columns=column_mapping, inplace=True)

    # Supprimer les lignes avec des valeurs manquantes
    dataframe.dropna(subset=['cost', 'profit'], inplace=True)

    # Convertir les valeurs des benefices, des pourcentages vers des décimales
    dataframe['profit'] = dataframe['profit'].astype(str).str.replace('%', '')
    dataframe['profit'] = pd.to_numeric(dataframe['profit'], errors='coerce') / 100

    # Supprimer les actions avec un coût de 0 ou inférieur, supérieur au budget
    # ou ayant un benefice négatif
    dataframe = dataframe[(dataframe['cost'] > 0) & (dataframe['cost'] <= BUDGET)
                          & (dataframe['profit'] > 0)]

    # Supprimer les doublons (basé sur la colonne 'name')
    dataframe = dataframe[~dataframe['name'].duplicated(keep=False)]

    # Convertir les valeurs des actions, des euros vers les centimes
    dataframe['cost'] = pd.to_numeric(dataframe['cost'], errors='coerce') * 100

    # Calculer le montant des bénéfices en centimes
    dataframe['profit_amount'] = dataframe['profit'] * dataframe['cost']

    return dataframe


def greedy_best_combination(actions, budget=BUDGET):
    """
    Algorithme glouton qui prend la meilleur combinaison.
    Cet algorithme trie les actions par leur ratio profit/coût en ordre décroissant,
    puis sélectionne les actions les plus rentables dans la limite du budget.
    :param actions:
    :param budget:
    :return best_combination: variable qui contient la meilleure combinaison d'actions
    :return total_profit: variable qui contient le montant total des bénéfices
    :return total_cost: variable qui contient le montant total d'une sélection d'actions
    :return total_combinations: compte le nombre de combinaisons
    """
    # Calculer le ratio profit/coût pour chaque action
    for action in actions:
        action['ratio'] = (action['profit_amount'] / action['cost']) if action['cost'] > 0 else 0

    # Trier les actions par rapport ratio profit/coût par ordre décroissant
    actions_sorted = sorted(actions, key=lambda x: x['ratio'], reverse=True)

    # Initialiser les variables.
    best_combination = []
    total_cost = 0
    total_profit = 0
    total_combinations = 0

    # Ajouter les actions dans la combinaison dans la limite du budget.
    for action in actions_sorted:
        total_combinations += 1
        if total_cost + action['cost'] <= budget:
            best_combination.append(action)
            total_cost += action['cost']
            total_profit += action['profit_amount']

    return best_combination, total_profit, total_cost, total_combinations


def knapsack_best_combination(actions, budget=BUDGET):
    """
    Algorithme sac à dos qui sélectionne la meilleure combinaison d'actions maximisant le profit
    sans dépasser le budget.
    :param actions:
    :param budget:
    :return selected_actions[budget]:
    :return max_profit_for_budget[budget]:
    :return total_combinations: compte le nombre de combinaisons
    """
    # Créer un tableau pour stocker le meilleur profit pour chaque budget (de 0 à 50000). Commence à 0 d'où le + 1
    max_profit_for_budget = [0] * (budget + 1)

    # Créer un tableau pour stocker les actions sélectionnées pour chaque budget (Ex : selected_actions = [
    #     #[],  # Indice 0 : budget de 0 centime
    #     #[],  # Indice 1 : budget de 1 centime...
    selected_actions = [[] for _ in range(budget + 1)]
    total_combinations = 0

    # Parcourir chaque action de la liste actions et récupérer le coût et le profit
    for action in actions:
        cost = int(action['cost'])
        profit = action['profit_amount']

        # Parcourir le tableau pour trouver le meilleur profit pour chaque budget
        # Start = budget, stop = cost-1 (sinon coût exclus), step = -1
        for budget_level in range(budget, cost - 1, -1):
            total_combinations += 1
            # Vérifier si l'ajout de cette action au budget actuel augmente le profit maximal
            if max_profit_for_budget[budget_level - cost] + profit > max_profit_for_budget[budget_level]:
                # Mettre à jour le profit maximal pour ce niveau de budget en incluant cette action
                max_profit_for_budget[budget_level] = max_profit_for_budget[budget_level - cost] + profit
                # Mettre à jour la liste d'actions sélectionnées pour atteindre ce profit maximal à ce niveau de budget
                selected_actions[budget_level] = selected_actions[budget_level - cost] + [action]

    return selected_actions[budget], max_profit_for_budget[budget], total_combinations


def display_results(algorithm_name, execution_time, best_combination, best_profit, best_combination_cost, total_combinations):
    """
    Affiche les résultats sous forme de deux tableaux.
    :param algorithm_name:
    :param execution_time:
    :param best_combination:
    :param best_profit:
    :param best_combination_cost:
    :param total_combinations:
    """

    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Algorithme": [algorithm_name],
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost / 100],
        "Profit de la meilleure combinaison (€)": [round(best_profit / 100, 2)]
    })

    # Second tableau : détails des actions sélectionnées
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
        df = upload_data(file)
        actions = df.to_dict('records')

        # Algorithme glouton
        start_time = perf_counter()
        best_combination, best_profit, best_combination_cost, total_combinations = greedy_best_combination(actions, budget=BUDGET)
        end_time = perf_counter()
        display_results("Algorithme glouton", end_time - start_time, best_combination, best_profit, best_combination_cost, total_combinations)

        # Algorithme sac à dos
        start_time = perf_counter()
        best_combination, best_profit, total_combinations = knapsack_best_combination(actions, budget=BUDGET)
        end_time = perf_counter()
        best_combination_cost = sum(action['cost'] for action in best_combination)
        display_results("Programmation dynamique", end_time - start_time, best_combination, best_profit, best_combination_cost, total_combinations)


if __name__ == "__main__":
    main(CSV_FILES)
