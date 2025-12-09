# GUIDE D'UTILISATION - DP ENGINE

**Auteur:** Personne 3 - DP Engine & Data Analytics  
**Date:** Novembre 2024  
**Version:** 1.0

---

## TABLE DES MATIÈRES

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Démarrage Rapide](#démarrage-rapide)
4. [Fonctions Disponibles](#fonctions-disponibles)
5. [Epsilon Manager](#epsilon-manager)
6. [Exemples Complets](#exemples-complets)
7. [Bonnes Pratiques](#bonnes-pratiques)
8. [FAQ](#faq)

---

## INTRODUCTION

Le **DP Engine** est un moteur de Differential Privacy qui permet d'analyser des données sensibles tout en protégeant la vie privée des individus.

### Concepts clés :

- **Epsilon (ε)** : Budget de confidentialité (plus petit = plus privé)
- **Sensibilité** : Impact maximal d'un individu sur le résultat
- **Bruit** : Valeur aléatoire ajoutée pour masquer les contributions individuelles

### Garantie mathématique :

Pour tout epsilon > 0, le DP Engine garantit que :
```
P(Résultat avec personne X) / P(Résultat sans personne X) ≤ e^ε
```

---

## INSTALLATION

### Prérequis :
```bash
Python >= 3.8
numpy >= 1.20.0
pandas >= 1.3.0
```

### Installation :
```python
# Copier le dossier dp_engine dans votre projet
cp -r src/dp_engine /votre/projet/
```

---

## DÉMARRAGE RAPIDE

### Import basique :
```python
from dp_engine.dp_core import DPEngine
from dp_engine.epsilon_manager import EpsilonTracker

# Créer le moteur avec epsilon=1.0
engine = DPEngine(epsilon=1.0)

# Créer le gestionnaire de budget
tracker = EpsilonTracker(total_budget=10.0)
```

### Premier exemple :
```python
# Compter avec DP
true_count = 1000
noisy_count = engine.dp_count(true_count)

print(f"Vrai: {true_count}, Avec DP: {noisy_count}")
# Output: Vrai: 1000, Avec DP: 998
```

---

## FONCTIONS DISPONIBLES

### `dp_count(count: int) -> int`

Compte le nombre d'éléments avec Differential Privacy.

**Sensibilité:** 1 (ajouter/retirer une personne change le compte de ±1)

**Paramètres:**
- `count` (int): Nombre vrai à protéger

**Retourne:**
- `int`: Compte bruité (toujours ≥ 0)

**Exemple:**
```python
engine = DPEngine(epsilon=1.0)

# Compter les patients diabétiques
diabetic_count = Patient.objects.filter(diagnosis='Diabetes').count()
noisy_count = engine.dp_count(diabetic_count)

print(f"Nombre de diabétiques (DP): {noisy_count}")
```

**Erreur typique avec ε=1.0:** ±1 à ±5

---

### `dp_mean(values: List[float], lower: float, upper: float) -> float`

Calcule la moyenne avec Differential Privacy.

**Sensibilité:** `(upper - lower) / n`

**Paramètres:**
- `values` (list): Liste des valeurs
- `lower` (float): Borne inférieure pour clipping
- `upper` (float): Borne supérieure pour clipping

**Retourne:**
- `float`: Moyenne bruitée

**Exemple:**
```python
# Moyenne des âges des patients
ages = list(Patient.objects.values_list('age', flat=True))
noisy_mean_age = engine.dp_mean(ages, lower=0, upper=120)

print(f"Âge moyen (DP): {noisy_mean_age:.1f} ans")
```

**IMPORTANT:** Toujours définir des bornes réalistes pour le clipping !

---

### `dp_sum(values: List[float], lower: float, upper: float) -> float`

Calcule la somme avec Differential Privacy.

**Sensibilité:** `upper - lower`

**Paramètres:**
- `values` (list): Liste des valeurs
- `lower` (float): Borne inférieure
- `upper` (float): Borne supérieure

**Retourne:**
- `float`: Somme bruitée

**Exemple:**
```python
# Somme totale des coûts de traitement
costs = list(Patient.objects.values_list('treatment_cost', flat=True))
noisy_total = engine.dp_sum(costs, lower=0, upper=100000)

print(f"Coût total (DP): ${noisy_total:,.2f}")
```

---

### `dp_median(values: List[float], lower: float, upper: float) -> float`

Calcule la médiane avec mécanisme exponentiel.

**Exemple:**
```python
ages = [25, 30, 35, 40, 45, 50, 55, 60]
noisy_median = engine.dp_median(ages, lower=0, upper=100)

print(f"Âge médian (DP): {noisy_median:.1f}")
```

---

### `dp_histogram(values: List[float], bins: int, lower: float, upper: float) -> tuple`

Crée un histogramme avec DP.

**Retourne:** `(bin_edges, noisy_counts)`

**Exemple:**
```python
ages = list(Patient.objects.values_list('age', flat=True))
bin_edges, noisy_hist = engine.dp_histogram(ages, bins=10, lower=0, upper=100)

print("Distribution des âges (DP):")
for i, count in enumerate(noisy_hist):
    print(f"  {bin_edges[i]:.0f}-{bin_edges[i+1]:.0f} ans: {count} patients")
```

---

### Autres fonctions disponibles :

- `dp_variance()` - Variance (consomme 2×epsilon)
- `dp_percentile()` - N-ième percentile
- `dp_max()` - Maximum

---

## EPSILON MANAGER

### Initialisation :
```python
from dp_engine.epsilon_manager import EpsilonTracker

# Budget de 10.0 epsilon par utilisateur
tracker = EpsilonTracker(total_budget=10.0)
```

### Vérifier le budget :
```python
user_id = "user_123"

if tracker.check_budget(user_id, required_epsilon=1.0):
    print("Budget suffisant")
else:
    print("Budget insuffisant")
```

### Consommer du budget :
```python
success = tracker.consume_budget(
    user_id="user_123",
    epsilon_used=1.0,
    query_type="count",
    query_params={"filter": "age>30"}
)

if success:
    print("Budget consommé avec succès")
else:
    print("Échec: budget insuffisant")
```

### Obtenir les statistiques :
```python
# Budget restant pour un utilisateur
remaining = tracker.get_remaining_budget("user_123")
print(f"Budget restant: {remaining:.2f}ε")

# Historique des requêtes
history = tracker.get_user_history("user_123")
for query in history:
    print(f"{query['timestamp']}: {query['query_type']} (ε={query['epsilon_used']})")

# Statistiques globales
stats = tracker.get_stats()
print(f"Total utilisateurs: {stats['total_users']}")
print(f"Total requêtes: {stats['total_queries']}")
```

---

## EXEMPLES COMPLETS

### Exemple 1: Intégration Django API
```python
# Dans views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from dp_engine.dp_core import DPEngine
from dp_engine.epsilon_manager import EpsilonTracker
from .models import Patient

# Initialiser le tracker (une seule fois)
tracker = EpsilonTracker(total_budget=10.0)

@api_view(['POST'])
def dp_count_query(request):
    """
    Endpoint pour count avec DP
    """
    user_id = request.user.id
    epsilon = request.data.get('epsilon', 1.0)
    filters = request.data.get('filters', {})
    
    # Vérifier budget
    if not tracker.check_budget(user_id, epsilon):
        return Response({
            "error": "Budget epsilon insuffisant",
            "remaining": tracker.get_remaining_budget(user_id)
        }, status=403)
    
    # Appliquer filtres et compter
    queryset = Patient.objects.filter(**filters)
    true_count = queryset.count()
    
    # Appliquer DP
    engine = DPEngine(epsilon=epsilon)
    noisy_count = engine.dp_count(true_count)
    
    # Consommer budget
    tracker.consume_budget(user_id, epsilon, 'count', filters)
    
    # Retourner résultat
    return Response({
        "count": noisy_count,
        "epsilon_used": epsilon,
        "remaining_budget": tracker.get_remaining_budget(user_id)
    })
```

### Exemple 2: Analyses statistiques
```python
from dp_engine.dp_core import DPEngine
from .models import Patient

def get_patient_statistics(epsilon=1.0):
    """
    Retourne des statistiques agrégées avec DP
    """
    engine = DPEngine(epsilon=epsilon)
    
    # Récupérer les données
    ages = list(Patient.objects.values_list('age', flat=True))
    costs = list(Patient.objects.values_list('treatment_cost', flat=True))
    
    # Calculer statistiques avec DP
    stats = {
        'total_patients': engine.dp_count(len(ages)),
        'mean_age': engine.dp_mean(ages, 0, 120),
        'median_age': engine.dp_median(ages, 0, 120),
        'mean_cost': engine.dp_mean(costs, 0, 100000),
        'total_cost': engine.dp_sum(costs, 0, 100000)
    }
    
    return stats
```

### Exemple 3: Workflow complet
```python
from dp_engine.dp_core import DPEngine
from dp_engine.epsilon_manager import EpsilonTracker

# 1. Initialiser
engine = DPEngine(epsilon=1.0)
tracker = EpsilonTracker(total_budget=10.0)

# 2. Faire plusieurs requêtes
user_id = "analyst_1"

# Requête 1: Count
if tracker.check_budget(user_id, 1.0):
    count = engine.dp_count(5000)
    tracker.consume_budget(user_id, 1.0, 'count')
    print(f"Count: {count}")

# Requête 2: Mean
if tracker.check_budget(user_id, 1.0):
    ages = [25, 30, 35, 40, 45, 50]
    mean_age = engine.dp_mean(ages, 0, 100)
    tracker.consume_budget(user_id, 1.0, 'mean')
    print(f"Mean age: {mean_age:.1f}")

# 3. Vérifier budget restant
remaining = tracker.get_remaining_budget(user_id)
print(f"Budget restant: {remaining:.2f}ε")
```

---

## BONNES PRATIQUES

### DO (À FAIRE)

1. **Toujours utiliser le clipping**
```python
   # BON
   mean = engine.dp_mean(values, lower=0, upper=100)
```

2. **Choisir epsilon selon le contexte**
   - ε < 0.5: Très sensible (données médicales individuelles)
   - ε = 1.0: Standard (bon compromis)
   - ε > 5.0: Peu sensible (statistiques agrégées)

3. **Utiliser Epsilon Manager**
```python
   tracker = EpsilonTracker(total_budget=10.0)
   tracker.consume_budget(user_id, epsilon, query_type)
```

4. **Logger toutes les requêtes**
```python
   tracker.export_history('audit_log.json')
```

5. **Gérer les erreurs**
```python
   try:
       result = engine.dp_mean(values, 0, 100)
   except Exception as e:
       logger.error(f"DP query failed: {e}")
```

---

### DON'T (À ÉVITER)

1. **Ne pas utiliser epsilon trop grand**
```python
   # MAUVAIS - Pas assez de confidentialité
   engine = DPEngine(epsilon=100.0)
```

2. **Ne pas oublier les bornes**
```python
   # MAUVAIS - Pas de bornes définies
   mean = engine.dp_mean(values, 0, float('inf'))
```

3. **Ne pas réutiliser les résultats DP**
```python
   # MAUVAIS - Utiliser un résultat DP dans un autre calcul DP
   noisy_mean = engine.dp_mean(values, 0, 100)
   noisy_sum = engine.dp_sum([noisy_mean] * 10, 0, 100)
```

4. **Ne pas ignorer le budget**
```python
   # MAUVAIS - Pas de vérification de budget
   for i in range(1000):
       result = engine.dp_count(data)  # Consume trop d'epsilon!
```

---

## FAQ

### Q1: Quel epsilon choisir ?

**R:** Dépend du niveau de sensibilité :
- **ε = 0.1**: Données très sensibles (SSN, salaires individuels)
- **ε = 1.0**: Standard, bon compromis (recommandé)
- **ε = 10.0**: Données peu sensibles (statistiques publiques)

---

### Q2: Pourquoi mes résultats changent à chaque fois ?

**R:** C'est normal ! Le bruit est **aléatoire**. Si vous lancez la même requête 100 fois, la **moyenne** des résultats sera proche de la vraie valeur.
```python
# Normal: résultats différents
print(engine.dp_count(1000))  # 998
print(engine.dp_count(1000))  # 1003
print(engine.dp_count(1000))  # 997

# Mais la moyenne converge
results = [engine.dp_count(1000) for _ in range(100)]
print(np.mean(results))  # ~1000
```

---

### Q3: Comment choisir les bornes pour le clipping ?

**R:** Utiliser les **percentiles 1% et 99%** des données réelles :
```python
import numpy as np

ages = [...]  # Vos données
lower = np.percentile(ages, 1)   # 1er percentile
upper = np.percentile(ages, 99)  # 99e percentile

noisy_mean = engine.dp_mean(ages, lower, upper)
```

---

### Q4: Le DP Engine fonctionne avec n'importe quelle base de données ?

**R:** Oui ! Le DP Engine est **indépendant** de la base de données. Il prend des listes Python en entrée.
```python
# PostgreSQL
ages = list(Patient.objects.values_list('age', flat=True))

# MySQL
cursor.execute("SELECT age FROM patients")
ages = [row[0] for row in cursor.fetchall()]

# MongoDB
ages = [doc['age'] for doc in collection.find()]

# Tous fonctionnent avec:
noisy_mean = engine.dp_mean(ages, 0, 120)
```

---

### Q5: Comment tester si mon implémentation est correcte ?

**R:** Utilisez les tests unitaires fournis :
```bash
cd tests
python test_dp_engine.py
```

Tous les tests doivent passer

---

## SUPPORT

**Questions ?** Contactez Personne 3 (DP Engine Team)

**Bugs ?** Vérifiez d'abord les tests unitaires

**Documentation complète :** Voir `analysis_report.txt` dans `analyses/results/`

---

**Fin du guide - Bonne utilisation du DP Engine !**