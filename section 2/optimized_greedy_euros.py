import pandas as pd
import time

CSV_FILE = "../datasets/actions_list.csv"
BUDGET = 500


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
    total_combination = 0

    # Ajouter les actions dans la combinaison tant que le budget le permet
    for action in actions_sorted:
        total_combination += 1
        if total_cost + action['cost'] <= budget:
            best_combination.append(action)
            total_cost += action['cost']
            total_profit += action['profit_amount']

    return best_combination, total_profit, total_cost, total_combination


def display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combination):
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combination],
        "Coût total de la meilleure combinaison d'actions (€)": [best_combination_cost],
        "Profit de la meilleure combinaison (€)": [best_profit]
    })
    best_combination_dataframe = pd.DataFrame(best_combination)

    print("Résumé des résultats :")
    print(summary_dataframe.to_string())
    print("Meilleure combinaison d'actions :")
    print(best_combination_dataframe)


def main():
    raw_data = load_dataset(CSV_FILE)
    cleaned_data = clean_dataset(raw_data)
    actions = cleaned_data.to_dict('records')

    start_time = time.time()
    best_combination, best_profit, best_combination_cost, total_combination = greedy_best_combination(actions, BUDGET)
    end_time = time.time()
    execution_time = end_time - start_time
    display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combination)


if __name__ == "__main__":
    main()