import pandas as pd
import time

CSV_FILE = "../datasets/actions_list.csv"
BUDGET = 50000  # Le budget est maintenant en centimes (500 euros * 100)

def load_dataset(csv_file):
    dataframe = pd.read_csv(csv_file)
    return dataframe

def clean_dataset(dataframe):
    dataframe.rename(columns={'Coût par action (en euros)': 'cost', 'Bénéfice (après 2 ans)': 'profit'}, inplace=True)
    # Convertir le coût en centimes
    dataframe['cost'] = pd.to_numeric(dataframe['cost'], errors='coerce') * 100  # Multiplie par 100 pour avoir les centimes
    dataframe['profit'] = dataframe['profit'].str.replace('%', '').astype(float) / 100
    dataframe['profit_amount'] = dataframe['profit'] * dataframe['cost']
    dataframe.dropna(subset=['cost', 'profit'], inplace=True)
    return dataframe

# Fonction pour trouver la meilleure combinaison d'actions avec programmation dynamique
def find_best_combination(actions, budget=BUDGET):
    # Créer un tableau pour stocker le meilleur profit pour chaque budget (de 0 à 50000). Commence à 0 d'où le + 1
    max_profit_for_budget = [0] * (budget + 1)
    # Créer un tableau pour stocker les actions sélectionnées pour chaque budget
    #selected_actions = [
    #[],  # Indice 0 : budget de 0 centime
    #[],  # Indice 1 : budget de 1 centime
    #"[],  # Indice 2 : budget de 2 centimes
    #"...
    #[],  # Indice 500 : budget de 500 centimes
#]
    selected_actions = [[] for _ in range(budget + 1)]
    # Variable pour compter le nombre total de combinaisons évaluées
    total_combinations = 0

    # Parcourir chaque action de la liste action.
    for action in actions:
        cost = int(action['cost'])  # On récupère le coût de l'action
        profit = action['profit_amount']

        # Mettre à jour le tableau dp de manière descendante pour éviter d'écraser les données
        for budget_level in range(budget, cost - 1, -1): # Start = budget, stop = cost-1 (sinon coût exclus), step = -1
            total_combinations += 1
            if max_profit_for_budget[budget_level - cost] + profit > max_profit_for_budget[budget_level]:
                max_profit_for_budget[budget_level] = max_profit_for_budget[budget_level - cost] + profit
                selected_actions[budget_level] = selected_actions[budget_level - cost] + [action]

    # Le meilleur profit sera à dp[budget], avec les actions correspondantes
    return selected_actions[budget], max_profit_for_budget[budget], total_combinations

def display_results(execution_time, best_combination, best_profit, best_combination_cost, total_combinations):
    # Premier tableau : Résumé des résultats
    summary_dataframe = pd.DataFrame({
        "Durée d'exécution (s)": [execution_time],
        "Nombre de combinaisons": [total_combinations],
        "Coût total de la meilleur combinaison d'actions (€)": [best_combination_cost / 100],  # Diviser par 100 pour afficher en euros
        "Profit de la meilleure combinaison (€)": [best_profit/100]
    })

    # Deuxième tableau : Meilleure combinaison d'actions
    best_combination_dataframe = pd.DataFrame(best_combination)

    print("Résumé des résultats :")
    print(summary_dataframe.to_string())
    print("Meilleure combinaison d'actions :")
    print(best_combination_dataframe)

def main(CSV_FILE):
    raw_data = load_dataset(CSV_FILE)
    cleaned_data = clean_dataset(raw_data)
    actions = cleaned_data.to_dict('records')

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
    main(CSV_FILE)