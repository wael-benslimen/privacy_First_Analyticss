"""
Moteur de Differential Privacy
Personne 3 - DP Engine Core
"""
import numpy as np
from typing import List

class DPEngine:
    """Moteur pour appliquer la Differential Privacy"""
    
    def __init__(self, epsilon: float = 1.0):
        """
        Initialise le moteur DP
        
        Args:
            epsilon: Budget de confidentialité (plus petit = plus privé)
                    Valeurs typiques: 0.1 (très privé) à 10.0 (moins privé)
        """
        self.epsilon = epsilon
        print(f"DP Engine initialisé avec epsilon={epsilon}")
    
    def add_laplace_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """
        Ajoute du bruit de Laplace (mécanisme principal de DP)
        
        Formule: Laplace(0, sensitivity/epsilon)
        
        Args:
            value: Valeur vraie à protéger
            sensitivity: Sensibilité de la requête (combien une personne peut changer le résultat)
            
        Returns:
            Valeur bruitée pour protéger la vie privée
        """
        # Calculer l'échelle du bruit
        scale = sensitivity / self.epsilon
        
        # Générer le bruit de Laplace
        noise = np.random.laplace(loc=0, scale=scale)
        
        return value + noise
    
    def dp_count(self, count: int) -> int:
        """
        Compte avec Differential Privacy
        
        Sensibilité = 1 (ajouter/retirer une personne change le compte de ±1)
        
        Args:
            count: Nombre vrai (ex: nombre de patients)
            
        Returns:
            Compte bruité (toujours >= 0)
        """
        noisy_count = self.add_laplace_noise(float(count), sensitivity=1.0)
        
        # Garantir que le compte est non-négatif et entier
        return max(0, int(round(noisy_count)))
    
    def dp_mean(self, values: List[float], lower: float, upper: float) -> float:
        """
        Moyenne avec Differential Privacy
        
        Args:
            values: Liste de valeurs (ex: âges, coûts)
            lower: Borne inférieure pour le clipping
            upper: Borne supérieure pour le clipping
            
        Returns:
            Moyenne bruitée
        """
        if len(values) == 0:
            return 0.0
        
        # Étape 1: Clipper les valeurs pour borner la sensibilité
        clipped_values = np.clip(values, lower, upper)
        
        # Étape 2: Calculer la moyenne vraie
        true_mean = np.mean(clipped_values)
        
        # Étape 3: Sensibilité de la moyenne = (upper - lower) / n
        sensitivity = (upper - lower) / len(values)
        
        # Étape 4: Ajouter le bruit
        return self.add_laplace_noise(true_mean, sensitivity)
    
    def dp_sum(self, values: List[float], lower: float, upper: float) -> float:
        """
        Somme avec Differential Privacy
        
        Args:
            values: Liste de valeurs
            lower: Borne inférieure pour clipping
            upper: Borne supérieure pour clipping
            
        Returns:
            Somme bruitée
        """
        if len(values) == 0:
            return 0.0
        
        # Clipper les valeurs
        clipped_values = np.clip(values, lower, upper)
        
        # Calculer la somme vraie
        true_sum = np.sum(clipped_values)
        
        # Sensibilité = range d'une valeur
        sensitivity = upper - lower
        
        # Ajouter bruit
        return self.add_laplace_noise(true_sum, sensitivity)
    
    def dp_median(self, values: List[float], lower: float, upper: float) -> float:
        """
        Médiane avec mécanisme exponentiel (plus avancé)
        
        Args:
            values: Liste de valeurs
            lower: Borne inférieure
            upper: Borne supérieure
            
        Returns:
            Médiane approximative avec DP
        """
        if len(values) == 0:
            return 0.0
        
        # Clipper les valeurs
        clipped = np.clip(values, lower, upper)
        sorted_values = np.sort(clipped)
        
        # Créer des candidats pour la médiane
        candidates = np.linspace(lower, upper, 100)
        
        # Score: distance à la médiane (moins c'est mieux)
        def score_function(candidate):
            return -sum(abs(v - candidate) for v in sorted_values)
        
        scores = np.array([score_function(c) for c in candidates])
        
        # Mécanisme exponentiel: probabilités selon exp(epsilon * score / sensitivity)
        sensitivity = upper - lower
        probabilities = np.exp(scores * self.epsilon / (2 * sensitivity))
        probabilities = probabilities / probabilities.sum()
        
        # Échantillonner
        return np.random.choice(candidates, p=probabilities)
    
    def dp_histogram(self, values: List[float], bins: int, lower: float, upper: float) -> tuple:
        """
        Histogramme avec DP (bruiter chaque bin)
        
        Args:
            values: Liste de valeurs
            bins: Nombre de bins
            lower: Borne inférieure
            upper: Borne supérieure
            
        Returns:
            (bin_edges, noisy_counts)
        """
        # Créer histogramme vrai
        hist, bin_edges = np.histogram(
            values, 
            bins=bins, 
            range=(lower, upper)
        )
        
        # Bruiter chaque bin (sensibilité = 1 par bin)
        noisy_hist = [self.dp_count(int(count)) for count in hist]
        
        return bin_edges, noisy_hist
    
    def dp_variance(self, values: List[float], lower: float, upper: float) -> float:
        """
        Variance avec DP
        
        Note: Consomme 2*epsilon (une fois pour la moyenne, une fois pour variance)
        
        Args:
            values: Liste de valeurs
            lower: Borne inférieure
            upper: Borne supérieure
            
        Returns:
            Variance approximative avec DP
        """
        if len(values) == 0:
            return 0.0
        
        # Clipper
        clipped = np.clip(values, lower, upper)
        
        # Calculer moyenne avec DP (epsilon/2)
        engine_half = DPEngine(epsilon=self.epsilon/2)
        dp_mean_val = engine_half.dp_mean(list(clipped), lower, upper)
        
        # Calculer variance
        squared_diffs = [(v - dp_mean_val)**2 for v in clipped]
        dp_variance_val = engine_half.dp_mean(
            squared_diffs, 
            0, 
            (upper - lower)**2
        )
        
        return max(0, dp_variance_val)
    
    def dp_percentile(self, values: List[float], percentile: float, lower: float, upper: float) -> float:
        """
        Percentile avec DP (ex: 25e, 50e, 75e percentile)
        
        Args:
            values: Liste de valeurs
            percentile: Percentile désiré (0-100)
            lower: Borne inférieure
            upper: Borne supérieure
            
        Returns:
            Valeur du percentile avec DP
        """
        if len(values) == 0:
            return 0.0
        
        clipped = np.clip(values, lower, upper)
        sorted_values = np.sort(clipped)
        
        # Cible: percentile% des valeurs doivent être sous le résultat
        target_count = len(values) * (percentile / 100)
        
        # Créer candidats
        candidates = np.linspace(lower, upper, 100)
        
        # Score
        def score_function(candidate):
            count_below = np.sum(sorted_values <= candidate)
            return -abs(count_below - target_count)
        
        scores = np.array([score_function(c) for c in candidates])
        
        # Mécanisme exponentiel
        sensitivity = upper - lower
        probabilities = np.exp(scores * self.epsilon / (2 * sensitivity))
        probabilities = probabilities / probabilities.sum()
        
        return np.random.choice(candidates, p=probabilities)
    
    def dp_max(self, values: List[float], lower: float, upper: float) -> float:
        """
        Maximum avec DP (utilise mécanisme exponentiel)
        
        Args:
            values: Liste de valeurs
            lower: Borne inférieure
            upper: Borne supérieure
            
        Returns:
            Maximum approximatif avec DP
        """
        if len(values) == 0:
            return 0.0
        
        clipped = np.clip(values, lower, upper)
        
        # Créer candidats
        candidates = np.linspace(lower, upper, 100)
        
        # Score: nombre de valeurs <= candidat (on veut le max)
        def score_function(candidate):
            return np.sum(clipped <= candidate)
        
        scores = np.array([score_function(c) for c in candidates])
        
        # Mécanisme exponentiel
        sensitivity = 1  # Ajouter/retirer une personne change le score de max 1
        probabilities = np.exp(scores * self.epsilon / (2 * sensitivity))
        probabilities = probabilities / probabilities.sum()
        
        return np.random.choice(candidates, p=probabilities)

