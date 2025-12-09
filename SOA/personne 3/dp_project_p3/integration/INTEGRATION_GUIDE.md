# Guide d'intégration - Pour Personne 2

Ce guide explique comment intégrer le DP Engine dans le backend Django.

---

## Étape 1: Copier le DP Engine

Copiez le dossier `dp_engine` dans votre projet Django:
```
backend/
├── privacy_analytics/
├── analytics_api/
├── dp_engine/              ← Copier ici
│   ├── __init__.py
│   ├── dp_core.py
│   └── epsilon_manager.py
└── manage.py
```

---

## Étape 2: Créer le modèle Patient

Dans `analytics_api/models.py`:
```python
from django.db import models

class Patient(models.Model):
    patient_id = models.CharField(max_length=10, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    diagnosis = models.CharField(max_length=100)
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    hospital_stay_days = models.IntegerField()
    zipcode = models.CharField(max_length=10)
    admission_date = models.DateField()
    bmi = models.DecimalField(max_digits=4, decimal_places=1)
    insurance_type = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['patient_id']
    
    def __str__(self):
        return f"{self.patient_id} - {self.diagnosis}"
```

Exécuter:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Étape 3: Charger les données

Utiliser le script fourni:
```bash
cd integration
python load_data_to_django.py
# Choisir option 4 (tout faire)
```

---

## Étape 4: Créer les endpoints API

Dans `analytics_api/views.py`:
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from dp_engine.dp_core import DPEngine
from dp_engine.epsilon_manager import EpsilonTracker
from .models import Patient
from django.db.models import Q

# Initialiser le tracker (variable globale)
epsilon_tracker = EpsilonTracker(total_budget=10.0)


