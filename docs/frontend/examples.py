import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dp_engine.dp_core import DPEngine
from src.dp_engine.epsilon_manager import EpsilonTracker
import numpy as np


def example_1_basic_usage():
    """
    Exemple 1: Utilisation basique
    """
    print("\n" + "="*70)
    print("EXEMPLE 1: UTILISATION BASIQUE")
    print("="*70)
    
    # Créer le moteur
    engine = DPEngine(epsilon=1.0)
    
    # Count
    true_count = 1000
    noisy_count = engine.dp_count(true_count)
    print(f"\n1. Count:")
    print(f"   Vrai: {true_count}")
    print(f"   Avec DP: {noisy_count}")
    print(f"   Erreur: {abs(true_count - noisy_count)}")
    
    # Mean
    ages = [25, 30, 35, 40, 45, 50, 55, 60]
    true_mean = np.mean(ages)
    noisy_mean = engine.dp_mean(ages, 0, 100)
    print(f"\n2. Mean:")
    print(f"   Vrai: {true_mean:.2f}")
    print(f"   Avec DP: {noisy_mean:.2f}")
    print(f"   Erreur: {abs(true_mean - noisy_mean):.2f}")


def example_2_epsilon_comparison():
    """
    Exemple 2: Comparaison de différents epsilons
    """
    print("\n" + "="*70)
    print("EXEMPLE 2: IMPACT DE EPSILON")
    print("="*70)
    
    true_value = 500
    epsilons = [0.1, 0.5, 1.0, 5.0, 10.0]
    
    print(f"\nValeur vraie: {true_value}")
    print(f"{'Epsilon':<10} {'Résultat DP':<15} {'Erreur':<10}")
    print("-" * 35)
    
    for eps in epsilons:
        engine = DPEngine(epsilon=eps)
        noisy = engine.dp_count(true_value)
        error = abs(true_value - noisy)
        print(f"{eps:<10.1f} {noisy:<15} {error:<10}")


def example_3_epsilon_manager():
    """
    Exemple 3: Utilisation de l'Epsilon Manager
    """
    print("\n" + "="*70)
    print("EXEMPLE 3: EPSILON MANAGER")
    print("="*70)
    
    # Créer tracker
    tracker = EpsilonTracker(total_budget=5.0)
    user_id = "analyst_1"
    
    print(f"\nBudget initial: {tracker.get_remaining_budget(user_id):.2f}ε")
    
    # Requête 1
    print("\n1. Requête Count (ε=1.0)")
    if tracker.consume_budget(user_id, 1.0, 'count'):
        print(f" Succès - Reste: {tracker.get_remaining_budget(user_id):.2f}ε")
    
    # Requête 2
    print("\n2. Requête Mean (ε=2.0)")
    if tracker.consume_budget(user_id, 2.0, 'mean'):
        print(f" Succès - Reste: {tracker.get_remaining_budget(user_id):.2f}ε")
    
    # Requête 3 (doit échouer)
    print("\n3. Requête Sum (ε=3.0) - Devrait échouer")
    if tracker.consume_budget(user_id, 3.0, 'sum'):
        print(f" Succès")
    else:
        print(f" Échec - Budget insuffisant")
    
    # Afficher historique
    print("\nHistorique des requêtes:")
    history = tracker.get_user_history(user_id)
    for i, query in enumerate(history, 1):
        print(f"   {i}. {query['query_type']} - ε={query['epsilon_used']}")


def example_4_django_integration():
    """
    Exemple 4: Simulation d'intégration Django
    """
    print("\n" + "="*70)
    print("EXEMPLE 4: SIMULATION DJANGO API")
    print("="*70)
    
    # Simuler des données Django
    class FakePatient:
        def __init__(self, age, cost):
            self.age = age
            self.cost = cost
    
    # Créer faux patients
    patients = [FakePatient(np.random.randint(18, 90), np.random.uniform(1000, 50000)) 
                for _ in range(1000)]
    
    # Extraire données
    ages = [p.age for p in patients]
    costs = [p.cost for p in patients]
    
    print(f"\nDataset: {len(patients)} patients")
    print(f"   Âge moyen réel: {np.mean(ages):.1f} ans")
    print(f"   Coût moyen réel: ${np.mean(costs):,.2f}")
    
    # Appliquer DP
    engine = DPEngine(epsilon=1.0)
    tracker = EpsilonTracker(total_budget=10.0)
    
    user_id = "api_user"
    
    # Simuler endpoint /api/count
    print("\nGET /api/count")
    if tracker.check_budget(user_id, 1.0):
        noisy_count = engine.dp_count(len(patients))
        tracker.consume_budget(user_id, 1.0, 'count')
        print(f"   Response: {{'count': {noisy_count}, 'epsilon_used': 1.0}}")
    
    # Simuler endpoint /api/mean_age
    print("\nGET /api/mean_age")
    if tracker.check_budget(user_id, 1.0):
        noisy_mean_age = engine.dp_mean(ages, 0, 120)
        tracker.consume_budget(user_id, 1.0, 'mean')
        print(f"   Response: {{'mean_age': {noisy_mean_age:.1f}, 'epsilon_used': 1.0}}")
    
    # Simuler endpoint /api/mean_cost
    print("\nGET /api/mean_cost")
    if tracker.check_budget(user_id, 1.0):
        noisy_mean_cost = engine.dp_mean(costs, 0, 100000)
        tracker.consume_budget(user_id, 1.0, 'mean')
        print(f"   Response: {{'mean_cost': ${noisy_mean_cost:,.2f}, 'epsilon_used': 1.0}}")
    
    # Afficher budget restant
    print(f"\nBudget restant: {tracker.get_remaining_budget(user_id):.2f}ε")