# ==================== TEST ====================
if __name__ == "__main__":
    print("="*70)
    print("TEST COMPLET DU DP ENGINE")
    print("="*70)
    
    engine = DPEngine(epsilon=1.0)
    
    # Données de test
    ages = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    costs = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500]
    
    print("\n--- Test 1: DP Count ---")
    true_count = 1000
    noisy_count = engine.dp_count(true_count)
    print(f"  Vrai: {true_count}, Bruité: {noisy_count}, Erreur: {abs(true_count-noisy_count)}")
    
    print("\n--- Test 2: DP Mean ---")
    true_mean = np.mean(ages)
    noisy_mean = engine.dp_mean(ages, 0, 100)
    print(f"  Vrai: {true_mean:.1f}, Bruité: {noisy_mean:.1f}, Erreur: {abs(true_mean-noisy_mean):.1f}")
    
    print("\n--- Test 3: DP Sum ---")
    true_sum = sum(costs)
    noisy_sum = engine.dp_sum(costs, 0, 10000)
    print(f"  Vrai: {true_sum:.0f}, Bruité: {noisy_sum:.0f}, Erreur: {abs(true_sum-noisy_sum):.0f}")
    
    print("\n--- Test 4: DP Median ---")
    true_median = np.median(ages)
    noisy_median = engine.dp_median(ages, 0, 100)
    print(f"  Vrai: {true_median:.1f}, Bruité: {noisy_median:.1f}, Erreur: {abs(true_median-noisy_median):.1f}")
    
    print("\n--- Test 5: DP Histogram ---")
    bin_edges, noisy_hist = engine.dp_histogram(ages, bins=5, lower=0, upper=100)
    true_hist, _ = np.histogram(ages, bins=5, range=(0, 100))
    print(f"  Vrai histogram: {true_hist}")
    print(f"  Bruité histogram: {noisy_hist}")
    
    print("\n--- Test 6: DP Variance ---")
    true_var = np.var(ages)
    noisy_var = engine.dp_variance(ages, 0, 100)
    print(f"  Vrai: {true_var:.1f}, Bruité: {noisy_var:.1f}")
    
    print("\n--- Test 7: DP Percentile (50e = médiane) ---")
    noisy_p50 = engine.dp_percentile(ages, 50, 0, 100)
    print(f"  50e percentile: {noisy_p50:.1f}")
    
    print("\n--- Test 8: DP Max ---")
    true_max = max(ages)
    noisy_max = engine.dp_max(ages, 0, 100)
    print(f"  Vrai: {true_max}, Bruité: {noisy_max:.1f}")
    
    print("\n--- Test 9: Comparaison Epsilons ---")
    print("  Impact de epsilon sur Count (vrai=500):")
    for eps in [0.1, 0.5, 1.0, 5.0]:
        eng = DPEngine(epsilon=eps)
        noisy = eng.dp_count(500)
        err = abs(500 - noisy)
        print(f"    ε={eps:4.1f} → Résultat={noisy:4d}, Erreur={err:3d}")
    
    print("\n" + "="*70)
    print("TOUS LES TESTS TERMINÉS!")
    print(f"9 MÉCANISMES DP IMPLÉMENTÉS")
    print("="*70)