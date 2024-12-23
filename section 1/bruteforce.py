import pandas as pd
from itertools import combinations
import time
import matplotlib.pyplot as plt

CSV_FILE = "../datasets/actions_list.csv"
BUDGET = 500


def load_dataset(csv_file):
    """
    Charger les données
    :param csv_file:
    :return dataframe:
    """
    dataframe = pd.read_csv(csv_file)
    return dataframe


def clean_dataset(dataframe):
    """
    Nettoyer les données
    :param dataframe:
    :return dataframe:
    """
    dataframe.rename(columns={'Coût par action (en euros)': 'cost',
                              'Bénéfice (après 2 ans)': 'profit'}, inplace=True)
    dataframe['cost'] = pd.to_numeric(dataframe['cost'], errors='coerce')
    dataframe['profit'] = dataframe['profit'].str.replace('%', '').astype(float) / 100
    dataframe['profit_amount'] = dataframe['profit'] * dataframe['cost']
    dataframe.dropna(subset=['cost', 'profit'], inplace=True)
    return dataframe


def calculate_profit_combinations(combination):
    """
    Calculer le profit généré par chaque combinaison
    :param combination:
    :return total_cost:
    :return total_profit:
    """
    # Calcule le coût total de toutes les actions d'une combinaison
    total_cost = sum(action['cost'] for action in combination)

    # Calcule le profit total de la combinaison
    total_profit = sum(action['profit_amount'] for action in combination)
    return total_cost, total_profit


def find_best_combination(actions, budget=BUDGET):
    """
    Générer toutes les combinaisons possibles.
    :param actions:
    :param budget:
    :return:
    """
    best_profit = 0
    best_combination = []
    total_combinations = 0

    # r va tester les combinaisons de 1 à n actions
    # Combinations de itertools est un outil qui permet de créer tous les groupes possibles d’éléments dans une liste,
    # sans répéter les éléments dans un ordre différent.
    for r in range(1, len(actions) + 1):
        for combination in combinations(actions, r):
            total_combinations += 1
            total_cost, total_profit = calculate_profit_combinations(combination)

            # Vérifier si le coût total est inférieur ou égal au budget
            if total_cost <= budget and total_profit > best_profit:
                best_profit = total_profit
                best_combination = combination
                best_combination_cost = total_cost

    return best_combination, best_profit, best_combination_cost, total_combinations


def display_results(execution_time, best_combination, best_profit,
                    best_combination_cost, total_combinations):
    """
    Afficher les résultats sous forme de tableaux
    :param execution_time:
    :param best_combination:
    :param best_profit:
    :param best_combination_cost:
    :param total_combinations:
    :return:
    """
    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)":
            [best_combination_cost],
        "Profit de la meilleure combinaison (€)": [best_profit]
    })

    # Deuxième tableau : Meilleure combinaison d'actions
    best_combination_dataframe = pd.DataFrame(best_combination)

    print("Résumé des résultats :")
    print(summary_dataframe.to_string())
    print("Meilleure combinaison d'actions :")
    print(best_combination_dataframe)


def plot_complexity(sizes, execution_times):
    """
    Genérer le graphique de la complexité temporelle
    :param sizes:
    :param execution_times:
    :return:
    """
    plt.plot(sizes, execution_times, marker='o')
    plt.xlabel("Taille de l'entrée (nombre d'actions)")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.title("Complexité Temporelle de l'Algorithme")
    plt.grid(True)
    plt.show()


def main():
    raw_data = load_dataset(CSV_FILE)
    cleaned_data = clean_dataset(raw_data)
    actions = cleaned_data.to_dict('records')
    sizes = []
    execution_times = []
    step = 1
    for size in range(step, len(actions) + 1, step):
        sample_actions = actions[:size]
        start_time = time.time()
        (best_combination, best_profit, best_combination_cost,
         total_combinations) = find_best_combination(sample_actions, BUDGET)
        end_time = time.time()
        execution_time = end_time - start_time
        sizes.append(size)
        execution_times.append(execution_time)

    plot_complexity(sizes, execution_times)
    display_results(execution_time, best_combination,
                    best_profit, best_combination_cost, total_combinations)

if __name__ == "__main__":
    main()
