"""
Gestionnaire du budget Epsilon
Personne 3 - Epsilon Manager
"""
from typing import Dict, List, Optional
from datetime import datetime
import json

class EpsilonTracker:
    """
    Gestionnaire du budget de confidentialité (epsilon)
    
    Suit combien d'epsilon chaque utilisateur a consommé
    Implémente la composition séquentielle: les epsilons s'additionnent
    """
    
    def __init__(self, total_budget: float = 10.0):
        """
        Args:
            total_budget: Budget epsilon total par utilisateur (défaut: 10.0)
        """
        self.total_budget = total_budget
        self.user_budgets: Dict[str, float] = {}  # user_id -> epsilon utilisé
        self.query_history: List[dict] = []       # Historique complet
        print(f"Epsilon Tracker initialisé (budget par utilisateur: {total_budget})")
    
    def check_budget(self, user_id: str, required_epsilon: float) -> bool:
        """
        Vérifie si un utilisateur a assez de budget
        
        Args:
            user_id: Identifiant de l'utilisateur
            required_epsilon: Epsilon requis pour la requête
            
        Returns:
            True si le budget est suffisant, False sinon
        """
        used = self.user_budgets.get(user_id, 0.0)
        remaining = self.total_budget - used
        
        return remaining >= required_epsilon
    
    def consume_budget(self, user_id: str, epsilon_used: float, 
                        query_type: str, query_params: dict = None) -> bool:
        """
        Consomme du budget epsilon pour une requête
        
        Args:
            user_id: Identifiant utilisateur
            epsilon_used: Montant d'epsilon à consommer
            query_type: Type de requête (count, mean, sum, etc.)
            query_params: Paramètres de la requête (filtres, colonnes, etc.)
            
        Returns:
            True si la consommation a réussi, False si budget insuffisant
        """
        # Vérifier le budget disponible
        if not self.check_budget(user_id, epsilon_used):
            remaining = self.get_remaining_budget(user_id)
            print(f"Budget insuffisant pour {user_id}")
            print(f"Requis: {epsilon_used:.2f}ε, Disponible: {remaining:.2f}ε")
            return False
        
        # Mettre à jour le budget utilisé
        current_used = self.user_budgets.get(user_id, 0.0)
        self.user_budgets[user_id] = current_used + epsilon_used
        
        # Enregistrer dans l'historique
        query_record = {
            'user_id': user_id,
            'epsilon_used': epsilon_used,
            'query_type': query_type,
            'query_params': query_params or {},
            'timestamp': datetime.now().isoformat(),
            'remaining_budget': self.get_remaining_budget(user_id)
        }
        self.query_history.append(query_record)
        
        # Message de confirmation
        remaining = self.get_remaining_budget(user_id)
        print(f"{user_id}: Consommé {epsilon_used:.2f}ε (reste: {remaining:.2f}ε)")
        
        return True
    
    def get_remaining_budget(self, user_id: str) -> float:
        """
        Retourne le budget epsilon restant pour un utilisateur
        
        Args:
            user_id: Identifiant utilisateur
            
        Returns:
            Budget restant (float)
        """
        used = self.user_budgets.get(user_id, 0.0)
        return self.total_budget - used
    
    def get_used_budget(self, user_id: str) -> float:
        """Retourne le budget epsilon déjà utilisé"""
        return self.user_budgets.get(user_id, 0.0)
    
    def reset_budget(self, user_id: Optional[str] = None):
        """
        Réinitialise le budget
        
        Args:
            user_id: Si fourni, reset seulement cet utilisateur
                    Sinon, reset tous les utilisateurs
        """
        if user_id:
            self.user_budgets[user_id] = 0.0
            print(f"Budget réinitialisé pour {user_id}")
        else:
            self.user_budgets = {}
            self.query_history = []
            print("Tous les budgets réinitialisés")
    
    def get_stats(self) -> dict:
        """
        Retourne des statistiques d'utilisation globales
        
        Returns:
            Dictionnaire avec statistiques
        """
        total_consumed = sum(self.user_budgets.values())
        avg_per_user = total_consumed / len(self.user_budgets) if self.user_budgets else 0
        
        return {
            'total_users': len(self.user_budgets),
            'total_queries': len(self.query_history),
            'user_budgets': self.user_budgets.copy(),
            'total_epsilon_consumed': total_consumed,
            'average_epsilon_per_user': avg_per_user
        }
    
    def get_user_history(self, user_id: str) -> List[dict]:
        """
        Retourne l'historique des requêtes d'un utilisateur
        
        Args:
            user_id: Identifiant utilisateur
            
        Returns:
            Liste des requêtes de cet utilisateur
        """
        return [q for q in self.query_history if q['user_id'] == user_id]
    
    def export_history(self, filepath: str):
        """
        Exporte l'historique complet en JSON
        
        Args:
            filepath: Chemin du fichier de sortie
        """
        with open(filepath, 'w') as f:
            json.dump(self.query_history, f, indent=2)
        
        print(f"Historique exporté vers {filepath}")
    
    def display_summary(self):
        """Affiche un résumé de l'utilisation"""
        print("\n" + "="*60)
        print("RÉSUMÉ DES BUDGETS EPSILON")
        print("="*60)
        
        stats = self.get_stats()
        print(f"Nombre d'utilisateurs    : {stats['total_users']}")
        print(f"Nombre de requêtes       : {stats['total_queries']}")
        print(f"Epsilon total consommé   : {stats['total_epsilon_consumed']:.2f}")
        print(f"Moyenne par utilisateur  : {stats['average_epsilon_per_user']:.2f}")
        
        print("\nDétail par utilisateur:")
        for user_id, used in self.user_budgets.items():
            remaining = self.total_budget - used
            percentage = (used / self.total_budget) * 100
            print(f"  {user_id}: {used:.2f}/{self.total_budget:.2f}ε ({percentage:.1f}%) - Reste: {remaining:.2f}ε")
        
        print("="*60)


