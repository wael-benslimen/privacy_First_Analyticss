
import numpy as np
from typing import List, Dict, Any, Tuple
from django.db.models import QuerySet, Count, Avg, Sum
from decimal import Decimal


class DifferentialPrivacyService:
    """Service pour appliquer differential privacy aux requêtes"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
    
    def _calculate_sensitivity(self, query_type: str, bounds: Tuple[float, float]) -> float:
        """Calculer la sensibilité basée sur le type de requête"""
        lower, upper = bounds
        
        sensitivities = {
            'count': 1.0,
            'sum': upper - lower,
            'mean': (upper - lower),
            'median': (upper - lower) / 2,
        }
        
        return sensitivities.get(query_type, 1.0)
    
    def add_laplace_noise(self, true_value: float, sensitivity: float) -> float:
        """Ajouter du bruit Laplacien"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return true_value + noise
    
    def add_gaussian_noise(self, true_value: float, sensitivity: float) -> float:
        """Ajouter du bruit Gaussien (pour (epsilon, delta)-DP)"""
        sigma = (sensitivity * np.sqrt(2 * np.log(1.25 / self.delta))) / self.epsilon
        noise = np.random.normal(0, sigma)
        return true_value + noise
    
    def noisy_count(self, count: int) -> Dict[str, Any]:
        """Count avec DP"""
        sensitivity = 1.0
        noisy_value = self.add_laplace_noise(float(count), sensitivity)
        
        # Arrondir et assurer >= 0
        noisy_value = max(0, round(noisy_value))
        
        return {
            'noisy_result': noisy_value,
            'true_result': count,
            'noise_added': noisy_value - count,
            'epsilon_used': self.epsilon,
            'mechanism': 'Laplace',
            'sensitivity': sensitivity
        }
    
    def noisy_sum(self, total: float, bounds: Tuple[float, float], count: int) -> Dict[str, Any]:
        """Sum avec DP"""
        lower, upper = bounds
        sensitivity = (upper - lower) * count
        
        noisy_value = self.add_laplace_noise(total, sensitivity)
        
        return {
            'noisy_result': round(noisy_value, 2),
            'true_result': float(total),
            'noise_added': round(noisy_value - total, 2),
            'epsilon_used': self.epsilon,
            'mechanism': 'Laplace',
            'sensitivity': sensitivity,
            'bounds': bounds
        }
    
    def noisy_mean(self, mean: float, bounds: Tuple[float, float], count: int) -> Dict[str, Any]:
        """Mean avec DP"""
        lower, upper = bounds
        
        # Pour la moyenne, on utilise la composition de count et sum
        epsilon_count = self.epsilon / 2
        epsilon_sum = self.epsilon / 2
        
        # Ajouter du bruit au count
        noisy_count_value = max(1, self.add_laplace_noise(float(count), 1.0 / epsilon_count))
        
        # Ajouter du bruit à la somme
        true_sum = mean * count
        sensitivity_sum = (upper - lower) * count
        noisy_sum_value = self.add_laplace_noise(true_sum, sensitivity_sum / epsilon_sum)
        
        # Calculer moyenne bruitée
        noisy_mean = noisy_sum_value / noisy_count_value
        
        # Clamper dans les bounds
        noisy_mean = max(lower, min(upper, noisy_mean))
        
        return {
            'noisy_result': round(noisy_mean, 2),
            'true_result': float(mean),
            'noise_added': round(noisy_mean - mean, 2),
            'epsilon_used': self.epsilon,
            'mechanism': 'Laplace (Composition)',
            'bounds': bounds,
            'count': count
        }
    
    def noisy_median(self, values: List[float], bounds: Tuple[float, float]) -> Dict[str, Any]:
        """Median avec DP (approximation)"""
        if not values:
            return {
                'noisy_result': 0,
                'true_result': 0,
                'epsilon_used': self.epsilon,
                'error': 'No values provided'
            }
        
        true_median = float(np.median(values))
        lower, upper = bounds
        sensitivity = (upper - lower) / 2
        
        noisy_value = self.add_laplace_noise(true_median, sensitivity)
        noisy_value = max(lower, min(upper, noisy_value))
        
        return {
            'noisy_result': round(noisy_value, 2),
            'true_result': round(true_median, 2),
            'noise_added': round(noisy_value - true_median, 2),
            'epsilon_used': self.epsilon,
            'mechanism': 'Laplace',
            'sensitivity': sensitivity,
            'bounds': bounds
        }
    
    def noisy_histogram(self, bins: List[int], num_bins: int) -> Dict[str, Any]:
        """Histogram avec DP"""
        sensitivity = 1.0  # Une personne peut affecter au plus 1 bin
        
        noisy_bins = []
        for count in bins:
            noisy_count = self.add_laplace_noise(float(count), sensitivity)
            noisy_bins.append(max(0, round(noisy_count)))
        
        return {
            'noisy_bins': noisy_bins,
            'true_bins': bins,
            'epsilon_used': self.epsilon,
            'mechanism': 'Laplace',
            'sensitivity': sensitivity,
            'num_bins': num_bins
        }


class PolicyEnforcer:
    """Enforcer pour les politiques de privacy"""
    
    def __init__(self, user, epsilon_budget):
        self.user = user
        self.epsilon_budget = epsilon_budget
    
    def can_execute_query(self, epsilon_required: float) -> Tuple[bool, str]:
        """Vérifier si la requête peut être exécutée"""
        
        # Vérifier si user est actif
        if not self.user.is_active:
            return False, "User account is inactive"
        
        # Vérifier budget epsilon
        if not self.epsilon_budget.can_consume(epsilon_required):
            remaining = self.epsilon_budget.remaining_budget
            return False, f"Insufficient epsilon budget. Required: {epsilon_required}, Remaining: {remaining}"
        
        # Vérifier warning threshold
        if self.epsilon_budget.is_warning:
            # Log warning mais autoriser
            pass
        
        return True, "Query authorized"
    
    def consume_budget(self, epsilon_used: float) -> bool:
        """Consommer le budget epsilon"""
        return self.epsilon_budget.consume(epsilon_used)
    
    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut du budget"""
        return {
            'user': self.user.username,
            'role': self.user.role,
            'total_budget': self.epsilon_budget.total_budget,
            'consumed_budget': self.epsilon_budget.consumed_budget,
            'remaining_budget': self.epsilon_budget.remaining_budget,
            'is_warning': self.epsilon_budget.is_warning,
            'is_depleted': self.epsilon_budget.is_depleted,
            'last_reset': self.epsilon_budget.last_reset,
            'reset_count': self.epsilon_budget.reset_count
        }