@api_view(['POST'])
def dp_count_query(request):
    """
    Endpoint: POST /api/query/count
    
    Body:
    {
        "epsilon": 1.0,
        "filters": {
            "age__gt": 30,
            "diagnosis": "Diabetes"
        }
    }
    """
    user_id = str(request.user.id)
    epsilon = float(request.data.get('epsilon', 1.0))
    filters = request.data.get('filters', {})
    
    # Vérifier le budget
    if not epsilon_tracker.check_budget(user_id, epsilon):
        return Response({
            'error': 'Budget epsilon insuffisant',
            'remaining': epsilon_tracker.get_remaining_budget(user_id)
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Appliquer les filtres
    queryset = Patient.objects.filter(**filters)
    true_count = queryset.count()
    
    # Appliquer DP
    engine = DPEngine(epsilon=epsilon)
    noisy_count = engine.dp_count(true_count)
    
    # Consommer le budget
    epsilon_tracker.consume_budget(user_id, epsilon, 'count', filters)
    
    return Response({
        'count': noisy_count,
        'epsilon_used': epsilon,
        'remaining_budget': epsilon_tracker.get_remaining_budget(user_id)
    })


@api_view(['POST'])
def dp_mean_query(request):
    """
    Endpoint: POST /api/query/mean
    
    Body:
    {
        "epsilon": 1.0,
        "column": "age",
        "filters": {},
        "lower_bound": 0,
        "upper_bound": 120
    }
    """
    user_id = str(request.user.id)
    epsilon = float(request.data.get('epsilon', 1.0))
    column = request.data.get('column')
    filters = request.data.get('filters', {})
    lower = float(request.data.get('lower_bound', 0))
    upper = float(request.data.get('upper_bound', 100))
    
    if not column:
        return Response({'error': 'column is required'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Vérifier le budget
    if not epsilon_tracker.check_budget(user_id, epsilon):
        return Response({
            'error': 'Budget epsilon insuffisant',
            'remaining': epsilon_tracker.get_remaining_budget(user_id)
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les valeurs
    queryset = Patient.objects.filter(**filters)
    values = list(queryset.values_list(column, flat=True))
    
    if not values:
        return Response({'error': 'No data matching filters'}, 
                       status=status.HTTP_404_NOT_FOUND)
    
    # Appliquer DP
    engine = DPEngine(epsilon=epsilon)
    noisy_mean = engine.dp_mean(values, lower, upper)
    
    # Consommer le budget
    epsilon_tracker.consume_budget(user_id, epsilon, 'mean', {
        'column': column,
        'filters': filters
    })
    
    return Response({
        'mean': round(noisy_mean, 2),
        'column': column,
        'epsilon_used': epsilon,
        'remaining_budget': epsilon_tracker.get_remaining_budget(user_id)
    })


@api_view(['GET'])
def epsilon_status(request):
    """
    Endpoint: GET /api/epsilon/status
    
    Retourne le budget epsilon restant pour l'utilisateur
    """
    user_id = str(request.user.id)
    
    return Response({
        'user_id': user_id,
        'total_budget': epsilon_tracker.total_budget,
        'used': epsilon_tracker.get_used_budget(user_id),
        'remaining': epsilon_tracker.get_remaining_budget(user_id),
        'percentage_used': (epsilon_tracker.get_used_budget(user_id) / 
                           epsilon_tracker.total_budget) * 100
    })


@api_view(['POST'])
def epsilon_reset(request):
    """
    Endpoint: POST /api/epsilon/reset
    
    Réinitialise le budget epsilon (admin seulement)
    """
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    
    if user_id:
        epsilon_tracker.reset_budget(user_id)
        message = f'Budget reset for user {user_id}'
    else:
        epsilon_tracker.reset_budget()
        message = 'All budgets reset'
    
    return Response({'message': message})


@api_view(['GET'])
def query_history(request):
    """
    Endpoint: GET /api/logs/history
    
    Retourne l'historique des requêtes de l'utilisateur
    """
    user_id = str(request.user.id)
    history = epsilon_tracker.get_user_history(user_id)
    
    return Response({
        'user_id': user_id,
        'total_queries': len(history),
        'history': history
    })
```

---

## Étape 5: Configurer les URLs

Dans `analytics_api/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('query/count', views.dp_count_query, name='dp_count'),
    path('query/mean', views.dp_mean_query, name='dp_mean'),
    path('epsilon/status', views.epsilon_status, name='epsilon_status'),
    path('epsilon/reset', views.epsilon_reset, name='epsilon_reset'),
    path('logs/history', views.query_history, name='query_history'),
]
```

Dans `privacy_analytics/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('analytics_api.urls')),
]
```

---

## Étape 6: Tester l'API

Démarrer le serveur:
```bash
python manage.py runserver
```

Tester avec curl ou Postman:
```bash
# Test Count
curl -X POST http://localhost:8000/api/query/count \
  -H "Content-Type: application/json" \
  -d '{"epsilon": 1.0, "filters": {"age__gt": 30}}'

# Test Mean
curl -X POST http://localhost:8000/api/query/mean \
  -H "Content-Type: application/json" \
  -d '{"epsilon": 1.0, "column": "age", "lower_bound": 0, "upper_bound": 120}'

# Vérifier budget
curl http://localhost:8000/api/epsilon/status
```

---

## Tests unitaires pour Django

Dans `analytics_api/tests.py`:
```python
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Patient
from dp_engine.dp_core import DPEngine

class DPEngineIntegrationTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        
        # Créer des patients de test
        for i in range(100):
            Patient.objects.create(
                patient_id=f"P{i:05d}",
                age=30 + i % 50,
                gender="Male" if i % 2 == 0 else "Female",
                diagnosis="Diabetes",
                treatment_cost=5000.0,
                hospital_stay_days=3,
                zipcode="12345",
                admission_date="2024-01-01",
                bmi=25.0,
                insurance_type="Public"
            )
    
    def test_dp_count_endpoint(self):
        response = self.client.post('/api/query/count', {
            'epsilon': 1.0,
            'filters': {'diagnosis': 'Diabetes'}
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('count', response.data)
        self.assertIn('epsilon_used', response.data)
    
    def test_dp_mean_endpoint(self):
        response = self.client.post('/api/query/mean', {
            'epsilon': 1.0,
            'column': 'age',
            'lower_bound': 0,
            'upper_bound': 120
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('mean', response.data)
    
    def test_epsilon_budget_enforcement(self):
        # Consommer tout le budget
        for i in range(11):
            response = self.client.post('/api/query/count', {
                'epsilon': 1.0,
                'filters': {}
            }, format='json')
            
            if i < 10:
                self.assertEqual(response.status_code, 200)
            else:
                # La 11ème requête doit échouer
                self.assertEqual(response.status_code, 403)
```

Exécuter les tests:
```bash
python manage.py test analytics_api
```

---

## Checklist d'intégration

- [ ] DP Engine copié dans le projet Django
- [ ] Modèle Patient créé et migré
- [ ] Données chargées (5000 patients)
- [ ] Endpoints API créés
- [ ] URLs configurées
- [ ] Tests unitaires passent
- [ ] Serveur démarre sans erreur
- [ ] Tests manuels avec Postman réussis

---

## Support

En cas de problème, vérifier:

1. Le DP Engine est bien importable: `from dp_engine.dp_core import DPEngine`
2. La base de données contient des patients: `Patient.objects.count()`
3. Les migrations sont à jour: `python manage.py showmigrations`
4. Les logs Django pour les erreurs: `tail -f logs/django.log`

---

Fin du guide d'intégration