# ==================== TEST ====================
if __name__ == "__main__":
    print("="*60)
    print("TEST DE L'EPSILON TRACKER")
    print("="*60)
    
    # Créer tracker avec budget de 5.0
    tracker = EpsilonTracker(total_budget=5.0)
    
    print("\n--- Test 1: Consommation simple ---")
    print(f"Budget initial user1: {tracker.get_remaining_budget('user1'):.2f}ε\n")
    
    # Requête 1
    tracker.consume_budget('user1', 1.0, 'count', {'filter': 'age>30'})
    
    # Requête 2
    tracker.consume_budget('user1', 2.0, 'mean', {'column': 'treatment_cost'})
    
    # Requête 3 (devrait fonctionner - reste 2.0)
    tracker.consume_budget('user1', 1.5, 'sum', {'column': 'hospital_stay_days'})
    
    # Requête 4 (devrait ÉCHOUER - reste seulement 0.5)
    print("\nTentative de consommer plus que disponible:")
    tracker.consume_budget('user1', 1.0, 'count', {'filter': 'diagnosis=Cancer'})
    
    print("\n--- Test 2: Plusieurs utilisateurs ---")
    tracker.consume_budget('user2', 2.0, 'mean', {'column': 'age'})
    tracker.consume_budget('user3', 1.5, 'count', {})
    tracker.consume_budget('user2', 1.0, 'sum', {'column': 'bmi'})
    
    print("\n--- Test 3: Historique utilisateur ---")
    history = tracker.get_user_history('user1')
    print(f"Historique de user1 ({len(history)} requêtes):")
    for i, query in enumerate(history, 1):
        print(f"  {i}. {query['query_type']} - {query['epsilon_used']}ε")
    
    print("\n--- Test 4: Affichage du résumé ---")
    tracker.display_summary()
    
    print("\n--- Test 5: Reset d'un utilisateur ---")
    tracker.reset_budget('user1')
    print(f"Budget user1 après reset: {tracker.get_remaining_budget('user1'):.2f}ε")
    
    print("\n" + "="*60)
    print("TOUS LES TESTS TERMINÉS!")
    print("="*60)