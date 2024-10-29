import pandas as pd
from itertools import combinations
import time
import matplotlib.pyplot as plt

CSV_FILE = "../datasets/actions_list.csv"
BUDGET = 500
# Charger et nettoyer les données
'''
Génération des combinaisons : O(2^n)
Calcul des profits : 0(n)
Complexité totale : O(2^n * n)
'''


def load_dataset(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe


def clean_dataset(dataframe):
    dataframe.rename(columns={'Coût par action (en euros)': 'cost', 'Bénéfice (après 2 ans)': 'profit'}, inplace=True)
    dataframe['cost'] = pd.to_numeric(dataframe['cost'], errors='coerce')
    dataframe['profit'] = dataframe['profit'].str.replace('%', '').astype(float) / 100
    dataframe['profit_amount'] = dataframe['profit'] * dataframe['cost']
    dataframe.dropna(subset=['cost', 'profit'], inplace=True)
    return dataframe


def calculate_profit_combinations(combination):
    # Calcule le coût total de toutes les actions d'une combinaison
    total_cost = sum(action['cost'] for action in combination)
    # Calcule le profit total de la combinaison
    total_profit = sum(action['profit_amount'] for action in combination)
    return total_cost, total_profit


def find_best_combination(actions, budget=BUDGET):
    best_profit = 0
    best_combination = []
    total_combinations = 0

    # Générer toutes les combinaisons possibles,
    # r va tester les combinaisons de 1 à n actions
    # Les combinaisons de taille r : Si actions = ["action1", "action2", "action3"]
    # et r = 2, alors elle créera : ("action1", "action2"), ("action1", "action3"), ("action2", "action3").
    #combinations de itertools est un outil qui permet de créer tous les groupes possibles d’éléments dans une liste,
    # en choisissant un nombre fixe d’éléments à la fois. Par exemple, si on veut créer des groupes de 2 éléments à partir d'une liste d'actions,
    # combinations va générer tous les groupes de 2 possibles, sans répéter les mêmes éléments dans un ordre différent.
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


def display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations):
    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost],
        "Profit de la meilleure combinaison (€)": [best_profit]
    })

    # Deuxième tableau : Meilleure combinaison d'actions
    best_combination_dataframe = pd.DataFrame(best_combination)

    print("Résumé des résultats :")
    print(summary_dataframe.to_string())
    print("Meilleure combinaison d'actions :")
    print(best_combination_dataframe)

def plot_complexity(sizes, execution_times):
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
        best_combination, best_profit, best_combination_cost, total_combinations = find_best_combination(sample_actions, BUDGET)
        end_time = time.time()
        execution_time = end_time - start_time
        sizes.append(size)
        execution_times.append(execution_time)

    plot_complexity(sizes, execution_times)
    display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations)


if __name__ == "__main__":
    main()
