"""
Tests unitaires pour le DP Engine
Personne 3 - Tests
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import numpy as np
from dp_engine.dp_core import DPEngine
from dp_engine.epsilon_manager import EpsilonTracker


# ==================== TESTS DP ENGINE ====================

def test_dp_engine_initialization():
    """Test: Le moteur DP s'initialise correctement"""
    engine = DPEngine(epsilon=1.0)
    assert engine.epsilon == 1.0
    print("Test initialisation DP Engine")


def test_laplace_noise_is_random():
    """Test: Le bruit de Laplace est bien aléatoire"""
    engine = DPEngine(epsilon=1.0)
    noises = [engine.add_laplace_noise(0, sensitivity=1.0) for _ in range(100)]
    
    # Les bruits doivent être différents
    assert len(set(noises)) > 90  # Au moins 90% différents
    print("Test bruit de Laplace aléatoire")


def test_dp_count_non_negative():
    """Test: DP Count retourne toujours >= 0"""
    engine = DPEngine(epsilon=1.0)
    
    for _ in range(100):
        result = engine.dp_count(10)
        assert result >= 0
    
    print("Test DP Count non-négatif")


def test_dp_count_approximate():
    """Test: DP Count est proche de la vraie valeur"""
    engine = DPEngine(epsilon=1.0)
    true_count = 1000
    
    # Faire 100 requêtes et vérifier la moyenne
    noisy_counts = [engine.dp_count(true_count) for _ in range(100)]
    mean_noisy = np.mean(noisy_counts)
    
    # La moyenne des résultats bruités doit être proche du vrai compte
    assert abs(mean_noisy - true_count) < 50  # Tolérance de 5%
    print("Test DP Count approximation")


def test_dp_mean_clipping():
    """Test: DP Mean clippe correctement les valeurs"""
    engine = DPEngine(epsilon=1.0)
    values = [10, 20, 30, 40, 50, 1000]  # 1000 est outlier
    
    result = engine.dp_mean(values, lower=0, upper=100)
    
    # La valeur doit être dans les bornes raisonnables
    assert -50 <= result <= 150  # Avec le bruit
    print("Test DP Mean clipping")


def test_dp_sum_sensitivity():
    """Test: DP Sum utilise la bonne sensibilité"""
    engine = DPEngine(epsilon=1.0)
    values = [10, 20, 30, 40, 50]
    
    result = engine.dp_sum(values, lower=0, upper=100)
    true_sum = sum(values)
    
    # Le résultat doit être raisonnablement proche
    assert abs(result - true_sum) < 200  # Sensibilité = 100
    print("Test DP Sum sensibilité")


def test_dp_median_in_range():
    """Test: DP Median retourne une valeur dans les bornes"""
    engine = DPEngine(epsilon=1.0)
    values = [25, 30, 35, 40, 45, 50, 55, 60]
    
    result = engine.dp_median(values, lower=0, upper=100)
    
    assert 0 <= result <= 100
    print("Test DP Median dans les bornes")


def test_dp_histogram_length():
    """Test: DP Histogram retourne le bon nombre de bins"""
    engine = DPEngine(epsilon=1.0)
    values = list(range(100))
    
    bin_edges, noisy_hist = engine.dp_histogram(values, bins=10, lower=0, upper=100)
    
    assert len(noisy_hist) == 10
    assert len(bin_edges) == 11  # n+1 edges pour n bins
    print("Test DP Histogram longueur")


def test_dp_variance_non_negative():
    """Test: DP Variance est toujours >= 0"""
    engine = DPEngine(epsilon=2.0)  # Plus d'epsilon car consomme 2x
    values = [25, 30, 35, 40, 45, 50]
    
    result = engine.dp_variance(values, lower=0, upper=100)
    
    assert result >= 0
    print("Test DP Variance non-négatif")


def test_dp_percentile_order():
    """Test: Percentiles croissants donnent des valeurs croissantes (en moyenne)"""
    engine = DPEngine(epsilon=5.0)  # Plus d'epsilon pour moins de bruit
    values = list(range(1, 101))
    
    p25 = np.mean([engine.dp_percentile(values, 25, 0, 100) for _ in range(20)])
    p50 = np.mean([engine.dp_percentile(values, 50, 0, 100) for _ in range(20)])
    p75 = np.mean([engine.dp_percentile(values, 75, 0, 100) for _ in range(20)])
    
    assert p25 < p50 < p75
    print("Test DP Percentile ordre")


def test_epsilon_impact():
    """Test: Plus epsilon est petit, plus il y a de bruit"""
    values = [100] * 50
    
    engine_low = DPEngine(epsilon=0.1)
    engine_high = DPEngine(epsilon=10.0)
    
    # Faire 100 mesures
    errors_low = [abs(engine_low.dp_mean(values, 0, 200) - 100) for _ in range(100)]
    errors_high = [abs(engine_high.dp_mean(values, 0, 200) - 100) for _ in range(100)]
    
    # L'erreur moyenne doit être plus grande avec epsilon petit
    assert np.mean(errors_low) > np.mean(errors_high)
    print("Test impact de epsilon")


# ==================== TESTS EPSILON MANAGER ====================

def test_epsilon_tracker_initialization():
    """Test: Epsilon Tracker s'initialise correctement"""
    tracker = EpsilonTracker(total_budget=10.0)
    assert tracker.total_budget == 10.0
    assert len(tracker.user_budgets) == 0
    print("Test initialisation Epsilon Tracker")