def example_5_complete_workflow():
    """
    Exemple 5: Workflow complet
    """
    print("\n" + "="*70)
    print("EXEMPLE 5: WORKFLOW COMPLET")
    print("="*70)
    
    # Charger données
    data_path = '../data/patients.csv'
    if os.path.exists(data_path):
        import pandas as pd
        df = pd.read_csv(data_path)
        print(f"\nDonnées chargées: {len(df)} patients")
    else:
        print("\nFichier patients.csv introuvable, utilisation de données simulées")
        df = None
        ages = list(np.random.randint(18, 95, 1000))
        costs = list(np.random.uniform(500, 50000, 1000))
    
    # Initialiser
    engine = DPEngine(epsilon=1.0)
    tracker = EpsilonTracker(total_budget=10.0)
    user_id = "researcher_1"
    
    print(f"\nInitialisation:")
    print(f"   Epsilon: {engine.epsilon}")
    print(f"   Budget: {tracker.total_budget}ε")
    
    # Workflow d'analyse
    print(f"\nWorkflow d'analyse:")
    
    if df is not None:
        ages = df['age'].tolist()
        costs = df['treatment_cost'].tolist()
    
    results = {}
    
    # 1. Count total
    if tracker.check_budget(user_id, 1.0):
        results['total_patients'] = engine.dp_count(len(ages))
        tracker.consume_budget(user_id, 1.0, 'count')
        print(f"   1. Total patients: {results['total_patients']}")
    
    # 2. Mean age
    if tracker.check_budget(user_id, 1.0):
        results['mean_age'] = engine.dp_mean(ages, 0, 120)
        tracker.consume_budget(user_id, 1.0, 'mean')
        print(f"   2. Âge moyen: {results['mean_age']:.1f} ans")
    
    # 3. Median age
    if tracker.check_budget(user_id, 1.0):
        results['median_age'] = engine.dp_median(ages, 0, 120)
        tracker.consume_budget(user_id, 1.0, 'median')
        print(f"   3. Âge médian: {results['median_age']:.1f} ans")
    
    # 4. Mean cost
    if tracker.check_budget(user_id, 1.0):
        results['mean_cost'] = engine.dp_mean(costs, 0, 100000)
        tracker.consume_budget(user_id, 1.0, 'mean')
        print(f"   4. Coût moyen: ${results['mean_cost']:,.2f}")
    
    # 5. Total cost
    if tracker.check_budget(user_id, 1.0):
        results['total_cost'] = engine.dp_sum(costs, 0, 100000)
        tracker.consume_budget(user_id, 1.0, 'sum')
        print(f"   5. Coût total: ${results['total_cost']:,.2f}")
    
    # Résumé final
    print(f"\nRésumé:")
    print(f"   Requêtes effectuées: {len(results)}")
    print(f"   Epsilon consommé: {tracker.get_used_budget(user_id):.2f}ε")
    print(f"   Budget restant: {tracker.get_remaining_budget(user_id):.2f}ε")


def run_all_examples():
    """
    Lance tous les exemples
    """
    print("="*70)
    print("EXEMPLES D'UTILISATION DU DP ENGINE")
    print("="*70)
    
    example_1_basic_usage()
    example_2_epsilon_comparison()
    example_3_epsilon_manager()
    example_4_django_integration()
    example_5_complete_workflow()
    
    print("\n" + "="*70)
    print("TOUS LES EXEMPLES TERMINÉS!")
    print("="*70)


if __name__ == "__main__":
    run_all_examples()