def test_check_budget_new_user():
    """Test: Nouveau utilisateur a le budget complet"""
    tracker = EpsilonTracker(total_budget=5.0)
    assert tracker.check_budget('user1', 3.0) == True
    assert tracker.check_budget('user1', 6.0) == False
    print("Test budget nouvel utilisateur")


def test_consume_budget_success():
    """Test: Consommation de budget réussie"""
    tracker = EpsilonTracker(total_budget=5.0)
    
    result = tracker.consume_budget('user1', 2.0, 'count')
    assert result == True
    assert tracker.get_used_budget('user1') == 2.0
    assert tracker.get_remaining_budget('user1') == 3.0
    print("Test consommation budget réussie")


def test_consume_budget_failure():
    """Test: Consommation échoue si budget insuffisant"""
    tracker = EpsilonTracker(total_budget=5.0)
    
    tracker.consume_budget('user1', 4.0, 'count')
    result = tracker.consume_budget('user1', 2.0, 'mean')  # Doit échouer
    
    assert result == False
    assert tracker.get_used_budget('user1') == 4.0  # Pas changé
    print("Test consommation budget échouée")


def test_multiple_users():
    """Test: Plusieurs utilisateurs indépendants"""
    tracker = EpsilonTracker(total_budget=10.0)
    
    tracker.consume_budget('user1', 3.0, 'count')
    tracker.consume_budget('user2', 5.0, 'mean')
    
    assert tracker.get_remaining_budget('user1') == 7.0
    assert tracker.get_remaining_budget('user2') == 5.0
    print("Test utilisateurs multiples")


def test_query_history():
    """Test: L'historique des requêtes est enregistré"""
    tracker = EpsilonTracker(total_budget=10.0)
    
    tracker.consume_budget('user1', 1.0, 'count', {'filter': 'age>30'})
    tracker.consume_budget('user1', 2.0, 'mean', {'column': 'cost'})
    
    history = tracker.get_user_history('user1')
    assert len(history) == 2
    assert history[0]['query_type'] == 'count'
    assert history[1]['query_type'] == 'mean'
    print("Test historique requêtes")


def test_reset_budget_single_user():
    """Test: Reset du budget d'un utilisateur"""
    tracker = EpsilonTracker(total_budget=5.0)
    
    tracker.consume_budget('user1', 3.0, 'count')
    tracker.reset_budget('user1')
    
    assert tracker.get_remaining_budget('user1') == 5.0
    print("Test reset budget utilisateur")


def test_reset_budget_all_users():
    """Test: Reset de tous les budgets"""
    tracker = EpsilonTracker(total_budget=5.0)
    
    tracker.consume_budget('user1', 2.0, 'count')
    tracker.consume_budget('user2', 3.0, 'mean')
    tracker.reset_budget()  # Sans user_id
    
    assert len(tracker.user_budgets) == 0
    assert len(tracker.query_history) == 0
    print("Test reset tous les budgets")


def test_get_stats():
    """Test: Statistiques correctes"""
    tracker = EpsilonTracker(total_budget=10.0)
    
    tracker.consume_budget('user1', 2.0, 'count')
    tracker.consume_budget('user2', 3.0, 'mean')
    tracker.consume_budget('user1', 1.0, 'sum')
    
    stats = tracker.get_stats()
    assert stats['total_users'] == 2
    assert stats['total_queries'] == 3
    assert stats['total_epsilon_consumed'] == 6.0
    print("Test statistiques")


def test_sequential_composition():
    """Test: Composition séquentielle (epsilons s'additionnent)"""
    tracker = EpsilonTracker(total_budget=10.0)
    
    tracker.consume_budget('user1', 1.0, 'count')
    tracker.consume_budget('user1', 2.0, 'mean')
    tracker.consume_budget('user1', 3.0, 'sum')
    
    # Total consommé = 1 + 2 + 3 = 6
    assert tracker.get_used_budget('user1') == 6.0
    assert tracker.get_remaining_budget('user1') == 4.0
    print("Test composition séquentielle")


# ==================== EXÉCUTION DES TESTS ====================
if __name__ == "__main__":
    print("="*70)
    print("LANCEMENT DES TESTS UNITAIRES")
    print("="*70)
    
    # Tests DP Engine
    print("\nTests DP Engine:")
    test_dp_engine_initialization()
    test_laplace_noise_is_random()
    test_dp_count_non_negative()
    test_dp_count_approximate()
    test_dp_mean_clipping()
    test_dp_sum_sensitivity()
    test_dp_median_in_range()
    test_dp_histogram_length()
    test_dp_variance_non_negative()
    test_dp_percentile_order()
    test_epsilon_impact()
    
    # Tests Epsilon Manager
    print("\nTests Epsilon Manager:")
    test_epsilon_tracker_initialization()
    test_check_budget_new_user()
    test_consume_budget_success()
    test_consume_budget_failure()
    test_multiple_users()
    test_query_history()
    test_reset_budget_single_user()
    test_reset_budget_all_users()
    test_get_stats()
    test_sequential_composition()
    
    print("\n" + "="*70)
    print("TOUS LES TESTS SONT PASSÉS!")
    print(f"21 TESTS UNITAIRES RÉUSSIS")
    print("="*70)